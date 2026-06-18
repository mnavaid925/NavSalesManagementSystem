"""Security tests: multi-tenant isolation and authorization enforcement for leads."""
import pytest
from django.test import Client
from django.urls import reverse

from apps.leads.models import (
    Lead, LeadConversion, LeadScore, LeadSource, NurtureCampaign,
)


# ============================================================ cross-tenant 404
@pytest.mark.django_db
class TestCrossTenantIsolation404:
    """Tenant A must receive 404 (not 403/200) on ALL Tenant B resource URLs."""

    # LeadSource
    def test_leadsource_detail_cross_tenant_404(self, client_a, leadsource_b):
        resp = client_a.get(reverse("leads:leadsource_detail", args=[leadsource_b.pk]))
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"

    def test_leadsource_edit_cross_tenant_404(self, client_a, leadsource_b):
        resp = client_a.get(reverse("leads:leadsource_edit", args=[leadsource_b.pk]))
        assert resp.status_code == 404

    def test_leadsource_delete_cross_tenant_404(self, client_a, leadsource_b):
        resp = client_a.post(reverse("leads:leadsource_delete", args=[leadsource_b.pk]))
        assert resp.status_code == 404

    # NurtureCampaign
    def test_nurturecampaign_detail_cross_tenant_404(self, client_a, campaign_b):
        resp = client_a.get(reverse("leads:nurturecampaign_detail", args=[campaign_b.pk]))
        assert resp.status_code == 404

    def test_nurturecampaign_edit_cross_tenant_404(self, client_a, campaign_b):
        resp = client_a.get(reverse("leads:nurturecampaign_edit", args=[campaign_b.pk]))
        assert resp.status_code == 404

    def test_nurturecampaign_delete_cross_tenant_404(self, client_a, campaign_b):
        resp = client_a.post(reverse("leads:nurturecampaign_delete", args=[campaign_b.pk]))
        assert resp.status_code == 404

    # Lead
    def test_lead_detail_cross_tenant_404(self, client_a, lead_b):
        resp = client_a.get(reverse("leads:lead_detail", args=[lead_b.pk]))
        assert resp.status_code == 404

    def test_lead_edit_cross_tenant_404(self, client_a, lead_b):
        resp = client_a.get(reverse("leads:lead_edit", args=[lead_b.pk]))
        assert resp.status_code == 404

    def test_lead_delete_cross_tenant_404(self, client_a, lead_b):
        resp = client_a.post(reverse("leads:lead_delete", args=[lead_b.pk]))
        assert resp.status_code == 404

    # LeadScore
    def test_leadscore_detail_cross_tenant_404(self, client_a, leadscore_b):
        resp = client_a.get(reverse("leads:leadscore_detail", args=[leadscore_b.pk]))
        assert resp.status_code == 404

    def test_leadscore_edit_cross_tenant_404(self, client_a, leadscore_b):
        resp = client_a.get(reverse("leads:leadscore_edit", args=[leadscore_b.pk]))
        assert resp.status_code == 404

    def test_leadscore_delete_cross_tenant_404(self, client_a, leadscore_b):
        resp = client_a.post(reverse("leads:leadscore_delete", args=[leadscore_b.pk]))
        assert resp.status_code == 404

    # LeadConversion
    def test_leadconversion_detail_cross_tenant_404(self, client_a, leadconversion_b):
        resp = client_a.get(reverse("leads:leadconversion_detail", args=[leadconversion_b.pk]))
        assert resp.status_code == 404

    def test_leadconversion_edit_cross_tenant_404(self, client_a, leadconversion_b):
        resp = client_a.get(reverse("leads:leadconversion_edit", args=[leadconversion_b.pk]))
        assert resp.status_code == 404

    def test_leadconversion_delete_cross_tenant_404(self, client_a, leadconversion_b):
        resp = client_a.post(reverse("leads:leadconversion_delete", args=[leadconversion_b.pk]))
        assert resp.status_code == 404


# ============================================================ list isolation
@pytest.mark.django_db
class TestListIsolation:
    """List views for Tenant A should never include Tenant B rows."""

    def test_leadsource_list_excludes_tenant_b(self, client_a, leadsource_a, leadsource_b):
        resp = client_a.get(reverse("leads:leadsource_list"))
        pks = [s.pk for s in resp.context["sources"]]
        assert leadsource_a.pk in pks
        assert leadsource_b.pk not in pks

    def test_nurturecampaign_list_excludes_tenant_b(self, client_a, campaign_a, campaign_b):
        resp = client_a.get(reverse("leads:nurturecampaign_list"))
        pks = [c.pk for c in resp.context["campaigns"]]
        assert campaign_a.pk in pks
        assert campaign_b.pk not in pks

    def test_lead_list_excludes_tenant_b(self, client_a, lead_a, lead_b):
        resp = client_a.get(reverse("leads:lead_list"))
        pks = [l.pk for l in resp.context["leads"]]
        assert lead_a.pk in pks
        assert lead_b.pk not in pks

    def test_leadscore_list_excludes_tenant_b(self, client_a, leadscore_a, leadscore_b):
        resp = client_a.get(reverse("leads:leadscore_list"))
        pks = [s.pk for s in resp.context["scores"]]
        assert leadscore_a.pk in pks
        assert leadscore_b.pk not in pks

    def test_leadconversion_list_excludes_tenant_b(
        self, client_a, leadconversion_a, leadconversion_b
    ):
        resp = client_a.get(reverse("leads:leadconversion_list"))
        pks = [c.pk for c in resp.context["conversions"]]
        assert leadconversion_a.pk in pks
        assert leadconversion_b.pk not in pks


# ============================================================ CSRF / anonymous cannot mutate
@pytest.mark.django_db
class TestCSRFAndAnonymous:
    """Anonymous users cannot mutate any leads data."""

    def test_anonymous_cannot_create_lead(self):
        from django.utils import timezone
        c = Client()
        today = timezone.localdate().isoformat()
        resp = c.post(reverse("leads:lead_create"), {
            "first_name": "Anon",
            "last_name": "Attack",
            "status": "new",
            "rating": "cold",
            "captured_on": today,
        })
        assert resp.status_code in (301, 302)

    def test_anonymous_cannot_delete_leadsource(self, tenant_a):
        src = LeadSource.objects.create(tenant=tenant_a, name="Anon Delete Target")
        c = Client()
        resp = c.post(reverse("leads:leadsource_delete", args=[src.pk]))
        assert resp.status_code in (301, 302)
        # Source must still exist
        assert LeadSource.objects.filter(pk=src.pk).exists()

    def test_anonymous_cannot_delete_lead(self, tenant_a):
        lead = Lead.objects.create(tenant=tenant_a, first_name="Anon", last_name="Target")
        c = Client()
        resp = c.post(reverse("leads:lead_delete", args=[lead.pk]))
        assert resp.status_code in (301, 302)
        assert Lead.objects.filter(pk=lead.pk).exists()

    def test_anonymous_cannot_delete_leadconversion(self, tenant_a, lead_a):
        conv = LeadConversion.objects.create(
            tenant=tenant_a, lead=lead_a, status=LeadConversion.STATUS_PENDING
        )
        c = Client()
        resp = c.post(reverse("leads:leadconversion_delete", args=[conv.pk]))
        assert resp.status_code in (301, 302)
        assert LeadConversion.objects.filter(pk=conv.pk).exists()


# ============================================================ rep cannot write
@pytest.mark.django_db
class TestRepCannotWrite:
    """Non-admin reps are blocked from all write (admin-only) views."""

    def test_rep_cannot_delete_lead(self, rep_client_a, lead_a):
        resp = rep_client_a.post(reverse("leads:lead_delete", args=[lead_a.pk]))
        # Should redirect to dashboard (not delete)
        assert resp.status_code in (301, 302)
        assert Lead.objects.filter(pk=lead_a.pk).exists()

    def test_rep_cannot_delete_leadsource(self, rep_client_a, leadsource_a):
        resp = rep_client_a.post(reverse("leads:leadsource_delete", args=[leadsource_a.pk]))
        assert resp.status_code in (301, 302)
        assert LeadSource.objects.filter(pk=leadsource_a.pk).exists()

    def test_rep_cannot_delete_campaign(self, rep_client_a, campaign_a):
        resp = rep_client_a.post(reverse("leads:nurturecampaign_delete", args=[campaign_a.pk]))
        assert resp.status_code in (301, 302)
        assert NurtureCampaign.objects.filter(pk=campaign_a.pk).exists()

    def test_rep_cannot_delete_leadscore(self, rep_client_a, leadscore_a):
        resp = rep_client_a.post(reverse("leads:leadscore_delete", args=[leadscore_a.pk]))
        assert resp.status_code in (301, 302)
        assert LeadScore.objects.filter(pk=leadscore_a.pk).exists()

    def test_rep_cannot_delete_leadconversion(self, rep_client_a, leadconversion_a):
        resp = rep_client_a.post(
            reverse("leads:leadconversion_delete", args=[leadconversion_a.pk])
        )
        assert resp.status_code in (301, 302)
        assert LeadConversion.objects.filter(pk=leadconversion_a.pk).exists()

    def test_rep_cannot_edit_lead(self, rep_client_a, lead_a):
        resp = rep_client_a.get(reverse("leads:lead_edit", args=[lead_a.pk]))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_edit_leadsource(self, rep_client_a, leadsource_a):
        resp = rep_client_a.get(reverse("leads:leadsource_edit", args=[leadsource_a.pk]))
        assert resp.status_code in (301, 302)
