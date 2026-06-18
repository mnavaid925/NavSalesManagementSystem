"""Tests for leads views: CRUD for all leads models."""
import pytest
from django.urls import reverse
from django.test import Client
from django.utils import timezone

from apps.leads.models import (
    Lead, LeadConversion, LeadScore, LeadSource, NurtureCampaign,
)


# ============================================================ anonymous redirects
@pytest.mark.django_db
class TestAnonymousRedirects:
    def _get(self, url):
        return Client().get(url)

    def test_lead_list_redirects_anonymous(self):
        resp = self._get(reverse("leads:lead_list"))
        assert resp.status_code in (301, 302)

    def test_leadsource_list_redirects_anonymous(self):
        resp = self._get(reverse("leads:leadsource_list"))
        assert resp.status_code in (301, 302)

    def test_nurturecampaign_list_redirects_anonymous(self):
        resp = self._get(reverse("leads:nurturecampaign_list"))
        assert resp.status_code in (301, 302)

    def test_leadscore_list_redirects_anonymous(self):
        resp = self._get(reverse("leads:leadscore_list"))
        assert resp.status_code in (301, 302)

    def test_leadconversion_list_redirects_anonymous(self):
        resp = self._get(reverse("leads:leadconversion_list"))
        assert resp.status_code in (301, 302)

    def test_lead_create_redirects_anonymous(self):
        resp = self._get(reverse("leads:lead_create"))
        assert resp.status_code in (301, 302)

    def test_leadsource_create_redirects_anonymous(self):
        resp = self._get(reverse("leads:leadsource_create"))
        assert resp.status_code in (301, 302)


# ============================================================ non-admin rep blocked on write views
@pytest.mark.django_db
class TestRepBlockedFromWriteViews:
    def test_rep_cannot_create_lead(self, rep_client_a):
        resp = rep_client_a.get(reverse("leads:lead_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_leadsource(self, rep_client_a):
        resp = rep_client_a.get(reverse("leads:leadsource_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_campaign(self, rep_client_a):
        resp = rep_client_a.get(reverse("leads:nurturecampaign_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_leadscore(self, rep_client_a):
        resp = rep_client_a.get(reverse("leads:leadscore_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_leadconversion(self, rep_client_a):
        resp = rep_client_a.get(reverse("leads:leadconversion_create"))
        assert resp.status_code in (301, 302)

    def test_rep_can_view_lead_list(self, rep_client_a):
        """Reps can read the list page."""
        resp = rep_client_a.get(reverse("leads:lead_list"))
        assert resp.status_code == 200

    def test_rep_can_view_leadsource_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("leads:leadsource_list"))
        assert resp.status_code == 200

    def test_rep_can_view_leadscore_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("leads:leadscore_list"))
        assert resp.status_code == 200


# ============================================================ lead sources CRUD
@pytest.mark.django_db
class TestLeadSourceCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("leads:leadsource_list"))
        assert resp.status_code == 200

    def test_list_context_has_sources(self, client_a, leadsource_a):
        resp = client_a.get(reverse("leads:leadsource_list"))
        assert "sources" in resp.context

    def test_list_contains_tenant_a_source(self, client_a, leadsource_a):
        resp = client_a.get(reverse("leads:leadsource_list"))
        pks = [s.pk for s in resp.context["sources"]]
        assert leadsource_a.pk in pks

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("leads:leadsource_create"))
        assert resp.status_code == 200

    def test_create_post_creates_source(self, client_a, tenant_a):
        before = LeadSource.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("leads:leadsource_create"), {
            "name": "New Source",
            "source_type": "referral",
            "routing_rule": "owner",
            "status": "active",
            "default_owner": "",
            "cost_per_lead": "0.00",
            "description": "",
        })
        assert LeadSource.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a):
        client_a.post(reverse("leads:leadsource_create"), {
            "name": "Tenant Check Source",
            "source_type": "event",
            "routing_rule": "round_robin",
            "status": "active",
            "default_owner": "",
            "cost_per_lead": "0.00",
            "description": "",
        })
        src = LeadSource.objects.filter(tenant=tenant_a, name="Tenant Check Source").first()
        assert src is not None
        assert src.tenant == tenant_a

    def test_detail_200(self, client_a, leadsource_a):
        resp = client_a.get(reverse("leads:leadsource_detail", args=[leadsource_a.pk]))
        assert resp.status_code == 200

    def test_edit_get_200(self, client_a, leadsource_a):
        resp = client_a.get(reverse("leads:leadsource_edit", args=[leadsource_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_source(self, client_a, leadsource_a):
        client_a.post(reverse("leads:leadsource_edit", args=[leadsource_a.pk]), {
            "name": "Updated Source",
            "source_type": "partner",
            "routing_rule": "manual",
            "status": "paused",
            "default_owner": "",
            "cost_per_lead": "10.00",
            "description": "Updated",
        })
        leadsource_a.refresh_from_db()
        assert leadsource_a.name == "Updated Source"
        assert leadsource_a.status == "paused"

    def test_delete_post_deletes(self, client_a, tenant_a):
        src = LeadSource.objects.create(tenant=tenant_a, name="To Delete")
        client_a.post(reverse("leads:leadsource_delete", args=[src.pk]))
        assert not LeadSource.objects.filter(pk=src.pk).exists()

    def test_detail_404_for_other_tenant(self, client_a, leadsource_b):
        resp = client_a.get(reverse("leads:leadsource_detail", args=[leadsource_b.pk]))
        assert resp.status_code == 404

    def test_edit_404_for_other_tenant(self, client_a, leadsource_b):
        resp = client_a.get(reverse("leads:leadsource_edit", args=[leadsource_b.pk]))
        assert resp.status_code == 404

    def test_delete_404_for_other_tenant(self, client_a, leadsource_b):
        resp = client_a.post(reverse("leads:leadsource_delete", args=[leadsource_b.pk]))
        assert resp.status_code == 404

    def test_list_context_has_type_choices(self, client_a):
        resp = client_a.get(reverse("leads:leadsource_list"))
        assert "type_choices" in resp.context

    def test_list_context_has_routing_choices(self, client_a):
        resp = client_a.get(reverse("leads:leadsource_list"))
        assert "routing_choices" in resp.context

    def test_list_context_has_status_choices(self, client_a):
        resp = client_a.get(reverse("leads:leadsource_list"))
        assert "status_choices" in resp.context

    def test_list_search_by_name(self, client_a, leadsource_a):
        resp = client_a.get(reverse("leads:leadsource_list") + "?q=Web+Form+A")
        pks = [s.pk for s in resp.context["sources"]]
        assert leadsource_a.pk in pks

    def test_list_filter_by_status(self, client_a, leadsource_a):
        resp = client_a.get(reverse("leads:leadsource_list") + "?status=active")
        pks = [s.pk for s in resp.context["sources"]]
        assert leadsource_a.pk in pks


# ============================================================ nurture campaigns CRUD
@pytest.mark.django_db
class TestNurtureCampaignCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("leads:nurturecampaign_list"))
        assert resp.status_code == 200

    def test_list_context_has_campaigns(self, client_a, campaign_a):
        resp = client_a.get(reverse("leads:nurturecampaign_list"))
        assert "campaigns" in resp.context

    def test_list_contains_tenant_a_campaign(self, client_a, campaign_a):
        resp = client_a.get(reverse("leads:nurturecampaign_list"))
        pks = [c.pk for c in resp.context["campaigns"]]
        assert campaign_a.pk in pks

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("leads:nurturecampaign_create"))
        assert resp.status_code == 200

    def test_create_post_creates_campaign(self, client_a, tenant_a):
        before = NurtureCampaign.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("leads:nurturecampaign_create"), {
            "name": "New Campaign",
            "channel": "sms",
            "status": "draft",
            "step_count": 3,
            "cadence_days": 7,
            "enrolled_count": 0,
            "start_on": "",
            "end_on": "",
            "goal": "",
        })
        assert NurtureCampaign.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a):
        client_a.post(reverse("leads:nurturecampaign_create"), {
            "name": "Tenant Camp Check",
            "channel": "email",
            "status": "draft",
            "step_count": 1,
            "cadence_days": 3,
            "enrolled_count": 0,
            "start_on": "",
            "end_on": "",
            "goal": "",
        })
        camp = NurtureCampaign.objects.filter(tenant=tenant_a, name="Tenant Camp Check").first()
        assert camp is not None
        assert camp.tenant == tenant_a

    def test_detail_200(self, client_a, campaign_a):
        resp = client_a.get(reverse("leads:nurturecampaign_detail", args=[campaign_a.pk]))
        assert resp.status_code == 200

    def test_edit_get_200(self, client_a, campaign_a):
        resp = client_a.get(reverse("leads:nurturecampaign_edit", args=[campaign_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_campaign(self, client_a, campaign_a):
        client_a.post(reverse("leads:nurturecampaign_edit", args=[campaign_a.pk]), {
            "name": "Updated Campaign",
            "channel": "multi",
            "status": "running",
            "step_count": 5,
            "cadence_days": 14,
            "enrolled_count": 10,
            "start_on": "",
            "end_on": "",
            "goal": "Convert 50%",
        })
        campaign_a.refresh_from_db()
        assert campaign_a.name == "Updated Campaign"
        assert campaign_a.status == "running"

    def test_delete_post_deletes(self, client_a, tenant_a):
        camp = NurtureCampaign.objects.create(tenant=tenant_a, name="To Delete Camp")
        client_a.post(reverse("leads:nurturecampaign_delete", args=[camp.pk]))
        assert not NurtureCampaign.objects.filter(pk=camp.pk).exists()

    def test_detail_404_for_other_tenant(self, client_a, campaign_b):
        resp = client_a.get(reverse("leads:nurturecampaign_detail", args=[campaign_b.pk]))
        assert resp.status_code == 404

    def test_edit_404_for_other_tenant(self, client_a, campaign_b):
        resp = client_a.get(reverse("leads:nurturecampaign_edit", args=[campaign_b.pk]))
        assert resp.status_code == 404

    def test_delete_404_for_other_tenant(self, client_a, campaign_b):
        resp = client_a.post(reverse("leads:nurturecampaign_delete", args=[campaign_b.pk]))
        assert resp.status_code == 404

    def test_list_context_has_channel_choices(self, client_a):
        resp = client_a.get(reverse("leads:nurturecampaign_list"))
        assert "channel_choices" in resp.context

    def test_list_context_has_status_choices(self, client_a):
        resp = client_a.get(reverse("leads:nurturecampaign_list"))
        assert "status_choices" in resp.context


# ============================================================ leads CRUD
@pytest.mark.django_db
class TestLeadCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("leads:lead_list"))
        assert resp.status_code == 200

    def test_list_context_has_leads(self, client_a, lead_a):
        resp = client_a.get(reverse("leads:lead_list"))
        assert "leads" in resp.context

    def test_list_contains_tenant_a_lead(self, client_a, lead_a):
        resp = client_a.get(reverse("leads:lead_list"))
        pks = [l.pk for l in resp.context["leads"]]
        assert lead_a.pk in pks

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("leads:lead_create"))
        assert resp.status_code == 200

    def test_create_post_creates_lead(self, client_a, tenant_a):
        today = timezone.localdate().isoformat()
        before = Lead.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("leads:lead_create"), {
            "source": "",
            "campaign": "",
            "first_name": "Test",
            "last_name": "Lead",
            "company": "TestCo",
            "job_title": "",
            "email": "test@testco.com",
            "phone": "",
            "status": "new",
            "rating": "warm",
            "owner": "",
            "estimated_value": "0.00",
            "captured_on": today,
            "notes": "",
        })
        assert Lead.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a):
        today = timezone.localdate().isoformat()
        client_a.post(reverse("leads:lead_create"), {
            "source": "",
            "campaign": "",
            "first_name": "Tenant",
            "last_name": "Check",
            "company": "",
            "job_title": "",
            "email": "",
            "phone": "",
            "status": "new",
            "rating": "cold",
            "owner": "",
            "estimated_value": "0.00",
            "captured_on": today,
            "notes": "",
        })
        lead = Lead.objects.filter(tenant=tenant_a, first_name="Tenant", last_name="Check").first()
        assert lead is not None
        assert lead.tenant == tenant_a

    def test_create_auto_numbers_lead(self, client_a, tenant_a):
        today = timezone.localdate().isoformat()
        Lead.objects.filter(tenant=tenant_a).delete()
        client_a.post(reverse("leads:lead_create"), {
            "source": "",
            "campaign": "",
            "first_name": "Auto",
            "last_name": "Number",
            "company": "",
            "job_title": "",
            "email": "",
            "phone": "",
            "status": "new",
            "rating": "cold",
            "owner": "",
            "estimated_value": "0.00",
            "captured_on": today,
            "notes": "",
        })
        lead = Lead.objects.filter(tenant=tenant_a).latest("created_at")
        assert lead.number.startswith("LEAD-")

    def test_detail_200(self, client_a, lead_a):
        resp = client_a.get(reverse("leads:lead_detail", args=[lead_a.pk]))
        assert resp.status_code == 200

    def test_edit_get_200(self, client_a, lead_a):
        resp = client_a.get(reverse("leads:lead_edit", args=[lead_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_lead(self, client_a, lead_a):
        today = timezone.localdate().isoformat()
        client_a.post(reverse("leads:lead_edit", args=[lead_a.pk]), {
            "source": "",
            "campaign": "",
            "first_name": "AliceUpdated",
            "last_name": "Smith",
            "company": "NewCo",
            "job_title": "",
            "email": "alice@example.com",
            "phone": "",
            "status": "contacted",
            "rating": "hot",
            "owner": "",
            "estimated_value": "1000.00",
            "captured_on": today,
            "notes": "",
        })
        lead_a.refresh_from_db()
        assert lead_a.first_name == "AliceUpdated"
        assert lead_a.status == "contacted"

    def test_delete_post_deletes(self, client_a, tenant_a):
        today = timezone.localdate().isoformat()
        lead = Lead.objects.create(
            tenant=tenant_a, first_name="To", last_name="Delete"
        )
        client_a.post(reverse("leads:lead_delete", args=[lead.pk]))
        assert not Lead.objects.filter(pk=lead.pk).exists()

    def test_detail_404_for_other_tenant(self, client_a, lead_b):
        resp = client_a.get(reverse("leads:lead_detail", args=[lead_b.pk]))
        assert resp.status_code == 404

    def test_edit_404_for_other_tenant(self, client_a, lead_b):
        resp = client_a.get(reverse("leads:lead_edit", args=[lead_b.pk]))
        assert resp.status_code == 404

    def test_delete_404_for_other_tenant(self, client_a, lead_b):
        resp = client_a.post(reverse("leads:lead_delete", args=[lead_b.pk]))
        assert resp.status_code == 404

    def test_list_context_has_status_choices(self, client_a):
        resp = client_a.get(reverse("leads:lead_list"))
        assert "status_choices" in resp.context

    def test_list_context_has_rating_choices(self, client_a):
        resp = client_a.get(reverse("leads:lead_list"))
        assert "rating_choices" in resp.context

    def test_list_context_has_sources(self, client_a):
        resp = client_a.get(reverse("leads:lead_list"))
        assert "sources" in resp.context

    def test_list_search_by_name(self, client_a, lead_a):
        resp = client_a.get(reverse("leads:lead_list") + "?q=Alice")
        pks = [l.pk for l in resp.context["leads"]]
        assert lead_a.pk in pks

    def test_list_filter_by_status(self, client_a, lead_a):
        resp = client_a.get(reverse("leads:lead_list") + "?status=new")
        pks = [l.pk for l in resp.context["leads"]]
        assert lead_a.pk in pks

    def test_list_filter_by_rating(self, client_a, lead_a):
        resp = client_a.get(reverse("leads:lead_list") + "?rating=warm")
        pks = [l.pk for l in resp.context["leads"]]
        assert lead_a.pk in pks

    def test_detail_context_has_scores(self, client_a, lead_a):
        resp = client_a.get(reverse("leads:lead_detail", args=[lead_a.pk]))
        assert "scores" in resp.context

    def test_detail_context_has_conversions(self, client_a, lead_a):
        resp = client_a.get(reverse("leads:lead_detail", args=[lead_a.pk]))
        assert "conversions" in resp.context


# ============================================================ lead scores CRUD
@pytest.mark.django_db
class TestLeadScoreCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("leads:leadscore_list"))
        assert resp.status_code == 200

    def test_list_context_has_scores(self, client_a, leadscore_a):
        resp = client_a.get(reverse("leads:leadscore_list"))
        assert "scores" in resp.context

    def test_list_contains_tenant_a_score(self, client_a, leadscore_a):
        resp = client_a.get(reverse("leads:leadscore_list"))
        pks = [s.pk for s in resp.context["scores"]]
        assert leadscore_a.pk in pks

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("leads:leadscore_create"))
        assert resp.status_code == 200

    def test_create_post_creates_score(self, client_a, tenant_a, lead_a):
        today = timezone.localdate().isoformat()
        before = LeadScore.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("leads:leadscore_create"), {
            "lead": lead_a.pk,
            "score": 90,
            "grade": "A",
            "scoring_model": "rules",
            "demographic_points": 45,
            "behavioral_points": 45,
            "reason": "Excellent",
            "scored_on": today,
        })
        assert LeadScore.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a, lead_a):
        today = timezone.localdate().isoformat()
        client_a.post(reverse("leads:leadscore_create"), {
            "lead": lead_a.pk,
            "score": 60,
            "grade": "B",
            "scoring_model": "manual",
            "demographic_points": 30,
            "behavioral_points": 30,
            "reason": "Tenant check",
            "scored_on": today,
        })
        score = LeadScore.objects.filter(tenant=tenant_a, reason="Tenant check").first()
        assert score is not None
        assert score.tenant == tenant_a

    def test_detail_200(self, client_a, leadscore_a):
        resp = client_a.get(reverse("leads:leadscore_detail", args=[leadscore_a.pk]))
        assert resp.status_code == 200

    def test_edit_get_200(self, client_a, leadscore_a):
        resp = client_a.get(reverse("leads:leadscore_edit", args=[leadscore_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_score(self, client_a, leadscore_a, lead_a):
        today = timezone.localdate().isoformat()
        client_a.post(reverse("leads:leadscore_edit", args=[leadscore_a.pk]), {
            "lead": lead_a.pk,
            "score": 100,
            "grade": "A",
            "scoring_model": "predictive",
            "demographic_points": 50,
            "behavioral_points": 50,
            "reason": "Updated reason",
            "scored_on": today,
        })
        leadscore_a.refresh_from_db()
        assert leadscore_a.score == 100
        assert leadscore_a.grade == "A"

    def test_delete_post_deletes(self, client_a, tenant_a, lead_a):
        today = timezone.localdate().isoformat()
        score = LeadScore.objects.create(
            tenant=tenant_a, lead=lead_a, score=50, grade="C"
        )
        client_a.post(reverse("leads:leadscore_delete", args=[score.pk]))
        assert not LeadScore.objects.filter(pk=score.pk).exists()

    def test_detail_404_for_other_tenant(self, client_a, leadscore_b):
        resp = client_a.get(reverse("leads:leadscore_detail", args=[leadscore_b.pk]))
        assert resp.status_code == 404

    def test_edit_404_for_other_tenant(self, client_a, leadscore_b):
        resp = client_a.get(reverse("leads:leadscore_edit", args=[leadscore_b.pk]))
        assert resp.status_code == 404

    def test_delete_404_for_other_tenant(self, client_a, leadscore_b):
        resp = client_a.post(reverse("leads:leadscore_delete", args=[leadscore_b.pk]))
        assert resp.status_code == 404

    def test_list_context_has_grade_choices(self, client_a):
        resp = client_a.get(reverse("leads:leadscore_list"))
        assert "grade_choices" in resp.context

    def test_list_context_has_model_choices(self, client_a):
        resp = client_a.get(reverse("leads:leadscore_list"))
        assert "model_choices" in resp.context


# ============================================================ lead conversions CRUD
@pytest.mark.django_db
class TestLeadConversionCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("leads:leadconversion_list"))
        assert resp.status_code == 200

    def test_list_context_has_conversions(self, client_a, leadconversion_a):
        resp = client_a.get(reverse("leads:leadconversion_list"))
        assert "conversions" in resp.context

    def test_list_contains_tenant_a_conversion(self, client_a, leadconversion_a):
        resp = client_a.get(reverse("leads:leadconversion_list"))
        pks = [c.pk for c in resp.context["conversions"]]
        assert leadconversion_a.pk in pks

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("leads:leadconversion_create"))
        assert resp.status_code == 200

    def test_create_post_creates_conversion(self, client_a, tenant_a, lead_a):
        before = LeadConversion.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("leads:leadconversion_create"), {
            "lead": lead_a.pk,
            "status": "pending",
            "outcome": "opportunity",
            "assigned_to": "John",
            "deal_value": "5000.00",
            "handoff_notes": "",
        })
        assert LeadConversion.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_auto_numbers_conversion(self, client_a, tenant_a, lead_a):
        LeadConversion.objects.filter(tenant=tenant_a).delete()
        client_a.post(reverse("leads:leadconversion_create"), {
            "lead": lead_a.pk,
            "status": "pending",
            "outcome": "account",
            "assigned_to": "",
            "deal_value": "0.00",
            "handoff_notes": "",
        })
        conv = LeadConversion.objects.filter(tenant=tenant_a).latest("created_at")
        assert conv.number.startswith("CNV-")

    def test_create_assigns_correct_tenant(self, client_a, tenant_a, lead_a):
        client_a.post(reverse("leads:leadconversion_create"), {
            "lead": lead_a.pk,
            "status": "pending",
            "outcome": "contact",
            "assigned_to": "Tenant Check",
            "deal_value": "0.00",
            "handoff_notes": "",
        })
        conv = LeadConversion.objects.filter(
            tenant=tenant_a, assigned_to="Tenant Check"
        ).first()
        assert conv is not None
        assert conv.tenant == tenant_a

    def test_detail_200(self, client_a, leadconversion_a):
        resp = client_a.get(reverse("leads:leadconversion_detail", args=[leadconversion_a.pk]))
        assert resp.status_code == 200

    def test_edit_get_200(self, client_a, leadconversion_a):
        resp = client_a.get(reverse("leads:leadconversion_edit", args=[leadconversion_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_conversion(self, client_a, leadconversion_a, lead_a):
        client_a.post(reverse("leads:leadconversion_edit", args=[leadconversion_a.pk]), {
            "lead": lead_a.pk,
            "status": "accepted",
            "outcome": "opportunity",
            "assigned_to": "Jane",
            "deal_value": "9999.00",
            "handoff_notes": "All good",
        })
        leadconversion_a.refresh_from_db()
        assert leadconversion_a.status == "accepted"
        assert leadconversion_a.assigned_to == "Jane"

    def test_delete_post_deletes(self, client_a, tenant_a, lead_a):
        conv = LeadConversion.objects.create(
            tenant=tenant_a, lead=lead_a, status=LeadConversion.STATUS_PENDING
        )
        client_a.post(reverse("leads:leadconversion_delete", args=[conv.pk]))
        assert not LeadConversion.objects.filter(pk=conv.pk).exists()

    def test_detail_404_for_other_tenant(self, client_a, leadconversion_b):
        resp = client_a.get(reverse("leads:leadconversion_detail", args=[leadconversion_b.pk]))
        assert resp.status_code == 404

    def test_edit_404_for_other_tenant(self, client_a, leadconversion_b):
        resp = client_a.get(reverse("leads:leadconversion_edit", args=[leadconversion_b.pk]))
        assert resp.status_code == 404

    def test_delete_404_for_other_tenant(self, client_a, leadconversion_b):
        resp = client_a.post(reverse("leads:leadconversion_delete", args=[leadconversion_b.pk]))
        assert resp.status_code == 404

    def test_list_context_has_status_choices(self, client_a):
        resp = client_a.get(reverse("leads:leadconversion_list"))
        assert "status_choices" in resp.context

    def test_list_context_has_outcome_choices(self, client_a):
        resp = client_a.get(reverse("leads:leadconversion_list"))
        assert "outcome_choices" in resp.context
