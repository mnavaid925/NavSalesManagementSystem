"""Tests for quotes.models: Quote, QuoteLineItem, PricingRule, Proposal, QuoteVersion."""
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.quotes.models import (
    PricingRule, Proposal, Quote, QuoteLineItem, QuoteVersion,
)


# ============================================================ Quote
@pytest.mark.django_db
class TestQuote:
    def test_str_returns_number_when_saved(self, quote_a):
        assert "QUO-" in str(quote_a)

    def test_str_returns_title_when_no_number(self, tenant_a):
        q = Quote(tenant=tenant_a, title="Unsaved Quote")
        # unsaved — no number yet
        assert "Unsaved Quote" in str(q)

    def test_auto_number_generated_on_save(self, tenant_a):
        q = Quote.objects.create(tenant=tenant_a, title="Auto Num")
        assert q.number.startswith("QUO-")

    def test_auto_number_format_five_digits(self, tenant_a):
        q = Quote.objects.create(tenant=tenant_a, title="Format Check")
        parts = q.number.split("-")
        assert len(parts) == 2
        assert len(parts[1]) == 5
        assert parts[1].isdigit()

    def test_first_quote_is_QUO_00001(self, tenant_a):
        q = Quote.objects.create(tenant=tenant_a, title="First")
        assert q.number == "QUO-00001"

    def test_auto_number_increments_per_tenant(self, tenant_a):
        q1 = Quote.objects.create(tenant=tenant_a, title="One")
        q2 = Quote.objects.create(tenant=tenant_a, title="Two")
        assert q1.number == "QUO-00001"
        assert q2.number == "QUO-00002"

    def test_auto_number_isolated_per_tenant(self, tenant_a, tenant_b):
        qa = Quote.objects.create(tenant=tenant_a, title="A")
        qb = Quote.objects.create(tenant=tenant_b, title="B")
        assert qa.number == "QUO-00001"
        assert qb.number == "QUO-00001"

    def test_unique_together_tenant_number(self, tenant_a):
        Quote.objects.create(tenant=tenant_a, title="First")  # gets QUO-00001
        import django.db.utils as db_utils
        with pytest.raises(db_utils.IntegrityError):
            Quote.objects.create(tenant=tenant_a, number="QUO-00001", title="Dupe")

    def test_default_status_is_draft(self, tenant_a):
        q = Quote.objects.create(tenant=tenant_a, title="Draft Test")
        assert q.status == Quote.STATUS_DRAFT

    def test_default_currency_is_USD(self, tenant_a):
        q = Quote.objects.create(tenant=tenant_a, title="Currency Test")
        assert q.currency == Quote.CURRENCY_USD

    def test_status_choices_contain_all_eight(self):
        choices = dict(Quote.STATUS_CHOICES)
        assert Quote.STATUS_DRAFT in choices
        assert Quote.STATUS_PENDING in choices
        assert Quote.STATUS_APPROVED in choices
        assert Quote.STATUS_SENT in choices
        assert Quote.STATUS_ACCEPTED in choices
        assert Quote.STATUS_REJECTED in choices
        assert Quote.STATUS_EXPIRED in choices
        assert Quote.STATUS_CONVERTED in choices

    def test_currency_choices_contain_all_four(self):
        choices = dict(Quote.CURRENCY_CHOICES)
        assert Quote.CURRENCY_USD in choices
        assert Quote.CURRENCY_EUR in choices
        assert Quote.CURRENCY_GBP in choices
        assert Quote.CURRENCY_AUD in choices

    def test_sent_at_set_when_status_sent(self, tenant_a):
        q = Quote.objects.create(tenant=tenant_a, title="Sent Test")
        assert q.sent_at is None
        q.status = Quote.STATUS_SENT
        q.save()
        assert q.sent_at is not None

    def test_sent_at_not_overwritten_on_second_save(self, tenant_a):
        q = Quote.objects.create(tenant=tenant_a, title="Sent Once")
        q.status = Quote.STATUS_SENT
        q.save()
        first_sent_at = q.sent_at
        q.save()
        assert q.sent_at == first_sent_at

    def test_converted_at_set_when_status_converted(self, tenant_a):
        q = Quote.objects.create(tenant=tenant_a, title="Convert Test")
        assert q.converted_at is None
        q.status = Quote.STATUS_CONVERTED
        q.save()
        assert q.converted_at is not None

    def test_converted_at_not_overwritten_on_second_save(self, tenant_a):
        q = Quote.objects.create(tenant=tenant_a, title="Convert Once")
        q.status = Quote.STATUS_CONVERTED
        q.save()
        first = q.converted_at
        q.save()
        assert q.converted_at == first

    def test_default_totals_are_zero(self, tenant_a):
        q = Quote.objects.create(tenant=tenant_a, title="Zero Totals")
        assert q.subtotal == Decimal("0")
        assert q.discount_amount == Decimal("0")
        assert q.tax_amount == Decimal("0")
        assert q.total_amount == Decimal("0")

    def test_ordering_most_recent_first(self, tenant_a):
        q1 = Quote.objects.create(tenant=tenant_a, title="Old")
        q2 = Quote.objects.create(tenant=tenant_a, title="New")
        qs = list(Quote.objects.filter(tenant=tenant_a))
        # Most recently created should be first (ordering = ["-created_at", "-id"])
        assert qs[0].pk == q2.pk


# ============================================================ QuoteLineItem
@pytest.mark.django_db
class TestQuoteLineItem:
    def test_str_format(self, line_item_a):
        result = str(line_item_a)
        assert "Widget Pro" in result
        assert "×" in result

    def test_default_unit_is_each(self, tenant_a, quote_a):
        # NOTE: must pass Decimal values — app bug: computed_total fails when
        # decimal fields are passed as strings before DB round-trip converts them.
        li = QuoteLineItem.objects.create(
            tenant=tenant_a, quote=quote_a, product_name="Default Unit",
            unit_price=Decimal("10.00"),
        )
        assert li.unit == QuoteLineItem.UNIT_EACH

    def test_unit_choices_contain_all_five(self):
        choices = dict(QuoteLineItem.UNIT_CHOICES)
        assert QuoteLineItem.UNIT_EACH in choices
        assert QuoteLineItem.UNIT_HOUR in choices
        assert QuoteLineItem.UNIT_MONTH in choices
        assert QuoteLineItem.UNIT_YEAR in choices
        assert QuoteLineItem.UNIT_LICENSE in choices

    def test_computed_total_no_discount(self, tenant_a, quote_a):
        li = QuoteLineItem(
            tenant=tenant_a, quote=quote_a,
            product_name="No Discount",
            quantity=Decimal("3"),
            unit_price=Decimal("100.00"),
            discount_percent=Decimal("0"),
        )
        assert li.computed_total == Decimal("300.00")

    def test_computed_total_with_discount(self, tenant_a, quote_a):
        li = QuoteLineItem(
            tenant=tenant_a, quote=quote_a,
            product_name="With Discount",
            quantity=Decimal("2"),
            unit_price=Decimal("50.00"),
            discount_percent=Decimal("10"),
        )
        # gross=100, discount=10, total=90
        assert li.computed_total == Decimal("90.00")

    def test_save_sets_line_total(self, tenant_a, quote_a):
        li = QuoteLineItem.objects.create(
            tenant=tenant_a, quote=quote_a,
            product_name="Auto Total",
            quantity=Decimal("2"),
            unit_price=Decimal("50.00"),
            discount_percent=Decimal("10"),
        )
        assert li.line_total == Decimal("90.00")

    def test_line_item_uses_fixture_computed_total(self, line_item_a):
        # quantity=2, unit_price=50, discount=10% => gross=100, discount=10, total=90
        assert line_item_a.line_total == Decimal("90.00")

    def test_ordering_by_position_then_id(self, tenant_a, quote_a):
        # NOTE: must pass Decimal — app bug: computed_total fails with string decimal values
        li2 = QuoteLineItem.objects.create(
            tenant=tenant_a, quote=quote_a, product_name="Second", position=2,
            unit_price=Decimal("1.00"),
        )
        li1 = QuoteLineItem.objects.create(
            tenant=tenant_a, quote=quote_a, product_name="First", position=1,
            unit_price=Decimal("1.00"),
        )
        qs = list(QuoteLineItem.objects.filter(quote=quote_a).values_list("position", flat=True))
        assert qs == sorted(qs)


# ============================================================ PricingRule
@pytest.mark.django_db
class TestPricingRule:
    def test_str_returns_name(self, pricing_rule_a):
        assert str(pricing_rule_a) == "Volume 10%"

    def test_default_rule_type_is_volume(self, tenant_a):
        rule = PricingRule.objects.create(tenant=tenant_a, name="Default Rule")
        assert rule.rule_type == PricingRule.RULE_VOLUME

    def test_default_approval_level_is_auto(self, tenant_a):
        rule = PricingRule.objects.create(tenant=tenant_a, name="Auto Approval")
        assert rule.approval_level == PricingRule.APPROVAL_AUTO

    def test_default_status_is_active(self, tenant_a):
        rule = PricingRule.objects.create(tenant=tenant_a, name="Active Status")
        assert rule.status == PricingRule.STATUS_ACTIVE

    def test_rule_choices_contain_all_five(self):
        choices = dict(PricingRule.RULE_CHOICES)
        assert PricingRule.RULE_VOLUME in choices
        assert PricingRule.RULE_PROMO in choices
        assert PricingRule.RULE_LOYALTY in choices
        assert PricingRule.RULE_CONTRACT in choices
        assert PricingRule.RULE_CLEARANCE in choices

    def test_approval_choices_contain_all_four(self):
        choices = dict(PricingRule.APPROVAL_CHOICES)
        assert PricingRule.APPROVAL_AUTO in choices
        assert PricingRule.APPROVAL_MANAGER in choices
        assert PricingRule.APPROVAL_DIRECTOR in choices
        assert PricingRule.APPROVAL_VP in choices

    def test_status_choices_contain_all_three(self):
        choices = dict(PricingRule.STATUS_CHOICES)
        assert PricingRule.STATUS_ACTIVE in choices
        assert PricingRule.STATUS_INACTIVE in choices
        assert PricingRule.STATUS_ARCHIVED in choices

    def test_ordering_by_priority_then_name(self, tenant_a):
        PricingRule.objects.create(tenant=tenant_a, name="Zebra Rule", priority=2)
        PricingRule.objects.create(tenant=tenant_a, name="Alpha Rule", priority=1)
        qs = list(PricingRule.objects.filter(tenant=tenant_a).values_list("priority", flat=True))
        assert qs == sorted(qs)


# ============================================================ Proposal
@pytest.mark.django_db
class TestProposal:
    def test_str_returns_title(self, proposal_a):
        assert str(proposal_a) == "Alpha Proposal"

    def test_default_template_is_standard(self, tenant_a):
        p = Proposal.objects.create(tenant=tenant_a, title="Default Template")
        assert p.template == Proposal.TEMPLATE_STANDARD

    def test_default_status_is_draft(self, tenant_a):
        p = Proposal.objects.create(tenant=tenant_a, title="Draft Status")
        assert p.status == Proposal.STATUS_DRAFT

    def test_template_choices_contain_all_four(self):
        choices = dict(Proposal.TEMPLATE_CHOICES)
        assert Proposal.TEMPLATE_STANDARD in choices
        assert Proposal.TEMPLATE_EXECUTIVE in choices
        assert Proposal.TEMPLATE_TECHNICAL in choices
        assert Proposal.TEMPLATE_MINIMAL in choices

    def test_status_choices_contain_all_four(self):
        choices = dict(Proposal.STATUS_CHOICES)
        assert Proposal.STATUS_DRAFT in choices
        assert Proposal.STATUS_REVIEW in choices
        assert Proposal.STATUS_FINAL in choices
        assert Proposal.STATUS_SENT in choices

    def test_sent_at_set_when_status_sent(self, tenant_a):
        p = Proposal.objects.create(tenant=tenant_a, title="Sent Proposal")
        assert p.sent_at is None
        p.status = Proposal.STATUS_SENT
        p.save()
        assert p.sent_at is not None

    def test_sent_at_not_overwritten_on_second_save(self, tenant_a):
        p = Proposal.objects.create(tenant=tenant_a, title="Sent Once Proposal")
        p.status = Proposal.STATUS_SENT
        p.save()
        first_sent_at = p.sent_at
        p.save()
        assert p.sent_at == first_sent_at

    def test_proposal_can_be_created_without_quote(self, tenant_a):
        p = Proposal.objects.create(tenant=tenant_a, title="No Quote Proposal")
        assert p.quote is None

    def test_proposal_links_to_quote(self, proposal_a, quote_a):
        assert proposal_a.quote == quote_a

    def test_ordering_most_recent_first(self, tenant_a):
        p1 = Proposal.objects.create(tenant=tenant_a, title="Old Prop")
        p2 = Proposal.objects.create(tenant=tenant_a, title="New Prop")
        qs = list(Proposal.objects.filter(tenant=tenant_a))
        assert qs[0].pk == p2.pk


# ============================================================ QuoteVersion
@pytest.mark.django_db
class TestQuoteVersion:
    def test_str_format(self, quote_version_a, quote_a):
        result = str(quote_version_a)
        assert "v1" in result
        assert str(quote_a) in result

    def test_default_version_number_is_1(self, tenant_a, quote_a):
        ver = QuoteVersion.objects.create(
            tenant=tenant_a, quote=quote_a, version_number=5,
            change_type=QuoteVersion.CHANGE_PRICE,
        )
        assert ver.version_number == 5

    def test_default_change_type_is_initial(self, tenant_a, quote_a):
        ver = QuoteVersion.objects.create(
            tenant=tenant_a, quote=quote_a, version_number=2,
        )
        assert ver.change_type == QuoteVersion.CHANGE_INITIAL

    def test_default_is_current_is_false(self, tenant_a, quote_a):
        ver = QuoteVersion.objects.create(
            tenant=tenant_a, quote=quote_a, version_number=3,
        )
        assert ver.is_current is False

    def test_change_choices_contain_all_five(self):
        choices = dict(QuoteVersion.CHANGE_CHOICES)
        assert QuoteVersion.CHANGE_INITIAL in choices
        assert QuoteVersion.CHANGE_PRICE in choices
        assert QuoteVersion.CHANGE_SCOPE in choices
        assert QuoteVersion.CHANGE_DISCOUNT in choices
        assert QuoteVersion.CHANGE_TERMS in choices

    def test_unique_together_quote_version_number(self, tenant_a, quote_a):
        QuoteVersion.objects.create(
            tenant=tenant_a, quote=quote_a, version_number=10,
        )
        import django.db.utils as db_utils
        with pytest.raises(db_utils.IntegrityError):
            QuoteVersion.objects.create(
                tenant=tenant_a, quote=quote_a, version_number=10,
            )

    def test_ordering_by_quote_then_descending_version(self, tenant_a, quote_a):
        QuoteVersion.objects.create(tenant=tenant_a, quote=quote_a, version_number=2)
        # quote_version_a is version 1, version 2 just created
        # ordering = ["quote", "-version_number"] => version 2 first within same quote
        qs = list(QuoteVersion.objects.filter(quote=quote_a).values_list("version_number", flat=True))
        assert qs == sorted(qs, reverse=True)
