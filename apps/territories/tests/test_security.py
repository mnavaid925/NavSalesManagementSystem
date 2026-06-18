"""Security tests: multi-tenant isolation and authorization enforcement for territories."""
import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from apps.territories.models import (
    CoverageModel, QuotaPlan, Territory, TerritoryAssignment, TerritoryPerformance,
)


# ============================================================ cross-tenant 404 isolation
@pytest.mark.django_db
class TestCrossTenantIsolation404:
    """Tenant A must receive 404 (not 403/200) on ALL Tenant B resource URLs."""

    # Territory
    def test_territory_detail_cross_tenant_404(self, client_a, territory_b):
        resp = client_a.get(reverse("territories:territory_detail", args=[territory_b.pk]))
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"

    def test_territory_edit_cross_tenant_404(self, client_a, territory_b):
        resp = client_a.get(reverse("territories:territory_edit", args=[territory_b.pk]))
        assert resp.status_code == 404

    def test_territory_delete_cross_tenant_404(self, client_a, territory_b):
        resp = client_a.post(reverse("territories:territory_delete", args=[territory_b.pk]))
        assert resp.status_code == 404

    def test_territory_delete_cross_tenant_does_not_delete(self, client_a, territory_b):
        client_a.post(reverse("territories:territory_delete", args=[territory_b.pk]))
        assert Territory.objects.filter(pk=territory_b.pk).exists()

    # TerritoryAssignment
    def test_assignment_detail_cross_tenant_404(self, client_a, assignment_b):
        resp = client_a.get(
            reverse("territories:territoryassignment_detail", args=[assignment_b.pk])
        )
        assert resp.status_code == 404

    def test_assignment_edit_cross_tenant_404(self, client_a, assignment_b):
        resp = client_a.get(
            reverse("territories:territoryassignment_edit", args=[assignment_b.pk])
        )
        assert resp.status_code == 404

    def test_assignment_delete_cross_tenant_404(self, client_a, assignment_b):
        resp = client_a.post(
            reverse("territories:territoryassignment_delete", args=[assignment_b.pk])
        )
        assert resp.status_code == 404

    def test_assignment_delete_cross_tenant_does_not_delete(self, client_a, assignment_b):
        client_a.post(
            reverse("territories:territoryassignment_delete", args=[assignment_b.pk])
        )
        assert TerritoryAssignment.objects.filter(pk=assignment_b.pk).exists()

    # QuotaPlan
    def test_quotaplan_detail_cross_tenant_404(self, client_a, quota_plan_b):
        resp = client_a.get(reverse("territories:quotaplan_detail", args=[quota_plan_b.pk]))
        assert resp.status_code == 404

    def test_quotaplan_edit_cross_tenant_404(self, client_a, quota_plan_b):
        resp = client_a.get(reverse("territories:quotaplan_edit", args=[quota_plan_b.pk]))
        assert resp.status_code == 404

    def test_quotaplan_delete_cross_tenant_404(self, client_a, quota_plan_b):
        resp = client_a.post(reverse("territories:quotaplan_delete", args=[quota_plan_b.pk]))
        assert resp.status_code == 404

    def test_quotaplan_delete_cross_tenant_does_not_delete(self, client_a, quota_plan_b):
        client_a.post(reverse("territories:quotaplan_delete", args=[quota_plan_b.pk]))
        assert QuotaPlan.objects.filter(pk=quota_plan_b.pk).exists()

    # CoverageModel
    def test_coveragemodel_detail_cross_tenant_404(self, client_a, coverage_model_b):
        resp = client_a.get(
            reverse("territories:coveragemodel_detail", args=[coverage_model_b.pk])
        )
        assert resp.status_code == 404

    def test_coveragemodel_edit_cross_tenant_404(self, client_a, coverage_model_b):
        resp = client_a.get(
            reverse("territories:coveragemodel_edit", args=[coverage_model_b.pk])
        )
        assert resp.status_code == 404

    def test_coveragemodel_delete_cross_tenant_404(self, client_a, coverage_model_b):
        resp = client_a.post(
            reverse("territories:coveragemodel_delete", args=[coverage_model_b.pk])
        )
        assert resp.status_code == 404

    def test_coveragemodel_delete_cross_tenant_does_not_delete(self, client_a, coverage_model_b):
        client_a.post(reverse("territories:coveragemodel_delete", args=[coverage_model_b.pk]))
        assert CoverageModel.objects.filter(pk=coverage_model_b.pk).exists()

    # TerritoryPerformance
    def test_performance_detail_cross_tenant_404(self, client_a, performance_b):
        resp = client_a.get(
            reverse("territories:territoryperformance_detail", args=[performance_b.pk])
        )
        assert resp.status_code == 404

    def test_performance_edit_cross_tenant_404(self, client_a, performance_b):
        resp = client_a.get(
            reverse("territories:territoryperformance_edit", args=[performance_b.pk])
        )
        assert resp.status_code == 404

    def test_performance_delete_cross_tenant_404(self, client_a, performance_b):
        resp = client_a.post(
            reverse("territories:territoryperformance_delete", args=[performance_b.pk])
        )
        assert resp.status_code == 404

    def test_performance_delete_cross_tenant_does_not_delete(self, client_a, performance_b):
        client_a.post(
            reverse("territories:territoryperformance_delete", args=[performance_b.pk])
        )
        assert TerritoryPerformance.objects.filter(pk=performance_b.pk).exists()


# ============================================================ list isolation
@pytest.mark.django_db
class TestListIsolation:
    """List views for Tenant A should never include Tenant B rows."""

    def test_territory_list_excludes_tenant_b(self, client_a, territory_a, territory_b):
        resp = client_a.get(reverse("territories:territory_list"))
        pks = [t.pk for t in resp.context["territories"]]
        assert territory_a.pk in pks
        assert territory_b.pk not in pks

    def test_assignment_list_excludes_tenant_b(self, client_a, assignment_a, assignment_b):
        resp = client_a.get(reverse("territories:territoryassignment_list"))
        pks = [a.pk for a in resp.context["assignments"]]
        assert assignment_a.pk in pks
        assert assignment_b.pk not in pks

    def test_quotaplan_list_excludes_tenant_b(self, client_a, quota_plan_a, quota_plan_b):
        resp = client_a.get(reverse("territories:quotaplan_list"))
        pks = [qp.pk for qp in resp.context["quota_plans"]]
        assert quota_plan_a.pk in pks
        assert quota_plan_b.pk not in pks

    def test_coveragemodel_list_excludes_tenant_b(
        self, client_a, coverage_model_a, coverage_model_b
    ):
        resp = client_a.get(reverse("territories:coveragemodel_list"))
        pks = [m.pk for m in resp.context["models"]]
        assert coverage_model_a.pk in pks
        assert coverage_model_b.pk not in pks

    def test_performance_list_excludes_tenant_b(self, client_a, performance_a, performance_b):
        resp = client_a.get(reverse("territories:territoryperformance_list"))
        pks = [s.pk for s in resp.context["snapshots"]]
        assert performance_a.pk in pks
        assert performance_b.pk not in pks


# ============================================================ anonymous POST safety
@pytest.mark.django_db
class TestAnonymousCannotMutate:
    """Anonymous requests must never mutate data."""

    def test_anonymous_cannot_create_territory(self):
        c = Client()
        resp = c.post(reverse("territories:territory_create"), {
            "name": "Anon Territory",
            "territory_type": "geographic",
            "status": "draft",
            "account_count": 0,
            "annual_potential": "0.00",
        })
        assert resp.status_code in (301, 302)
        assert not Territory.objects.filter(name="Anon Territory").exists()

    def test_anonymous_cannot_delete_territory(self, tenant_a):
        obj = Territory.objects.create(tenant=tenant_a, name="Anon Delete Terr")
        c = Client()
        resp = c.post(reverse("territories:territory_delete", args=[obj.pk]))
        assert resp.status_code in (301, 302)
        assert Territory.objects.filter(pk=obj.pk).exists()

    def test_anonymous_cannot_create_quota_plan(self):
        c = Client()
        resp = c.post(reverse("territories:quotaplan_create"), {
            "name": "Anon Plan",
            "period_type": "quarterly",
            "fiscal_year": 2026,
            "status": "draft",
            "target_amount": "0.00",
        })
        assert resp.status_code in (301, 302)
        assert not QuotaPlan.objects.filter(name="Anon Plan").exists()

    def test_anonymous_cannot_delete_coverage_model(self, tenant_a):
        obj = CoverageModel.objects.create(tenant=tenant_a, name="Anon Delete CM")
        c = Client()
        resp = c.post(reverse("territories:coveragemodel_delete", args=[obj.pk]))
        assert resp.status_code in (301, 302)
        assert CoverageModel.objects.filter(pk=obj.pk).exists()


# ============================================================ rep blocked on write views
@pytest.mark.django_db
class TestRepBlockedFromWriteViews:
    """Non-admin reps should be blocked from all write (create/edit/delete) views."""

    def test_rep_cannot_create_territory(self, rep_client_a):
        resp = rep_client_a.get(reverse("territories:territory_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_edit_territory(self, rep_client_a, territory_a):
        resp = rep_client_a.get(
            reverse("territories:territory_edit", args=[territory_a.pk])
        )
        assert resp.status_code in (301, 302)

    def test_rep_cannot_delete_territory(self, rep_client_a, territory_a):
        resp = rep_client_a.post(
            reverse("territories:territory_delete", args=[territory_a.pk])
        )
        # Redirected (not deleted) — the territory still exists
        assert Territory.objects.filter(pk=territory_a.pk).exists()

    def test_rep_cannot_create_quota_plan(self, rep_client_a):
        resp = rep_client_a.get(reverse("territories:quotaplan_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_coverage_model(self, rep_client_a):
        resp = rep_client_a.get(reverse("territories:coveragemodel_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_assignment(self, rep_client_a):
        resp = rep_client_a.get(reverse("territories:territoryassignment_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_performance(self, rep_client_a):
        resp = rep_client_a.get(reverse("territories:territoryperformance_create"))
        assert resp.status_code in (301, 302)

    def test_rep_can_view_territory_list(self, rep_client_a):
        """Reps can READ list pages — only write views are blocked."""
        resp = rep_client_a.get(reverse("territories:territory_list"))
        assert resp.status_code == 200

    def test_rep_can_view_assignment_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("territories:territoryassignment_list"))
        assert resp.status_code == 200

    def test_rep_can_view_quotaplan_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("territories:quotaplan_list"))
        assert resp.status_code == 200

    def test_rep_can_view_coveragemodel_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("territories:coveragemodel_list"))
        assert resp.status_code == 200

    def test_rep_can_view_performance_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("territories:territoryperformance_list"))
        assert resp.status_code == 200
