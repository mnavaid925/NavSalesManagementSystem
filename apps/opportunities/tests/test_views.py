"""Tests for opportunities views: CRUD for all five models."""
import pytest
from django.urls import reverse
from django.test import Client

from apps.opportunities.models import (
    Competitor,
    DealCollaborator,
    Opportunity,
    OpportunityActivity,
    PipelineStage,
)


# ════════════════════════════════════════════════════════════════
#  Anonymous → redirect
# ════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestAnonymousRedirects:
    def _get(self, url):
        return Client().get(url)

    def test_pipelinestage_list_redirects_anonymous(self):
        resp = self._get(reverse("opportunities:pipelinestage_list"))
        assert resp.status_code in (301, 302)

    def test_opportunity_list_redirects_anonymous(self):
        resp = self._get(reverse("opportunities:opportunity_list"))
        assert resp.status_code in (301, 302)

    def test_opportunityactivity_list_redirects_anonymous(self):
        resp = self._get(reverse("opportunities:opportunityactivity_list"))
        assert resp.status_code in (301, 302)

    def test_competitor_list_redirects_anonymous(self):
        resp = self._get(reverse("opportunities:competitor_list"))
        assert resp.status_code in (301, 302)

    def test_dealcollaborator_list_redirects_anonymous(self):
        resp = self._get(reverse("opportunities:dealcollaborator_list"))
        assert resp.status_code in (301, 302)


# ════════════════════════════════════════════════════════════════
#  PipelineStage CRUD
# ════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestPipelineStageCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("opportunities:pipelinestage_list"))
        assert resp.status_code == 200

    def test_list_context_has_stages(self, client_a, stage_a):
        resp = client_a.get(reverse("opportunities:pipelinestage_list"))
        assert "stages" in resp.context

    def test_list_contains_seeded_stage(self, client_a, stage_a):
        resp = client_a.get(reverse("opportunities:pipelinestage_list"))
        pks = [s.pk for s in resp.context["stages"]]
        assert stage_a.pk in pks

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("opportunities:pipelinestage_create"))
        assert resp.status_code == 200

    def test_create_post_creates_stage(self, client_a, tenant_a):
        before = PipelineStage.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("opportunities:pipelinestage_create"), {
            "name": "Demo Stage",
            "description": "",
            "order": 5,
            "probability": 30,
            "stage_type": "open",
            "is_active": True,
        })
        assert PipelineStage.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a):
        client_a.post(reverse("opportunities:pipelinestage_create"), {
            "name": "Tenant Stage",
            "description": "",
            "order": 1,
            "probability": 10,
            "stage_type": "open",
            "is_active": True,
        })
        stage = PipelineStage.objects.filter(name="Tenant Stage").first()
        assert stage is not None
        assert stage.tenant == tenant_a

    def test_detail_200(self, client_a, stage_a):
        resp = client_a.get(reverse("opportunities:pipelinestage_detail", args=[stage_a.pk]))
        assert resp.status_code == 200

    def test_edit_get_200(self, client_a, stage_a):
        resp = client_a.get(reverse("opportunities:pipelinestage_edit", args=[stage_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_stage(self, client_a, stage_a):
        client_a.post(reverse("opportunities:pipelinestage_edit", args=[stage_a.pk]), {
            "name": "Updated Stage",
            "description": "Updated desc",
            "order": 2,
            "probability": 50,
            "stage_type": "open",
            "is_active": True,
        })
        stage_a.refresh_from_db()
        assert stage_a.name == "Updated Stage"
        assert stage_a.probability == 50

    def test_delete_post_removes_stage(self, client_a, tenant_a):
        stage = PipelineStage.objects.create(tenant=tenant_a, name="ToDelete")
        client_a.post(reverse("opportunities:pipelinestage_delete", args=[stage.pk]))
        assert not PipelineStage.objects.filter(pk=stage.pk).exists()

    def test_delete_redirects_to_list(self, client_a, tenant_a):
        stage = PipelineStage.objects.create(tenant=tenant_a, name="RedirDel")
        resp = client_a.post(reverse("opportunities:pipelinestage_delete", args=[stage.pk]))
        assert resp.status_code in (301, 302)


# ════════════════════════════════════════════════════════════════
#  Opportunity CRUD
# ════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestOpportunityCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("opportunities:opportunity_list"))
        assert resp.status_code == 200

    def test_list_context_has_opportunities(self, client_a, opportunity_a):
        resp = client_a.get(reverse("opportunities:opportunity_list"))
        assert "opportunities" in resp.context

    def test_list_contains_seeded_opportunity(self, client_a, opportunity_a):
        resp = client_a.get(reverse("opportunities:opportunity_list"))
        pks = [o.pk for o in resp.context["opportunities"]]
        assert opportunity_a.pk in pks

    def test_list_context_has_status_choices(self, client_a):
        resp = client_a.get(reverse("opportunities:opportunity_list"))
        assert "status_choices" in resp.context

    def test_list_context_has_priority_choices(self, client_a):
        resp = client_a.get(reverse("opportunities:opportunity_list"))
        assert "priority_choices" in resp.context

    def test_list_context_has_stages(self, client_a):
        resp = client_a.get(reverse("opportunities:opportunity_list"))
        assert "stages" in resp.context

    def test_list_search_filters_by_name(self, client_a, opportunity_a):
        resp = client_a.get(reverse("opportunities:opportunity_list") + "?q=Big")
        pks = [o.pk for o in resp.context["opportunities"]]
        assert opportunity_a.pk in pks

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("opportunities:opportunity_create"))
        assert resp.status_code == 200

    def test_create_post_creates_opportunity(self, client_a, tenant_a):
        before = Opportunity.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("opportunities:opportunity_create"), {
            "name": "New Deal",
            "account_name": "New Customer",
            "stage": "",
            "status": "open",
            "priority": "high",
            "forecast_category": "pipeline",
            "amount": "10000.00",
            "probability": 40,
            "owner_name": "Bob",
            "source": "Outbound",
            "expected_close_date": "",
            "description": "",
        })
        assert Opportunity.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a):
        client_a.post(reverse("opportunities:opportunity_create"), {
            "name": "Tenant Check Deal",
            "account_name": "",
            "stage": "",
            "status": "open",
            "priority": "medium",
            "forecast_category": "pipeline",
            "amount": "0",
            "probability": 10,
            "owner_name": "",
            "source": "",
            "expected_close_date": "",
            "description": "",
        })
        opp = Opportunity.objects.filter(name="Tenant Check Deal").first()
        assert opp is not None
        assert opp.tenant == tenant_a

    def test_create_auto_numbers_opportunity(self, client_a, tenant_a):
        Opportunity.objects.filter(tenant=tenant_a).delete()
        client_a.post(reverse("opportunities:opportunity_create"), {
            "name": "Auto Numbered",
            "account_name": "",
            "stage": "",
            "status": "open",
            "priority": "medium",
            "forecast_category": "pipeline",
            "amount": "0",
            "probability": 10,
            "owner_name": "",
            "source": "",
            "expected_close_date": "",
            "description": "",
        })
        opp = Opportunity.objects.filter(name="Auto Numbered").first()
        assert opp is not None
        assert opp.number.startswith("OPP-")

    def test_detail_200(self, client_a, opportunity_a):
        resp = client_a.get(reverse("opportunities:opportunity_detail", args=[opportunity_a.pk]))
        assert resp.status_code == 200

    def test_detail_context_has_obj(self, client_a, opportunity_a):
        resp = client_a.get(reverse("opportunities:opportunity_detail", args=[opportunity_a.pk]))
        assert "obj" in resp.context
        assert resp.context["obj"].pk == opportunity_a.pk

    def test_detail_context_has_activities(self, client_a, opportunity_a):
        resp = client_a.get(reverse("opportunities:opportunity_detail", args=[opportunity_a.pk]))
        assert "activities" in resp.context

    def test_detail_context_has_competitors(self, client_a, opportunity_a):
        resp = client_a.get(reverse("opportunities:opportunity_detail", args=[opportunity_a.pk]))
        assert "competitors" in resp.context

    def test_detail_context_has_collaborators(self, client_a, opportunity_a):
        resp = client_a.get(reverse("opportunities:opportunity_detail", args=[opportunity_a.pk]))
        assert "collaborators" in resp.context

    def test_edit_get_200(self, client_a, opportunity_a):
        resp = client_a.get(reverse("opportunities:opportunity_edit", args=[opportunity_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_opportunity(self, client_a, opportunity_a):
        client_a.post(reverse("opportunities:opportunity_edit", args=[opportunity_a.pk]), {
            "name": "Updated Big Deal",
            "account_name": "Updated Customer",
            "stage": "",
            "status": "open",
            "priority": "critical",
            "forecast_category": "commit",
            "amount": "75000.00",
            "probability": 80,
            "owner_name": "Charlie",
            "source": "",
            "expected_close_date": "",
            "description": "Updated description",
        })
        opportunity_a.refresh_from_db()
        assert opportunity_a.name == "Updated Big Deal"
        assert opportunity_a.priority == "critical"

    def test_delete_post_removes_opportunity(self, client_a, tenant_a):
        opp = Opportunity.objects.create(tenant=tenant_a, name="ToDelete")
        client_a.post(reverse("opportunities:opportunity_delete", args=[opp.pk]))
        assert not Opportunity.objects.filter(pk=opp.pk).exists()

    def test_delete_redirects_to_list(self, client_a, tenant_a):
        opp = Opportunity.objects.create(tenant=tenant_a, name="RedirDel")
        resp = client_a.post(reverse("opportunities:opportunity_delete", args=[opp.pk]))
        assert resp.status_code in (301, 302)


# ════════════════════════════════════════════════════════════════
#  OpportunityActivity CRUD
# ════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestOpportunityActivityCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("opportunities:opportunityactivity_list"))
        assert resp.status_code == 200

    def test_list_context_has_activities(self, client_a, activity_a):
        resp = client_a.get(reverse("opportunities:opportunityactivity_list"))
        assert "activities" in resp.context

    def test_list_contains_seeded_activity(self, client_a, activity_a):
        resp = client_a.get(reverse("opportunities:opportunityactivity_list"))
        pks = [a.pk for a in resp.context["activities"]]
        assert activity_a.pk in pks

    def test_list_context_has_type_choices(self, client_a):
        resp = client_a.get(reverse("opportunities:opportunityactivity_list"))
        assert "type_choices" in resp.context

    def test_list_context_has_outcome_choices(self, client_a):
        resp = client_a.get(reverse("opportunities:opportunityactivity_list"))
        assert "outcome_choices" in resp.context

    def test_list_context_has_opportunities(self, client_a):
        resp = client_a.get(reverse("opportunities:opportunityactivity_list"))
        assert "opportunities" in resp.context

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("opportunities:opportunityactivity_create"))
        assert resp.status_code == 200

    def test_create_post_creates_activity(self, client_a, tenant_a, opportunity_a):
        before = OpportunityActivity.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("opportunities:opportunityactivity_create"), {
            "opportunity": opportunity_a.pk,
            "subject": "New Call Activity",
            "activity_type": "call",
            "outcome": "positive",
            "performed_by": "Alice",
            "activity_date": "2026-02-01",
            "notes": "",
        })
        assert OpportunityActivity.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a, opportunity_a):
        client_a.post(reverse("opportunities:opportunityactivity_create"), {
            "opportunity": opportunity_a.pk,
            "subject": "Tenant Check Activity",
            "activity_type": "note",
            "outcome": "pending",
            "performed_by": "",
            "activity_date": "",
            "notes": "",
        })
        act = OpportunityActivity.objects.filter(subject="Tenant Check Activity").first()
        assert act is not None
        assert act.tenant == tenant_a

    def test_detail_200(self, client_a, activity_a):
        resp = client_a.get(reverse("opportunities:opportunityactivity_detail", args=[activity_a.pk]))
        assert resp.status_code == 200

    def test_edit_get_200(self, client_a, activity_a):
        resp = client_a.get(reverse("opportunities:opportunityactivity_edit", args=[activity_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_activity(self, client_a, activity_a, opportunity_a):
        client_a.post(reverse("opportunities:opportunityactivity_edit", args=[activity_a.pk]), {
            "opportunity": opportunity_a.pk,
            "subject": "Updated Call",
            "activity_type": "meeting",
            "outcome": "neutral",
            "performed_by": "Alice",
            "activity_date": "",
            "notes": "Updated notes",
        })
        activity_a.refresh_from_db()
        assert activity_a.subject == "Updated Call"
        assert activity_a.activity_type == "meeting"

    def test_delete_post_removes_activity(self, client_a, tenant_a, opportunity_a):
        act = OpportunityActivity.objects.create(
            tenant=tenant_a,
            opportunity=opportunity_a,
            subject="DeleteMe",
        )
        client_a.post(reverse("opportunities:opportunityactivity_delete", args=[act.pk]))
        assert not OpportunityActivity.objects.filter(pk=act.pk).exists()

    def test_delete_redirects(self, client_a, tenant_a, opportunity_a):
        act = OpportunityActivity.objects.create(
            tenant=tenant_a,
            opportunity=opportunity_a,
            subject="RedirDelete",
        )
        resp = client_a.post(reverse("opportunities:opportunityactivity_delete", args=[act.pk]))
        assert resp.status_code in (301, 302)


# ════════════════════════════════════════════════════════════════
#  Competitor CRUD
# ════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestCompetitorCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("opportunities:competitor_list"))
        assert resp.status_code == 200

    def test_list_context_has_competitors(self, client_a, competitor_a):
        resp = client_a.get(reverse("opportunities:competitor_list"))
        assert "competitors" in resp.context

    def test_list_contains_seeded_competitor(self, client_a, competitor_a):
        resp = client_a.get(reverse("opportunities:competitor_list"))
        pks = [c.pk for c in resp.context["competitors"]]
        assert competitor_a.pk in pks

    def test_list_context_has_threat_choices(self, client_a):
        resp = client_a.get(reverse("opportunities:competitor_list"))
        assert "threat_choices" in resp.context

    def test_list_context_has_status_choices(self, client_a):
        resp = client_a.get(reverse("opportunities:competitor_list"))
        assert "status_choices" in resp.context

    def test_list_context_has_opportunities(self, client_a):
        resp = client_a.get(reverse("opportunities:competitor_list"))
        assert "opportunities" in resp.context

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("opportunities:competitor_create"))
        assert resp.status_code == 200

    def test_create_post_creates_competitor(self, client_a, tenant_a, opportunity_a):
        before = Competitor.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("opportunities:competitor_create"), {
            "opportunity": opportunity_a.pk,
            "name": "NewRival",
            "threat_level": "medium",
            "status": "active",
            "strengths": "",
            "weaknesses": "",
            "our_strategy": "",
        })
        assert Competitor.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a, opportunity_a):
        client_a.post(reverse("opportunities:competitor_create"), {
            "opportunity": opportunity_a.pk,
            "name": "TenantCheckRival",
            "threat_level": "low",
            "status": "active",
            "strengths": "",
            "weaknesses": "",
            "our_strategy": "",
        })
        comp = Competitor.objects.filter(name="TenantCheckRival").first()
        assert comp is not None
        assert comp.tenant == tenant_a

    def test_detail_200(self, client_a, competitor_a):
        resp = client_a.get(reverse("opportunities:competitor_detail", args=[competitor_a.pk]))
        assert resp.status_code == 200

    def test_edit_get_200(self, client_a, competitor_a):
        resp = client_a.get(reverse("opportunities:competitor_edit", args=[competitor_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_competitor(self, client_a, competitor_a, opportunity_a):
        client_a.post(reverse("opportunities:competitor_edit", args=[competitor_a.pk]), {
            "opportunity": opportunity_a.pk,
            "name": "UpdatedRival",
            "threat_level": "low",
            "status": "eliminated",
            "strengths": "Was strong",
            "weaknesses": "Too expensive",
            "our_strategy": "Win on service",
        })
        competitor_a.refresh_from_db()
        assert competitor_a.name == "UpdatedRival"
        assert competitor_a.status == "eliminated"

    def test_delete_post_removes_competitor(self, client_a, tenant_a, opportunity_a):
        comp = Competitor.objects.create(
            tenant=tenant_a, opportunity=opportunity_a, name="DeleteMe"
        )
        client_a.post(reverse("opportunities:competitor_delete", args=[comp.pk]))
        assert not Competitor.objects.filter(pk=comp.pk).exists()

    def test_delete_redirects(self, client_a, tenant_a, opportunity_a):
        comp = Competitor.objects.create(
            tenant=tenant_a, opportunity=opportunity_a, name="RedirDelete"
        )
        resp = client_a.post(reverse("opportunities:competitor_delete", args=[comp.pk]))
        assert resp.status_code in (301, 302)


# ════════════════════════════════════════════════════════════════
#  DealCollaborator CRUD
# ════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestDealCollaboratorCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("opportunities:dealcollaborator_list"))
        assert resp.status_code == 200

    def test_list_context_has_collaborators(self, client_a, collaborator_a):
        resp = client_a.get(reverse("opportunities:dealcollaborator_list"))
        assert "collaborators" in resp.context

    def test_list_contains_seeded_collaborator(self, client_a, collaborator_a):
        resp = client_a.get(reverse("opportunities:dealcollaborator_list"))
        pks = [c.pk for c in resp.context["collaborators"]]
        assert collaborator_a.pk in pks

    def test_list_context_has_role_choices(self, client_a):
        resp = client_a.get(reverse("opportunities:dealcollaborator_list"))
        assert "role_choices" in resp.context

    def test_list_context_has_status_choices(self, client_a):
        resp = client_a.get(reverse("opportunities:dealcollaborator_list"))
        assert "status_choices" in resp.context

    def test_list_context_has_opportunities(self, client_a):
        resp = client_a.get(reverse("opportunities:dealcollaborator_list"))
        assert "opportunities" in resp.context

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("opportunities:dealcollaborator_create"))
        assert resp.status_code == 200

    def test_create_post_creates_collaborator(self, client_a, tenant_a, opportunity_a):
        before = DealCollaborator.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("opportunities:dealcollaborator_create"), {
            "opportunity": opportunity_a.pk,
            "member_name": "New Member",
            "email": "new@acme.com",
            "team_role": "legal",
            "status": "invited",
            "contribution": "",
        })
        assert DealCollaborator.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a, opportunity_a):
        client_a.post(reverse("opportunities:dealcollaborator_create"), {
            "opportunity": opportunity_a.pk,
            "member_name": "Tenant Check Member",
            "email": "",
            "team_role": "support",
            "status": "active",
            "contribution": "",
        })
        collab = DealCollaborator.objects.filter(member_name="Tenant Check Member").first()
        assert collab is not None
        assert collab.tenant == tenant_a

    def test_detail_200(self, client_a, collaborator_a):
        resp = client_a.get(reverse("opportunities:dealcollaborator_detail", args=[collaborator_a.pk]))
        assert resp.status_code == 200

    def test_edit_get_200(self, client_a, collaborator_a):
        resp = client_a.get(reverse("opportunities:dealcollaborator_edit", args=[collaborator_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_collaborator(self, client_a, collaborator_a, opportunity_a):
        client_a.post(reverse("opportunities:dealcollaborator_edit", args=[collaborator_a.pk]), {
            "opportunity": opportunity_a.pk,
            "member_name": "Updated Carol",
            "email": "carol-updated@acme.com",
            "team_role": "exec_sponsor",
            "status": "inactive",
            "contribution": "Sponsor activities",
        })
        collaborator_a.refresh_from_db()
        assert collaborator_a.member_name == "Updated Carol"
        assert collaborator_a.team_role == "exec_sponsor"

    def test_delete_post_removes_collaborator(self, client_a, tenant_a, opportunity_a):
        collab = DealCollaborator.objects.create(
            tenant=tenant_a, opportunity=opportunity_a, member_name="DeleteMe"
        )
        client_a.post(reverse("opportunities:dealcollaborator_delete", args=[collab.pk]))
        assert not DealCollaborator.objects.filter(pk=collab.pk).exists()

    def test_delete_redirects(self, client_a, tenant_a, opportunity_a):
        collab = DealCollaborator.objects.create(
            tenant=tenant_a, opportunity=opportunity_a, member_name="RedirDelete"
        )
        resp = client_a.post(reverse("opportunities:dealcollaborator_delete", args=[collab.pk]))
        assert resp.status_code in (301, 302)
