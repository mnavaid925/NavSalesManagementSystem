"""Tests for quotes views: CRUD for Quote, QuoteLineItem, PricingRule, Proposal, QuoteVersion."""
from decimal import Decimal

import pytest
from django.urls import reverse
from django.test import Client

from apps.quotes.models import (
    PricingRule, Proposal, Quote, QuoteLineItem, QuoteVersion,
)


# ============================================================ anonymous redirects
@pytest.mark.django_db
class TestAnonymousRedirects:
    def _get(self, url):
        return Client().get(url)

    def test_quote_list_redirects_anonymous(self):
        resp = self._get(reverse("quotes:quote_list"))
        assert resp.status_code in (301, 302)

    def test_quotelineitem_list_redirects_anonymous(self):
        resp = self._get(reverse("quotes:quotelineitem_list"))
        assert resp.status_code in (301, 302)

    def test_pricingrule_list_redirects_anonymous(self):
        resp = self._get(reverse("quotes:pricingrule_list"))
        assert resp.status_code in (301, 302)

    def test_proposal_list_redirects_anonymous(self):
        resp = self._get(reverse("quotes:proposal_list"))
        assert resp.status_code in (301, 302)

    def test_quoteversion_list_redirects_anonymous(self):
        resp = self._get(reverse("quotes:quoteversion_list"))
        assert resp.status_code in (301, 302)


# ============================================================ Quote CRUD
@pytest.mark.django_db
class TestQuoteCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("quotes:quote_list"))
        assert resp.status_code == 200

    def test_list_context_has_quotes(self, client_a, quote_a):
        resp = client_a.get(reverse("quotes:quote_list"))
        assert "quotes" in resp.context

    def test_list_contains_seeded_quote(self, client_a, quote_a):
        resp = client_a.get(reverse("quotes:quote_list"))
        pks = [q.pk for q in resp.context["quotes"]]
        assert quote_a.pk in pks

    def test_list_search_filters_results(self, client_a, quote_a):
        resp = client_a.get(reverse("quotes:quote_list") + "?q=Alpha")
        assert resp.status_code == 200
        pks = [q.pk for q in resp.context["quotes"]]
        assert quote_a.pk in pks

    def test_list_context_has_status_choices(self, client_a):
        resp = client_a.get(reverse("quotes:quote_list"))
        assert "status_choices" in resp.context

    def test_list_context_has_currency_choices(self, client_a):
        resp = client_a.get(reverse("quotes:quote_list"))
        assert "currency_choices" in resp.context

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("quotes:quote_create"))
        assert resp.status_code == 200

    def test_create_post_creates_quote(self, client_a, tenant_a):
        before = Quote.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("quotes:quote_create"), {
            "title": "New Test Quote",
            "account_name": "Test Corp",
            "contact_name": "John",
            "contact_email": "john@test.com",
            "status": "draft",
            "currency": "USD",
            "subtotal": "0.00",
            "discount_amount": "0.00",
            "tax_amount": "0.00",
            "total_amount": "0.00",
            "valid_until": "",
            "notes": "",
        })
        assert Quote.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a):
        client_a.post(reverse("quotes:quote_create"), {
            "title": "Tenant Check Quote",
            "account_name": "",
            "contact_name": "",
            "contact_email": "",
            "status": "draft",
            "currency": "USD",
            "subtotal": "0.00",
            "discount_amount": "0.00",
            "tax_amount": "0.00",
            "total_amount": "0.00",
            "valid_until": "",
            "notes": "",
        })
        q = Quote.objects.filter(tenant=tenant_a, title="Tenant Check Quote").first()
        assert q is not None
        assert q.tenant == tenant_a

    def test_create_auto_numbers_quote(self, client_a, tenant_a):
        Quote.objects.filter(tenant=tenant_a).delete()
        client_a.post(reverse("quotes:quote_create"), {
            "title": "Auto Numbered",
            "status": "draft",
            "currency": "USD",
            "subtotal": "0.00",
            "discount_amount": "0.00",
            "tax_amount": "0.00",
            "total_amount": "0.00",
            "valid_until": "",
            "notes": "",
        })
        q = Quote.objects.filter(tenant=tenant_a, title="Auto Numbered").first()
        assert q is not None
        assert q.number.startswith("QUO-")

    def test_detail_200(self, client_a, quote_a):
        resp = client_a.get(reverse("quotes:quote_detail", args=[quote_a.pk]))
        assert resp.status_code == 200

    def test_detail_context_has_obj(self, client_a, quote_a):
        resp = client_a.get(reverse("quotes:quote_detail", args=[quote_a.pk]))
        assert resp.context["obj"] == quote_a

    def test_detail_context_has_line_items(self, client_a, quote_a):
        resp = client_a.get(reverse("quotes:quote_detail", args=[quote_a.pk]))
        assert "line_items" in resp.context

    def test_detail_context_has_versions(self, client_a, quote_a):
        resp = client_a.get(reverse("quotes:quote_detail", args=[quote_a.pk]))
        assert "versions" in resp.context

    def test_detail_context_has_proposals(self, client_a, quote_a):
        resp = client_a.get(reverse("quotes:quote_detail", args=[quote_a.pk]))
        assert "proposals" in resp.context

    def test_edit_get_200(self, client_a, quote_a):
        resp = client_a.get(reverse("quotes:quote_edit", args=[quote_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_quote(self, client_a, quote_a):
        client_a.post(reverse("quotes:quote_edit", args=[quote_a.pk]), {
            "title": "Updated Quote Title",
            "account_name": "Updated Corp",
            "contact_name": "",
            "contact_email": "",
            "status": "draft",
            "currency": "EUR",
            "subtotal": "200.00",
            "discount_amount": "0.00",
            "tax_amount": "0.00",
            "total_amount": "200.00",
            "valid_until": "",
            "notes": "updated",
        })
        quote_a.refresh_from_db()
        assert quote_a.title == "Updated Quote Title"
        assert quote_a.currency == "EUR"

    def test_delete_post_removes_quote(self, client_a, tenant_a):
        q = Quote.objects.create(tenant=tenant_a, title="To Delete")
        resp = client_a.post(reverse("quotes:quote_delete", args=[q.pk]))
        assert not Quote.objects.filter(pk=q.pk).exists()

    def test_delete_post_redirects_to_list(self, client_a, tenant_a):
        q = Quote.objects.create(tenant=tenant_a, title="Delete Redirect")
        resp = client_a.post(reverse("quotes:quote_delete", args=[q.pk]))
        assert resp.status_code in (301, 302)

    def test_detail_404_for_other_tenant(self, client_a, quote_b):
        resp = client_a.get(reverse("quotes:quote_detail", args=[quote_b.pk]))
        assert resp.status_code == 404

    def test_edit_404_for_other_tenant(self, client_a, quote_b):
        resp = client_a.get(reverse("quotes:quote_edit", args=[quote_b.pk]))
        assert resp.status_code == 404

    def test_delete_404_for_other_tenant(self, client_a, quote_b):
        resp = client_a.post(reverse("quotes:quote_delete", args=[quote_b.pk]))
        assert resp.status_code == 404


# ============================================================ QuoteLineItem CRUD
@pytest.mark.django_db
class TestQuoteLineItemCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("quotes:quotelineitem_list"))
        assert resp.status_code == 200

    def test_list_context_has_line_items(self, client_a, line_item_a):
        resp = client_a.get(reverse("quotes:quotelineitem_list"))
        assert "line_items" in resp.context

    def test_list_contains_seeded_line_item(self, client_a, line_item_a):
        resp = client_a.get(reverse("quotes:quotelineitem_list"))
        pks = [li.pk for li in resp.context["line_items"]]
        assert line_item_a.pk in pks

    def test_list_context_has_unit_choices(self, client_a):
        resp = client_a.get(reverse("quotes:quotelineitem_list"))
        assert "unit_choices" in resp.context

    def test_list_context_has_quotes(self, client_a):
        resp = client_a.get(reverse("quotes:quotelineitem_list"))
        assert "quotes" in resp.context

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("quotes:quotelineitem_create"))
        assert resp.status_code == 200

    def test_create_post_creates_line_item(self, client_a, tenant_a, quote_a):
        before = QuoteLineItem.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("quotes:quotelineitem_create"), {
            "quote": str(quote_a.pk),
            "product_name": "New Product",
            "sku": "NP-001",
            "description": "",
            "unit": "each",
            "quantity": "1",
            "unit_price": "99.00",
            "discount_percent": "0.00",
            "position": "1",
        })
        assert QuoteLineItem.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a, quote_a):
        client_a.post(reverse("quotes:quotelineitem_create"), {
            "quote": str(quote_a.pk),
            "product_name": "Tenant Check Item",
            "sku": "",
            "description": "",
            "unit": "each",
            "quantity": "1",
            "unit_price": "10.00",
            "discount_percent": "0.00",
            "position": "0",
        })
        li = QuoteLineItem.objects.filter(product_name="Tenant Check Item").first()
        assert li is not None
        assert li.tenant == tenant_a

    def test_detail_200(self, client_a, line_item_a):
        resp = client_a.get(reverse("quotes:quotelineitem_detail", args=[line_item_a.pk]))
        assert resp.status_code == 200

    def test_detail_404_for_other_tenant(self, client_a, line_item_b):
        resp = client_a.get(reverse("quotes:quotelineitem_detail", args=[line_item_b.pk]))
        assert resp.status_code == 404

    def test_edit_get_200(self, client_a, line_item_a):
        resp = client_a.get(reverse("quotes:quotelineitem_edit", args=[line_item_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_line_item(self, client_a, line_item_a, quote_a):
        client_a.post(reverse("quotes:quotelineitem_edit", args=[line_item_a.pk]), {
            "quote": str(quote_a.pk),
            "product_name": "Updated Widget",
            "sku": "UW-001",
            "description": "",
            "unit": "hour",
            "quantity": "5",
            "unit_price": "30.00",
            "discount_percent": "0.00",
            "position": "1",
        })
        line_item_a.refresh_from_db()
        assert line_item_a.product_name == "Updated Widget"
        assert line_item_a.unit == "hour"

    def test_edit_404_for_other_tenant(self, client_a, line_item_b):
        resp = client_a.get(reverse("quotes:quotelineitem_edit", args=[line_item_b.pk]))
        assert resp.status_code == 404

    def test_delete_post_removes_line_item(self, client_a, tenant_a, quote_a):
        # NOTE: must pass Decimal — app bug: computed_total fails with string decimal values
        li = QuoteLineItem.objects.create(
            tenant=tenant_a, quote=quote_a, product_name="To Delete",
            unit_price=Decimal("5.00"),
        )
        client_a.post(reverse("quotes:quotelineitem_delete", args=[li.pk]))
        assert not QuoteLineItem.objects.filter(pk=li.pk).exists()

    def test_delete_404_for_other_tenant(self, client_a, line_item_b):
        resp = client_a.post(reverse("quotes:quotelineitem_delete", args=[line_item_b.pk]))
        assert resp.status_code == 404


# ============================================================ PricingRule CRUD
@pytest.mark.django_db
class TestPricingRuleCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("quotes:pricingrule_list"))
        assert resp.status_code == 200

    def test_list_context_has_rules(self, client_a, pricing_rule_a):
        resp = client_a.get(reverse("quotes:pricingrule_list"))
        assert "rules" in resp.context

    def test_list_contains_seeded_rule(self, client_a, pricing_rule_a):
        resp = client_a.get(reverse("quotes:pricingrule_list"))
        pks = [r.pk for r in resp.context["rules"]]
        assert pricing_rule_a.pk in pks

    def test_list_context_has_rule_choices(self, client_a):
        resp = client_a.get(reverse("quotes:pricingrule_list"))
        assert "rule_choices" in resp.context

    def test_list_context_has_status_choices(self, client_a):
        resp = client_a.get(reverse("quotes:pricingrule_list"))
        assert "status_choices" in resp.context

    def test_list_context_has_approval_choices(self, client_a):
        resp = client_a.get(reverse("quotes:pricingrule_list"))
        assert "approval_choices" in resp.context

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("quotes:pricingrule_create"))
        assert resp.status_code == 200

    def test_create_post_creates_rule(self, client_a, tenant_a):
        before = PricingRule.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("quotes:pricingrule_create"), {
            "name": "New Volume Rule",
            "rule_type": "volume",
            "description": "",
            "min_discount_percent": "5.00",
            "max_discount_percent": "15.00",
            "approval_level": "auto",
            "status": "active",
            "priority": "0",
        })
        assert PricingRule.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a):
        client_a.post(reverse("quotes:pricingrule_create"), {
            "name": "Tenant Check Rule",
            "rule_type": "loyalty",
            "description": "",
            "min_discount_percent": "0.00",
            "max_discount_percent": "5.00",
            "approval_level": "manager",
            "status": "active",
            "priority": "0",
        })
        rule = PricingRule.objects.filter(name="Tenant Check Rule").first()
        assert rule is not None
        assert rule.tenant == tenant_a

    def test_detail_200(self, client_a, pricing_rule_a):
        resp = client_a.get(reverse("quotes:pricingrule_detail", args=[pricing_rule_a.pk]))
        assert resp.status_code == 200

    def test_detail_404_for_other_tenant(self, client_a, pricing_rule_b):
        resp = client_a.get(reverse("quotes:pricingrule_detail", args=[pricing_rule_b.pk]))
        assert resp.status_code == 404

    def test_edit_get_200(self, client_a, pricing_rule_a):
        resp = client_a.get(reverse("quotes:pricingrule_edit", args=[pricing_rule_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_rule(self, client_a, pricing_rule_a):
        client_a.post(reverse("quotes:pricingrule_edit", args=[pricing_rule_a.pk]), {
            "name": "Updated Volume Rule",
            "rule_type": "contract",
            "description": "Updated description",
            "min_discount_percent": "2.00",
            "max_discount_percent": "8.00",
            "approval_level": "director",
            "status": "inactive",
            "priority": "5",
        })
        pricing_rule_a.refresh_from_db()
        assert pricing_rule_a.name == "Updated Volume Rule"
        assert pricing_rule_a.status == "inactive"

    def test_edit_404_for_other_tenant(self, client_a, pricing_rule_b):
        resp = client_a.get(reverse("quotes:pricingrule_edit", args=[pricing_rule_b.pk]))
        assert resp.status_code == 404

    def test_delete_post_removes_rule(self, client_a, tenant_a):
        rule = PricingRule.objects.create(tenant=tenant_a, name="To Delete Rule")
        client_a.post(reverse("quotes:pricingrule_delete", args=[rule.pk]))
        assert not PricingRule.objects.filter(pk=rule.pk).exists()

    def test_delete_404_for_other_tenant(self, client_a, pricing_rule_b):
        resp = client_a.post(reverse("quotes:pricingrule_delete", args=[pricing_rule_b.pk]))
        assert resp.status_code == 404


# ============================================================ Proposal CRUD
@pytest.mark.django_db
class TestProposalCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("quotes:proposal_list"))
        assert resp.status_code == 200

    def test_list_context_has_proposals(self, client_a, proposal_a):
        resp = client_a.get(reverse("quotes:proposal_list"))
        assert "proposals" in resp.context

    def test_list_contains_seeded_proposal(self, client_a, proposal_a):
        resp = client_a.get(reverse("quotes:proposal_list"))
        pks = [p.pk for p in resp.context["proposals"]]
        assert proposal_a.pk in pks

    def test_list_context_has_template_choices(self, client_a):
        resp = client_a.get(reverse("quotes:proposal_list"))
        assert "template_choices" in resp.context

    def test_list_context_has_status_choices(self, client_a):
        resp = client_a.get(reverse("quotes:proposal_list"))
        assert "status_choices" in resp.context

    def test_list_context_has_quotes(self, client_a):
        resp = client_a.get(reverse("quotes:proposal_list"))
        assert "quotes" in resp.context

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("quotes:proposal_create"))
        assert resp.status_code == 200

    def test_create_post_creates_proposal(self, client_a, tenant_a, quote_a):
        before = Proposal.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("quotes:proposal_create"), {
            "quote": str(quote_a.pk),
            "title": "New Proposal",
            "template": "standard",
            "status": "draft",
            "executive_summary": "",
            "body": "",
            "cover_letter": "",
            "prepared_by": "Bob",
        })
        assert Proposal.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a, quote_a):
        client_a.post(reverse("quotes:proposal_create"), {
            "quote": str(quote_a.pk),
            "title": "Tenant Check Proposal",
            "template": "executive",
            "status": "draft",
            "executive_summary": "",
            "body": "",
            "cover_letter": "",
            "prepared_by": "",
        })
        p = Proposal.objects.filter(title="Tenant Check Proposal").first()
        assert p is not None
        assert p.tenant == tenant_a

    def test_detail_200(self, client_a, proposal_a):
        resp = client_a.get(reverse("quotes:proposal_detail", args=[proposal_a.pk]))
        assert resp.status_code == 200

    def test_detail_404_for_other_tenant(self, client_a, proposal_b):
        resp = client_a.get(reverse("quotes:proposal_detail", args=[proposal_b.pk]))
        assert resp.status_code == 404

    def test_edit_get_200(self, client_a, proposal_a):
        resp = client_a.get(reverse("quotes:proposal_edit", args=[proposal_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_proposal(self, client_a, proposal_a, quote_a):
        client_a.post(reverse("quotes:proposal_edit", args=[proposal_a.pk]), {
            "quote": str(quote_a.pk),
            "title": "Updated Proposal Title",
            "template": "technical",
            "status": "in_review",
            "executive_summary": "Updated summary",
            "body": "",
            "cover_letter": "",
            "prepared_by": "Charlie",
        })
        proposal_a.refresh_from_db()
        assert proposal_a.title == "Updated Proposal Title"
        assert proposal_a.template == "technical"

    def test_edit_404_for_other_tenant(self, client_a, proposal_b):
        resp = client_a.get(reverse("quotes:proposal_edit", args=[proposal_b.pk]))
        assert resp.status_code == 404

    def test_delete_post_removes_proposal(self, client_a, tenant_a):
        p = Proposal.objects.create(tenant=tenant_a, title="To Delete Proposal")
        client_a.post(reverse("quotes:proposal_delete", args=[p.pk]))
        assert not Proposal.objects.filter(pk=p.pk).exists()

    def test_delete_404_for_other_tenant(self, client_a, proposal_b):
        resp = client_a.post(reverse("quotes:proposal_delete", args=[proposal_b.pk]))
        assert resp.status_code == 404


# ============================================================ QuoteVersion CRUD
@pytest.mark.django_db
class TestQuoteVersionCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("quotes:quoteversion_list"))
        assert resp.status_code == 200

    def test_list_context_has_versions(self, client_a, quote_version_a):
        resp = client_a.get(reverse("quotes:quoteversion_list"))
        assert "versions" in resp.context

    def test_list_contains_seeded_version(self, client_a, quote_version_a):
        resp = client_a.get(reverse("quotes:quoteversion_list"))
        pks = [v.pk for v in resp.context["versions"]]
        assert quote_version_a.pk in pks

    def test_list_context_has_change_choices(self, client_a):
        resp = client_a.get(reverse("quotes:quoteversion_list"))
        assert "change_choices" in resp.context

    def test_list_context_has_quotes(self, client_a):
        resp = client_a.get(reverse("quotes:quoteversion_list"))
        assert "quotes" in resp.context

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("quotes:quoteversion_create"))
        assert resp.status_code == 200

    def test_create_post_creates_version(self, client_a, tenant_a, quote_a):
        before = QuoteVersion.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("quotes:quoteversion_create"), {
            "quote": str(quote_a.pk),
            "version_number": "2",
            "change_type": "price_change",
            "change_summary": "Updated pricing",
            "total_amount": "500.00",
            "is_current": True,
            "snapshot_notes": "",
        })
        assert QuoteVersion.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a, quote_a):
        client_a.post(reverse("quotes:quoteversion_create"), {
            "quote": str(quote_a.pk),
            "version_number": "3",
            "change_type": "scope_change",
            "change_summary": "Tenant check version",
            "total_amount": "0.00",
            "is_current": False,
            "snapshot_notes": "",
        })
        ver = QuoteVersion.objects.filter(change_summary="Tenant check version").first()
        assert ver is not None
        assert ver.tenant == tenant_a

    def test_detail_200(self, client_a, quote_version_a):
        resp = client_a.get(reverse("quotes:quoteversion_detail", args=[quote_version_a.pk]))
        assert resp.status_code == 200

    def test_detail_404_for_other_tenant(self, client_a, quote_version_b):
        resp = client_a.get(reverse("quotes:quoteversion_detail", args=[quote_version_b.pk]))
        assert resp.status_code == 404

    def test_edit_get_200(self, client_a, quote_version_a):
        resp = client_a.get(reverse("quotes:quoteversion_edit", args=[quote_version_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_version(self, client_a, quote_version_a, quote_a):
        client_a.post(reverse("quotes:quoteversion_edit", args=[quote_version_a.pk]), {
            "quote": str(quote_a.pk),
            "version_number": "1",
            "change_type": "discount_change",
            "change_summary": "Updated summary",
            "total_amount": "750.00",
            "is_current": False,
            "snapshot_notes": "Updated notes",
        })
        quote_version_a.refresh_from_db()
        assert quote_version_a.change_summary == "Updated summary"
        assert quote_version_a.change_type == "discount_change"

    def test_edit_404_for_other_tenant(self, client_a, quote_version_b):
        resp = client_a.get(reverse("quotes:quoteversion_edit", args=[quote_version_b.pk]))
        assert resp.status_code == 404

    def test_delete_post_removes_version(self, client_a, tenant_a, quote_a):
        ver = QuoteVersion.objects.create(
            tenant=tenant_a, quote=quote_a, version_number=99,
            change_type=QuoteVersion.CHANGE_TERMS,
        )
        client_a.post(reverse("quotes:quoteversion_delete", args=[ver.pk]))
        assert not QuoteVersion.objects.filter(pk=ver.pk).exists()

    def test_delete_404_for_other_tenant(self, client_a, quote_version_b):
        resp = client_a.post(reverse("quotes:quoteversion_delete", args=[quote_version_b.pk]))
        assert resp.status_code == 404
