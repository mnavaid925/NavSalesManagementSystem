"""Security tests: multi-tenant isolation and authorization enforcement for quotes app."""
import pytest
from django.test import Client
from django.urls import reverse

from apps.quotes.models import (
    PricingRule, Proposal, Quote, QuoteLineItem, QuoteVersion,
)


# ============================================================ cross-tenant 404 isolation
@pytest.mark.django_db
class TestCrossTenantIsolation404:
    """Tenant A must receive 404 (not 403/200) on all Tenant B resource URLs."""

    # Quote
    def test_quote_detail_cross_tenant_404(self, client_a, quote_b):
        resp = client_a.get(reverse("quotes:quote_detail", args=[quote_b.pk]))
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"

    def test_quote_edit_cross_tenant_404(self, client_a, quote_b):
        resp = client_a.get(reverse("quotes:quote_edit", args=[quote_b.pk]))
        assert resp.status_code == 404

    def test_quote_delete_cross_tenant_404(self, client_a, quote_b):
        resp = client_a.post(reverse("quotes:quote_delete", args=[quote_b.pk]))
        assert resp.status_code == 404

    # QuoteLineItem
    def test_line_item_detail_cross_tenant_404(self, client_a, line_item_b):
        resp = client_a.get(reverse("quotes:quotelineitem_detail", args=[line_item_b.pk]))
        assert resp.status_code == 404

    def test_line_item_edit_cross_tenant_404(self, client_a, line_item_b):
        resp = client_a.get(reverse("quotes:quotelineitem_edit", args=[line_item_b.pk]))
        assert resp.status_code == 404

    def test_line_item_delete_cross_tenant_404(self, client_a, line_item_b):
        resp = client_a.post(reverse("quotes:quotelineitem_delete", args=[line_item_b.pk]))
        assert resp.status_code == 404

    # PricingRule
    def test_pricing_rule_detail_cross_tenant_404(self, client_a, pricing_rule_b):
        resp = client_a.get(reverse("quotes:pricingrule_detail", args=[pricing_rule_b.pk]))
        assert resp.status_code == 404

    def test_pricing_rule_edit_cross_tenant_404(self, client_a, pricing_rule_b):
        resp = client_a.get(reverse("quotes:pricingrule_edit", args=[pricing_rule_b.pk]))
        assert resp.status_code == 404

    def test_pricing_rule_delete_cross_tenant_404(self, client_a, pricing_rule_b):
        resp = client_a.post(reverse("quotes:pricingrule_delete", args=[pricing_rule_b.pk]))
        assert resp.status_code == 404

    # Proposal
    def test_proposal_detail_cross_tenant_404(self, client_a, proposal_b):
        resp = client_a.get(reverse("quotes:proposal_detail", args=[proposal_b.pk]))
        assert resp.status_code == 404

    def test_proposal_edit_cross_tenant_404(self, client_a, proposal_b):
        resp = client_a.get(reverse("quotes:proposal_edit", args=[proposal_b.pk]))
        assert resp.status_code == 404

    def test_proposal_delete_cross_tenant_404(self, client_a, proposal_b):
        resp = client_a.post(reverse("quotes:proposal_delete", args=[proposal_b.pk]))
        assert resp.status_code == 404

    # QuoteVersion
    def test_quote_version_detail_cross_tenant_404(self, client_a, quote_version_b):
        resp = client_a.get(reverse("quotes:quoteversion_detail", args=[quote_version_b.pk]))
        assert resp.status_code == 404

    def test_quote_version_edit_cross_tenant_404(self, client_a, quote_version_b):
        resp = client_a.get(reverse("quotes:quoteversion_edit", args=[quote_version_b.pk]))
        assert resp.status_code == 404

    def test_quote_version_delete_cross_tenant_404(self, client_a, quote_version_b):
        resp = client_a.post(reverse("quotes:quoteversion_delete", args=[quote_version_b.pk]))
        assert resp.status_code == 404


# ============================================================ list isolation
@pytest.mark.django_db
class TestListIsolation:
    """List views for Tenant A must never include Tenant B rows."""

    def test_quote_list_excludes_tenant_b(self, client_a, quote_a, quote_b):
        resp = client_a.get(reverse("quotes:quote_list"))
        pks = [q.pk for q in resp.context["quotes"]]
        assert quote_a.pk in pks
        assert quote_b.pk not in pks

    def test_line_item_list_excludes_tenant_b(self, client_a, line_item_a, line_item_b):
        resp = client_a.get(reverse("quotes:quotelineitem_list"))
        pks = [li.pk for li in resp.context["line_items"]]
        assert line_item_a.pk in pks
        assert line_item_b.pk not in pks

    def test_pricing_rule_list_excludes_tenant_b(self, client_a, pricing_rule_a, pricing_rule_b):
        resp = client_a.get(reverse("quotes:pricingrule_list"))
        pks = [r.pk for r in resp.context["rules"]]
        assert pricing_rule_a.pk in pks
        assert pricing_rule_b.pk not in pks

    def test_proposal_list_excludes_tenant_b(self, client_a, proposal_a, proposal_b):
        resp = client_a.get(reverse("quotes:proposal_list"))
        pks = [p.pk for p in resp.context["proposals"]]
        assert proposal_a.pk in pks
        assert proposal_b.pk not in pks

    def test_quote_version_list_excludes_tenant_b(self, client_a, quote_version_a, quote_version_b):
        resp = client_a.get(reverse("quotes:quoteversion_list"))
        pks = [v.pk for v in resp.context["versions"]]
        assert quote_version_a.pk in pks
        assert quote_version_b.pk not in pks

    def test_line_item_form_quotes_exclude_tenant_b(self, client_a, quote_a, quote_b):
        """The quotes dropdown on the line-item create form must only show tenant A quotes."""
        resp = client_a.get(reverse("quotes:quotelineitem_create"))
        assert resp.status_code == 200
        form = resp.context["form"]
        quote_pks = [q.pk for q in form.fields["quote"].queryset]
        assert quote_a.pk in quote_pks
        assert quote_b.pk not in quote_pks

    def test_proposal_form_quotes_exclude_tenant_b(self, client_a, quote_a, quote_b):
        """The quotes dropdown on the proposal create form must only show tenant A quotes."""
        resp = client_a.get(reverse("quotes:proposal_create"))
        assert resp.status_code == 200
        form = resp.context["form"]
        quote_pks = [q.pk for q in form.fields["quote"].queryset]
        assert quote_a.pk in quote_pks
        assert quote_b.pk not in quote_pks

    def test_quoteversion_form_quotes_exclude_tenant_b(self, client_a, quote_a, quote_b):
        """The quotes dropdown on the version create form must only show tenant A quotes."""
        resp = client_a.get(reverse("quotes:quoteversion_create"))
        assert resp.status_code == 200
        form = resp.context["form"]
        quote_pks = [q.pk for q in form.fields["quote"].queryset]
        assert quote_a.pk in quote_pks
        assert quote_b.pk not in quote_pks


# ============================================================ anonymous vs login
@pytest.mark.django_db
class TestAnonymousPostsDoNotMutate:
    """Anonymous POSTs to write views must redirect and NOT mutate data."""

    def test_anonymous_cannot_create_quote(self, tenant_a):
        c = Client()
        before = Quote.objects.filter(tenant=tenant_a).count()
        resp = c.post(reverse("quotes:quote_create"), {
            "title": "Anon Quote",
            "status": "draft",
            "currency": "USD",
            "subtotal": "0.00",
            "discount_amount": "0.00",
            "tax_amount": "0.00",
            "total_amount": "0.00",
        })
        assert resp.status_code in (301, 302)
        assert Quote.objects.filter(tenant=tenant_a).count() == before

    def test_anonymous_cannot_delete_quote(self, tenant_a):
        q = Quote.objects.create(tenant=tenant_a, title="Anon Delete Target")
        c = Client()
        resp = c.post(reverse("quotes:quote_delete", args=[q.pk]))
        assert resp.status_code in (301, 302)
        assert Quote.objects.filter(pk=q.pk).exists()

    def test_anonymous_cannot_create_pricing_rule(self, tenant_a):
        c = Client()
        before = PricingRule.objects.filter(tenant=tenant_a).count()
        resp = c.post(reverse("quotes:pricingrule_create"), {
            "name": "Anon Rule",
            "rule_type": "volume",
            "approval_level": "auto",
            "status": "active",
        })
        assert resp.status_code in (301, 302)
        assert PricingRule.objects.filter(tenant=tenant_a).count() == before

    def test_anonymous_cannot_delete_pricing_rule(self, tenant_a):
        rule = PricingRule.objects.create(tenant=tenant_a, name="Anon Delete Rule")
        c = Client()
        resp = c.post(reverse("quotes:pricingrule_delete", args=[rule.pk]))
        assert resp.status_code in (301, 302)
        assert PricingRule.objects.filter(pk=rule.pk).exists()

    def test_anonymous_cannot_create_proposal(self, tenant_a):
        c = Client()
        before = Proposal.objects.filter(tenant=tenant_a).count()
        resp = c.post(reverse("quotes:proposal_create"), {
            "title": "Anon Proposal",
            "template": "standard",
            "status": "draft",
        })
        assert resp.status_code in (301, 302)
        assert Proposal.objects.filter(tenant=tenant_a).count() == before


# ============================================================ rep (non-admin) access
@pytest.mark.django_db
class TestRepPermissions:
    """A non-admin rep may view list/detail but must NOT reach create/edit/delete."""

    def test_rep_can_view_quote_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("quotes:quote_list"))
        assert resp.status_code == 200

    def test_rep_can_view_pricingrule_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("quotes:pricingrule_list"))
        assert resp.status_code == 200

    def test_rep_can_view_proposal_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("quotes:proposal_list"))
        assert resp.status_code == 200

    def test_rep_can_view_quoteversion_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("quotes:quoteversion_list"))
        assert resp.status_code == 200

    def test_rep_cannot_create_quote(self, rep_client_a):
        resp = rep_client_a.get(reverse("quotes:quote_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_line_item(self, rep_client_a):
        resp = rep_client_a.get(reverse("quotes:quotelineitem_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_pricing_rule(self, rep_client_a):
        resp = rep_client_a.get(reverse("quotes:pricingrule_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_proposal(self, rep_client_a):
        resp = rep_client_a.get(reverse("quotes:proposal_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_quoteversion(self, rep_client_a):
        resp = rep_client_a.get(reverse("quotes:quoteversion_create"))
        assert resp.status_code in (301, 302)

    def test_rep_post_delete_quote_does_not_delete(self, rep_client_a, quote_a):
        """Rep POST to delete should redirect without deleting the quote."""
        resp = rep_client_a.post(reverse("quotes:quote_delete", args=[quote_a.pk]))
        assert resp.status_code in (301, 302)
        # Quote should still exist (rep was redirected before delete logic ran)
        assert Quote.objects.filter(pk=quote_a.pk).exists()

    def test_rep_post_delete_pricing_rule_does_not_delete(self, rep_client_a, pricing_rule_a):
        resp = rep_client_a.post(reverse("quotes:pricingrule_delete", args=[pricing_rule_a.pk]))
        assert resp.status_code in (301, 302)
        assert PricingRule.objects.filter(pk=pricing_rule_a.pk).exists()
