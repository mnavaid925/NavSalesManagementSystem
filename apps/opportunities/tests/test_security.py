"""Security tests: multi-tenant isolation (IDOR → 404) and auth/permission enforcement."""
import pytest
from django.test import Client
from django.urls import reverse

from apps.opportunities.models import (
    Competitor,
    DealCollaborator,
    Opportunity,
    OpportunityActivity,
    PipelineStage,
)


# ════════════════════════════════════════════════════════════════
#  Cross-tenant isolation: Tenant A client → Tenant B resources → 404
# ════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestCrossTenantIsolation404:
    """All object-level endpoints must return 404 when the tenant doesn't own the pk."""

    # PipelineStage
    def test_stage_detail_cross_tenant_404(self, client_a, stage_b):
        resp = client_a.get(reverse("opportunities:pipelinestage_detail", args=[stage_b.pk]))
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"

    def test_stage_edit_cross_tenant_404(self, client_a, stage_b):
        resp = client_a.get(reverse("opportunities:pipelinestage_edit", args=[stage_b.pk]))
        assert resp.status_code == 404

    def test_stage_delete_cross_tenant_404(self, client_a, stage_b):
        resp = client_a.post(reverse("opportunities:pipelinestage_delete", args=[stage_b.pk]))
        assert resp.status_code == 404

    # Opportunity
    def test_opportunity_detail_cross_tenant_404(self, client_a, opportunity_b):
        resp = client_a.get(reverse("opportunities:opportunity_detail", args=[opportunity_b.pk]))
        assert resp.status_code == 404

    def test_opportunity_edit_cross_tenant_404(self, client_a, opportunity_b):
        resp = client_a.get(reverse("opportunities:opportunity_edit", args=[opportunity_b.pk]))
        assert resp.status_code == 404

    def test_opportunity_delete_cross_tenant_404(self, client_a, opportunity_b):
        resp = client_a.post(reverse("opportunities:opportunity_delete", args=[opportunity_b.pk]))
        assert resp.status_code == 404

    # OpportunityActivity
    def test_activity_detail_cross_tenant_404(self, client_a, activity_b):
        resp = client_a.get(reverse("opportunities:opportunityactivity_detail", args=[activity_b.pk]))
        assert resp.status_code == 404

    def test_activity_edit_cross_tenant_404(self, client_a, activity_b):
        resp = client_a.get(reverse("opportunities:opportunityactivity_edit", args=[activity_b.pk]))
        assert resp.status_code == 404

    def test_activity_delete_cross_tenant_404(self, client_a, activity_b):
        resp = client_a.post(reverse("opportunities:opportunityactivity_delete", args=[activity_b.pk]))
        assert resp.status_code == 404

    # Competitor
    def test_competitor_detail_cross_tenant_404(self, client_a, competitor_b):
        resp = client_a.get(reverse("opportunities:competitor_detail", args=[competitor_b.pk]))
        assert resp.status_code == 404

    def test_competitor_edit_cross_tenant_404(self, client_a, competitor_b):
        resp = client_a.get(reverse("opportunities:competitor_edit", args=[competitor_b.pk]))
        assert resp.status_code == 404

    def test_competitor_delete_cross_tenant_404(self, client_a, competitor_b):
        resp = client_a.post(reverse("opportunities:competitor_delete", args=[competitor_b.pk]))
        assert resp.status_code == 404

    # DealCollaborator
    def test_collaborator_detail_cross_tenant_404(self, client_a, collaborator_b):
        resp = client_a.get(reverse("opportunities:dealcollaborator_detail", args=[collaborator_b.pk]))
        assert resp.status_code == 404

    def test_collaborator_edit_cross_tenant_404(self, client_a, collaborator_b):
        resp = client_a.get(reverse("opportunities:dealcollaborator_edit", args=[collaborator_b.pk]))
        assert resp.status_code == 404

    def test_collaborator_delete_cross_tenant_404(self, client_a, collaborator_b):
        resp = client_a.post(reverse("opportunities:dealcollaborator_delete", args=[collaborator_b.pk]))
        assert resp.status_code == 404


# ════════════════════════════════════════════════════════════════
#  List isolation: Tenant A lists must NOT contain Tenant B rows
# ════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestListIsolation:
    def test_stage_list_excludes_tenant_b(self, client_a, stage_a, stage_b):
        resp = client_a.get(reverse("opportunities:pipelinestage_list"))
        pks = [s.pk for s in resp.context["stages"]]
        assert stage_a.pk in pks
        assert stage_b.pk not in pks

    def test_opportunity_list_excludes_tenant_b(self, client_a, opportunity_a, opportunity_b):
        resp = client_a.get(reverse("opportunities:opportunity_list"))
        pks = [o.pk for o in resp.context["opportunities"]]
        assert opportunity_a.pk in pks
        assert opportunity_b.pk not in pks

    def test_activity_list_excludes_tenant_b(self, client_a, activity_a, activity_b):
        resp = client_a.get(reverse("opportunities:opportunityactivity_list"))
        pks = [a.pk for a in resp.context["activities"]]
        assert activity_a.pk in pks
        assert activity_b.pk not in pks

    def test_competitor_list_excludes_tenant_b(self, client_a, competitor_a, competitor_b):
        resp = client_a.get(reverse("opportunities:competitor_list"))
        pks = [c.pk for c in resp.context["competitors"]]
        assert competitor_a.pk in pks
        assert competitor_b.pk not in pks

    def test_collaborator_list_excludes_tenant_b(self, client_a, collaborator_a, collaborator_b):
        resp = client_a.get(reverse("opportunities:dealcollaborator_list"))
        pks = [c.pk for c in resp.context["collaborators"]]
        assert collaborator_a.pk in pks
        assert collaborator_b.pk not in pks


# ════════════════════════════════════════════════════════════════
#  Non-admin rep: blocked from write (create/edit/delete) views
# ════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestRepBlockedFromWriteViews:
    """tenant_admin_required → rep gets redirected (302) to dashboard:index, not 200."""

    def test_rep_cannot_create_pipeline_stage(self, rep_client_a):
        resp = rep_client_a.get(reverse("opportunities:pipelinestage_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_edit_pipeline_stage(self, rep_client_a, stage_a):
        resp = rep_client_a.get(reverse("opportunities:pipelinestage_edit", args=[stage_a.pk]))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_delete_pipeline_stage(self, rep_client_a, stage_a):
        resp = rep_client_a.post(reverse("opportunities:pipelinestage_delete", args=[stage_a.pk]))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_opportunity(self, rep_client_a):
        resp = rep_client_a.get(reverse("opportunities:opportunity_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_edit_opportunity(self, rep_client_a, opportunity_a):
        resp = rep_client_a.get(reverse("opportunities:opportunity_edit", args=[opportunity_a.pk]))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_delete_opportunity(self, rep_client_a, opportunity_a):
        resp = rep_client_a.post(reverse("opportunities:opportunity_delete", args=[opportunity_a.pk]))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_activity(self, rep_client_a):
        resp = rep_client_a.get(reverse("opportunities:opportunityactivity_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_edit_activity(self, rep_client_a, activity_a):
        resp = rep_client_a.get(reverse("opportunities:opportunityactivity_edit", args=[activity_a.pk]))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_delete_activity(self, rep_client_a, activity_a):
        resp = rep_client_a.post(reverse("opportunities:opportunityactivity_delete", args=[activity_a.pk]))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_competitor(self, rep_client_a):
        resp = rep_client_a.get(reverse("opportunities:competitor_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_edit_competitor(self, rep_client_a, competitor_a):
        resp = rep_client_a.get(reverse("opportunities:competitor_edit", args=[competitor_a.pk]))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_delete_competitor(self, rep_client_a, competitor_a):
        resp = rep_client_a.post(reverse("opportunities:competitor_delete", args=[competitor_a.pk]))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_collaborator(self, rep_client_a):
        resp = rep_client_a.get(reverse("opportunities:dealcollaborator_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_edit_collaborator(self, rep_client_a, collaborator_a):
        resp = rep_client_a.get(reverse("opportunities:dealcollaborator_edit", args=[collaborator_a.pk]))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_delete_collaborator(self, rep_client_a, collaborator_a):
        resp = rep_client_a.post(reverse("opportunities:dealcollaborator_delete", args=[collaborator_a.pk]))
        assert resp.status_code in (301, 302)

    def test_rep_can_view_list_pages(self, rep_client_a):
        """Reps can VIEW (read-only) list pages — only write views are blocked."""
        resp = rep_client_a.get(reverse("opportunities:opportunity_list"))
        assert resp.status_code == 200

    def test_rep_can_view_detail_pages(self, rep_client_a, opportunity_a):
        """Reps can VIEW detail pages (login_required only, not tenant_admin_required)."""
        resp = rep_client_a.get(reverse("opportunities:opportunity_detail", args=[opportunity_a.pk]))
        assert resp.status_code == 200


# ════════════════════════════════════════════════════════════════
#  Anonymous POST: must NOT mutate data; must redirect to login
# ════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestAnonymousCannotMutate:
    def test_anonymous_create_opportunity_redirects(self):
        c = Client()
        resp = c.post(reverse("opportunities:opportunity_create"), {
            "name": "Anon Created",
            "status": "open",
            "priority": "medium",
            "forecast_category": "pipeline",
            "amount": "0",
            "probability": 10,
        })
        assert resp.status_code in (301, 302)
        assert not Opportunity.objects.filter(name="Anon Created").exists()

    def test_anonymous_delete_opportunity_leaves_row(self, tenant_a):
        from apps.core.models import Tenant
        opp = Opportunity.objects.create(tenant=tenant_a, name="Persistent Opp")
        c = Client()
        resp = c.post(reverse("opportunities:opportunity_delete", args=[opp.pk]))
        assert resp.status_code in (301, 302)
        assert Opportunity.objects.filter(pk=opp.pk).exists()

    def test_anonymous_create_competitor_redirects(self):
        c = Client()
        resp = c.post(reverse("opportunities:competitor_create"), {
            "name": "Anon Competitor",
            "threat_level": "high",
            "status": "active",
        })
        assert resp.status_code in (301, 302)
        assert not Competitor.objects.filter(name="Anon Competitor").exists()

    def test_anonymous_create_collaborator_redirects(self):
        c = Client()
        resp = c.post(reverse("opportunities:dealcollaborator_create"), {
            "member_name": "Anon Member",
            "team_role": "legal",
            "status": "invited",
        })
        assert resp.status_code in (301, 302)
        assert not DealCollaborator.objects.filter(member_name="Anon Member").exists()


# ════════════════════════════════════════════════════════════════
#  Rep POST: write endpoints redirect, no mutation
# ════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestRepCannotMutate:
    def test_rep_create_opportunity_redirects_and_no_row(self, rep_client_a, tenant_a):
        before = Opportunity.objects.filter(tenant=tenant_a).count()
        resp = rep_client_a.post(reverse("opportunities:opportunity_create"), {
            "name": "Rep Created",
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
        assert resp.status_code in (301, 302)
        assert Opportunity.objects.filter(tenant=tenant_a).count() == before

    def test_rep_delete_opportunity_redirects_row_intact(self, rep_client_a, opportunity_a):
        resp = rep_client_a.post(
            reverse("opportunities:opportunity_delete", args=[opportunity_a.pk])
        )
        assert resp.status_code in (301, 302)
        # Row must still exist — rep was blocked before reaching delete logic
        assert Opportunity.objects.filter(pk=opportunity_a.pk).exists()

    def test_rep_delete_competitor_redirects_row_intact(self, rep_client_a, competitor_a):
        resp = rep_client_a.post(
            reverse("opportunities:competitor_delete", args=[competitor_a.pk])
        )
        assert resp.status_code in (301, 302)
        assert Competitor.objects.filter(pk=competitor_a.pk).exists()

    def test_rep_delete_collaborator_redirects_row_intact(self, rep_client_a, collaborator_a):
        resp = rep_client_a.post(
            reverse("opportunities:dealcollaborator_delete", args=[collaborator_a.pk])
        )
        assert resp.status_code in (301, 302)
        assert DealCollaborator.objects.filter(pk=collaborator_a.pk).exists()
