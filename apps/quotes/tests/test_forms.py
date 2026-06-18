"""Tests for quotes.forms: field presence, required fields, and tenant-scoped FK querysets."""
import pytest
from decimal import Decimal

from apps.quotes.forms import (
    PricingRuleForm, ProposalForm, QuoteForm, QuoteLineItemForm, QuoteVersionForm,
)
from apps.quotes.models import Quote


# ============================================================ QuoteForm
@pytest.mark.django_db
class TestQuoteForm:
    def test_valid_form(self):
        form = QuoteForm(data={
            "title": "Test Quote",
            "account_name": "Acme",
            "contact_name": "Bob",
            "contact_email": "bob@acme.com",
            "status": "draft",
            "currency": "USD",
            "subtotal": "100.00",
            "discount_amount": "10.00",
            "tax_amount": "9.00",
            "total_amount": "99.00",
            "valid_until": "",
            "notes": "",
        })
        assert form.is_valid(), form.errors

    def test_missing_title_is_invalid(self):
        form = QuoteForm(data={
            "account_name": "Acme",
            "status": "draft",
            "currency": "USD",
        })
        assert not form.is_valid()
        assert "title" in form.errors

    def test_tenant_not_in_form_fields(self):
        form = QuoteForm()
        assert "tenant" not in form.fields

    def test_number_not_in_form_fields(self):
        """number is auto-generated, must not be a form field."""
        form = QuoteForm()
        assert "number" not in form.fields

    def test_sent_at_not_in_form_fields(self):
        """sent_at is system-set (off forms)."""
        form = QuoteForm()
        assert "sent_at" not in form.fields

    def test_converted_at_not_in_form_fields(self):
        """converted_at is system-set (off forms)."""
        form = QuoteForm()
        assert "converted_at" not in form.fields

    def test_created_at_not_in_form_fields(self):
        form = QuoteForm()
        assert "created_at" not in form.fields

    def test_invalid_status_choice_is_invalid(self):
        form = QuoteForm(data={
            "title": "Bad Status",
            "status": "invalid_status",
            "currency": "USD",
        })
        assert not form.is_valid()

    def test_invalid_currency_choice_is_invalid(self):
        form = QuoteForm(data={
            "title": "Bad Currency",
            "status": "draft",
            "currency": "XXX",
        })
        assert not form.is_valid()

    def test_invalid_email_is_invalid(self):
        form = QuoteForm(data={
            "title": "Bad Email",
            "status": "draft",
            "currency": "USD",
            "contact_email": "not-an-email",
        })
        assert not form.is_valid()


# ============================================================ QuoteLineItemForm
@pytest.mark.django_db
class TestQuoteLineItemForm:
    def test_valid_form(self, tenant_a, quote_a):
        form = QuoteLineItemForm(
            data={
                "quote": str(quote_a.pk),
                "product_name": "Widget",
                "sku": "W-01",
                "description": "",
                "unit": "each",
                "quantity": "2",
                "unit_price": "50.00",
                "discount_percent": "0.00",
                "position": "1",
            },
            tenant=tenant_a,
        )
        assert form.is_valid(), form.errors

    def test_missing_product_name_is_invalid(self, tenant_a, quote_a):
        form = QuoteLineItemForm(
            data={
                "quote": str(quote_a.pk),
                "unit": "each",
                "quantity": "1",
                "unit_price": "10.00",
            },
            tenant=tenant_a,
        )
        assert not form.is_valid()
        assert "product_name" in form.errors

    def test_tenant_not_in_form_fields(self, tenant_a):
        form = QuoteLineItemForm(tenant=tenant_a)
        assert "tenant" not in form.fields

    def test_line_total_not_in_form_fields(self, tenant_a):
        """line_total is computed in save(), must not be a form field."""
        form = QuoteLineItemForm(tenant=tenant_a)
        assert "line_total" not in form.fields

    def test_quote_queryset_scoped_to_tenant(self, tenant_a, tenant_b, quote_a, quote_b):
        form = QuoteLineItemForm(tenant=tenant_a)
        quote_pks = [q.pk for q in form.fields["quote"].queryset]
        assert quote_a.pk in quote_pks
        assert quote_b.pk not in quote_pks

    def test_quote_queryset_empty_when_no_tenant(self):
        """Without a tenant, queryset must be .none() to prevent cross-tenant leak."""
        form = QuoteLineItemForm(tenant=None)
        assert form.fields["quote"].queryset.count() == 0

    def test_invalid_unit_choice_is_invalid(self, tenant_a, quote_a):
        form = QuoteLineItemForm(
            data={
                "quote": str(quote_a.pk),
                "product_name": "Widget",
                "unit": "invalid_unit",
                "quantity": "1",
                "unit_price": "10.00",
            },
            tenant=tenant_a,
        )
        assert not form.is_valid()


# ============================================================ PricingRuleForm
@pytest.mark.django_db
class TestPricingRuleForm:
    def test_valid_form(self):
        form = PricingRuleForm(data={
            "name": "Volume Discount",
            "rule_type": "volume",
            "description": "10% off for bulk orders",
            "min_discount_percent": "5.00",
            "max_discount_percent": "10.00",
            "approval_level": "auto",
            "status": "active",
            "priority": "1",
        })
        assert form.is_valid(), form.errors

    def test_missing_name_is_invalid(self):
        form = PricingRuleForm(data={
            "rule_type": "volume",
            "approval_level": "auto",
            "status": "active",
        })
        assert not form.is_valid()
        assert "name" in form.errors

    def test_tenant_not_in_form_fields(self):
        form = PricingRuleForm()
        assert "tenant" not in form.fields

    def test_created_at_not_in_form_fields(self):
        form = PricingRuleForm()
        assert "created_at" not in form.fields

    def test_invalid_rule_type_is_invalid(self):
        form = PricingRuleForm(data={
            "name": "Bad Type",
            "rule_type": "invalid_type",
            "approval_level": "auto",
            "status": "active",
        })
        assert not form.is_valid()

    def test_invalid_approval_level_is_invalid(self):
        form = PricingRuleForm(data={
            "name": "Bad Approval",
            "rule_type": "volume",
            "approval_level": "invalid_level",
            "status": "active",
        })
        assert not form.is_valid()


# ============================================================ ProposalForm
@pytest.mark.django_db
class TestProposalForm:
    def test_valid_form(self, tenant_a, quote_a):
        form = ProposalForm(
            data={
                "quote": str(quote_a.pk),
                "title": "My Proposal",
                "template": "standard",
                "status": "draft",
                "executive_summary": "",
                "body": "",
                "cover_letter": "",
                "prepared_by": "Alice",
            },
            tenant=tenant_a,
        )
        assert form.is_valid(), form.errors

    def test_valid_form_without_quote(self, tenant_a):
        form = ProposalForm(
            data={
                "quote": "",
                "title": "No Quote Proposal",
                "template": "minimal",
                "status": "draft",
                "executive_summary": "",
                "body": "",
                "cover_letter": "",
                "prepared_by": "",
            },
            tenant=tenant_a,
        )
        assert form.is_valid(), form.errors

    def test_missing_title_is_invalid(self, tenant_a):
        form = ProposalForm(
            data={
                "quote": "",
                "template": "standard",
                "status": "draft",
            },
            tenant=tenant_a,
        )
        assert not form.is_valid()
        assert "title" in form.errors

    def test_tenant_not_in_form_fields(self, tenant_a):
        form = ProposalForm(tenant=tenant_a)
        assert "tenant" not in form.fields

    def test_sent_at_not_in_form_fields(self, tenant_a):
        """sent_at is system-set (off forms)."""
        form = ProposalForm(tenant=tenant_a)
        assert "sent_at" not in form.fields

    def test_quote_queryset_scoped_to_tenant(self, tenant_a, tenant_b, quote_a, quote_b):
        form = ProposalForm(tenant=tenant_a)
        quote_pks = [q.pk for q in form.fields["quote"].queryset]
        assert quote_a.pk in quote_pks
        assert quote_b.pk not in quote_pks

    def test_quote_queryset_empty_when_no_tenant(self):
        """Without a tenant, queryset must be .none() to prevent cross-tenant leak."""
        form = ProposalForm(tenant=None)
        assert form.fields["quote"].queryset.count() == 0

    def test_invalid_template_choice_is_invalid(self, tenant_a):
        form = ProposalForm(
            data={
                "quote": "",
                "title": "Bad Template",
                "template": "invalid_template",
                "status": "draft",
            },
            tenant=tenant_a,
        )
        assert not form.is_valid()


# ============================================================ QuoteVersionForm
@pytest.mark.django_db
class TestQuoteVersionForm:
    def test_valid_form(self, tenant_a, quote_a):
        form = QuoteVersionForm(
            data={
                "quote": str(quote_a.pk),
                "version_number": "1",
                "change_type": "initial",
                "change_summary": "Initial version",
                "total_amount": "500.00",
                "is_current": True,
                "snapshot_notes": "",
            },
            tenant=tenant_a,
        )
        assert form.is_valid(), form.errors

    def test_missing_quote_is_invalid(self, tenant_a):
        form = QuoteVersionForm(
            data={
                "quote": "",
                "version_number": "1",
                "change_type": "initial",
                "total_amount": "0.00",
            },
            tenant=tenant_a,
        )
        assert not form.is_valid()
        assert "quote" in form.errors

    def test_tenant_not_in_form_fields(self, tenant_a):
        form = QuoteVersionForm(tenant=tenant_a)
        assert "tenant" not in form.fields

    def test_quote_queryset_scoped_to_tenant(self, tenant_a, tenant_b, quote_a, quote_b):
        form = QuoteVersionForm(tenant=tenant_a)
        quote_pks = [q.pk for q in form.fields["quote"].queryset]
        assert quote_a.pk in quote_pks
        assert quote_b.pk not in quote_pks

    def test_quote_queryset_empty_when_no_tenant(self):
        """Without a tenant, queryset must be .none() to prevent cross-tenant leak."""
        form = QuoteVersionForm(tenant=None)
        assert form.fields["quote"].queryset.count() == 0

    def test_invalid_change_type_is_invalid(self, tenant_a, quote_a):
        form = QuoteVersionForm(
            data={
                "quote": str(quote_a.pk),
                "version_number": "1",
                "change_type": "invalid_type",
                "total_amount": "0.00",
            },
            tenant=tenant_a,
        )
        assert not form.is_valid()
