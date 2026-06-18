"""Tests for territories views: CRUD for all five models."""
import pytest
from django.urls import reverse
from django.test import Client
from django.utils import timezone

from apps.territories.models import (
    CoverageModel, QuotaPlan, Territory, TerritoryAssignment, TerritoryPerformance,
)


# ============================================================ anonymous redirects
@pytest.mark.django_db
class TestAnonymousRedirects:
    def _get(self, url):
        return Client().get(url)

    def test_territory_list_redirects_anonymous(self):
        resp = self._get(reverse("territories:territory_list"))
        assert resp.status_code in (301, 302)

    def test_assignment_list_redirects_anonymous(self):
        resp = self._get(reverse("territories:territoryassignment_list"))
        assert resp.status_code in (301, 302)

    def test_quotaplan_list_redirects_anonymous(self):
        resp = self._get(reverse("territories:quotaplan_list"))
        assert resp.status_code in (301, 302)

    def test_coveragemodel_list_redirects_anonymous(self):
        resp = self._get(reverse("territories:coveragemodel_list"))
        assert resp.status_code in (301, 302)

    def test_performance_list_redirects_anonymous(self):
        resp = self._get(reverse("territories:territoryperformance_list"))
        assert resp.status_code in (301, 302)


# ============================================================ Territory CRUD
@pytest.mark.django_db
class TestTerritoryCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("territories:territory_list"))
        assert resp.status_code == 200

    def test_list_context_has_territories(self, client_a, territory_a):
        resp = client_a.get(reverse("territories:territory_list"))
        assert "territories" in resp.context

    def test_list_seeded_territory_appears(self, client_a, territory_a):
        resp = client_a.get(reverse("territories:territory_list"))
        pks = [t.pk for t in resp.context["territories"]]
        assert territory_a.pk in pks

    def test_list_status_filter_works(self, client_a, territory_a):
        resp = client_a.get(reverse("territories:territory_list") + "?status=active")
        assert resp.status_code == 200

    def test_list_search_works(self, client_a, territory_a):
        resp = client_a.get(reverse("territories:territory_list") + "?q=North")
        assert resp.status_code == 200
        pks = [t.pk for t in resp.context["territories"]]
        assert territory_a.pk in pks

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("territories:territory_create"))
        assert resp.status_code == 200

    def test_create_post_creates_territory(self, client_a, tenant_a):
        before = Territory.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("territories:territory_create"), {
            "name": "New Territory",
            "code": "NT-001",
            "territory_type": "geographic",
            "status": "draft",
            "region": "East",
            "country": "US",
            "description": "",
            "account_count": 0,
            "annual_potential": "0.00",
        })
        assert Territory.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a):
        client_a.post(reverse("territories:territory_create"), {
            "name": "Tenant Check Territory",
            "code": "",
            "territory_type": "geographic",
            "status": "draft",
            "region": "",
            "country": "",
            "description": "",
            "account_count": 0,
            "annual_potential": "0.00",
        })
        obj = Territory.objects.filter(name="Tenant Check Territory").first()
        assert obj is not None
        assert obj.tenant == tenant_a

    def test_detail_200(self, client_a, territory_a):
        resp = client_a.get(reverse("territories:territory_detail", args=[territory_a.pk]))
        assert resp.status_code == 200

    def test_detail_context_has_obj(self, client_a, territory_a):
        resp = client_a.get(reverse("territories:territory_detail", args=[territory_a.pk]))
        assert "obj" in resp.context
        assert resp.context["obj"].pk == territory_a.pk

    def test_edit_get_200(self, client_a, territory_a):
        resp = client_a.get(reverse("territories:territory_edit", args=[territory_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates(self, client_a, territory_a):
        client_a.post(reverse("territories:territory_edit", args=[territory_a.pk]), {
            "name": "Updated North Region",
            "code": "NR-001",
            "territory_type": "geographic",
            "status": "active",
            "region": "North",
            "country": "US",
            "description": "Updated",
            "account_count": 5,
            "annual_potential": "100000.00",
        })
        territory_a.refresh_from_db()
        assert territory_a.name == "Updated North Region"

    def test_delete_post_deletes(self, client_a, tenant_a):
        obj = Territory.objects.create(
            tenant=tenant_a, name="To Delete Territory", territory_type="geographic",
        )
        client_a.post(reverse("territories:territory_delete", args=[obj.pk]))
        assert not Territory.objects.filter(pk=obj.pk).exists()

    def test_delete_post_redirects_to_list(self, client_a, tenant_a):
        obj = Territory.objects.create(
            tenant=tenant_a, name="Redirect Territory", territory_type="geographic",
        )
        resp = client_a.post(reverse("territories:territory_delete", args=[obj.pk]))
        assert resp.status_code in (301, 302)

    def test_detail_404_for_other_tenant(self, client_a, territory_b):
        resp = client_a.get(reverse("territories:territory_detail", args=[territory_b.pk]))
        assert resp.status_code == 404

    def test_edit_404_for_other_tenant(self, client_a, territory_b):
        resp = client_a.get(reverse("territories:territory_edit", args=[territory_b.pk]))
        assert resp.status_code == 404


# ============================================================ TerritoryAssignment CRUD
@pytest.mark.django_db
class TestTerritoryAssignmentCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("territories:territoryassignment_list"))
        assert resp.status_code == 200

    def test_list_context_has_assignments(self, client_a, assignment_a):
        resp = client_a.get(reverse("territories:territoryassignment_list"))
        assert "assignments" in resp.context

    def test_list_seeded_assignment_appears(self, client_a, assignment_a):
        resp = client_a.get(reverse("territories:territoryassignment_list"))
        pks = [a.pk for a in resp.context["assignments"]]
        assert assignment_a.pk in pks

    def test_list_search_works(self, client_a, assignment_a):
        resp = client_a.get(reverse("territories:territoryassignment_list") + "?q=Alice")
        assert resp.status_code == 200
        pks = [a.pk for a in resp.context["assignments"]]
        assert assignment_a.pk in pks

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("territories:territoryassignment_create"))
        assert resp.status_code == 200

    def test_create_post_creates_assignment(self, client_a, tenant_a, territory_a):
        before = TerritoryAssignment.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("territories:territoryassignment_create"), {
            "territory": territory_a.pk,
            "rep_name": "Carol White",
            "rep_email": "carol@example.com",
            "assignment_role": "owner",
            "status": "proposed",
            "workload_percent": 100,
            "effective_date": timezone.localdate().isoformat(),
            "end_date": "",
            "notes": "",
        })
        assert TerritoryAssignment.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a, territory_a):
        client_a.post(reverse("territories:territoryassignment_create"), {
            "territory": territory_a.pk,
            "rep_name": "Tenant Test Rep",
            "rep_email": "",
            "assignment_role": "owner",
            "status": "proposed",
            "workload_percent": 100,
            "effective_date": timezone.localdate().isoformat(),
            "end_date": "",
            "notes": "",
        })
        obj = TerritoryAssignment.objects.filter(rep_name="Tenant Test Rep").first()
        assert obj is not None
        assert obj.tenant == tenant_a

    def test_detail_200(self, client_a, assignment_a):
        resp = client_a.get(reverse("territories:territoryassignment_detail", args=[assignment_a.pk]))
        assert resp.status_code == 200

    def test_edit_get_200(self, client_a, assignment_a):
        resp = client_a.get(reverse("territories:territoryassignment_edit", args=[assignment_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates(self, client_a, assignment_a, territory_a):
        client_a.post(reverse("territories:territoryassignment_edit", args=[assignment_a.pk]), {
            "territory": territory_a.pk,
            "rep_name": "Alice Updated",
            "rep_email": "alice@example.com",
            "assignment_role": "owner",
            "status": "active",
            "workload_percent": 80,
            "effective_date": timezone.localdate().isoformat(),
            "end_date": "",
            "notes": "",
        })
        assignment_a.refresh_from_db()
        assert assignment_a.rep_name == "Alice Updated"

    def test_delete_post_deletes(self, client_a, tenant_a, territory_a):
        obj = TerritoryAssignment.objects.create(
            tenant=tenant_a, territory=territory_a, rep_name="Delete Rep",
            effective_date=timezone.localdate(),
        )
        client_a.post(reverse("territories:territoryassignment_delete", args=[obj.pk]))
        assert not TerritoryAssignment.objects.filter(pk=obj.pk).exists()

    def test_detail_404_for_other_tenant(self, client_a, assignment_b):
        resp = client_a.get(
            reverse("territories:territoryassignment_detail", args=[assignment_b.pk])
        )
        assert resp.status_code == 404

    def test_edit_404_for_other_tenant(self, client_a, assignment_b):
        resp = client_a.get(
            reverse("territories:territoryassignment_edit", args=[assignment_b.pk])
        )
        assert resp.status_code == 404


# ============================================================ QuotaPlan CRUD
@pytest.mark.django_db
class TestQuotaPlanCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("territories:quotaplan_list"))
        assert resp.status_code == 200

    def test_list_context_has_quota_plans(self, client_a, quota_plan_a):
        resp = client_a.get(reverse("territories:quotaplan_list"))
        assert "quota_plans" in resp.context

    def test_list_seeded_plan_appears(self, client_a, quota_plan_a):
        resp = client_a.get(reverse("territories:quotaplan_list"))
        pks = [qp.pk for qp in resp.context["quota_plans"]]
        assert quota_plan_a.pk in pks

    def test_list_search_works(self, client_a, quota_plan_a):
        resp = client_a.get(reverse("territories:quotaplan_list") + "?q=Q1")
        assert resp.status_code == 200
        pks = [qp.pk for qp in resp.context["quota_plans"]]
        assert quota_plan_a.pk in pks

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("territories:quotaplan_create"))
        assert resp.status_code == 200

    def test_create_post_creates_plan(self, client_a, tenant_a, territory_a):
        before = QuotaPlan.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("territories:quotaplan_create"), {
            "territory": territory_a.pk,
            "name": "New Q Plan",
            "period_type": "quarterly",
            "fiscal_year": 2026,
            "status": "draft",
            "target_amount": "20000.00",
            "stretch_amount": "25000.00",
            "start_date": "",
            "end_date": "",
            "notes": "",
        })
        assert QuotaPlan.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_auto_numbers_plan(self, client_a, tenant_a):
        QuotaPlan.objects.filter(tenant=tenant_a).delete()
        client_a.post(reverse("territories:quotaplan_create"), {
            "territory": "",
            "name": "Numbered Plan",
            "period_type": "annual",
            "fiscal_year": 2026,
            "status": "draft",
            "target_amount": "0.00",
            "stretch_amount": "0.00",
            "start_date": "",
            "end_date": "",
            "notes": "",
        })
        qp = QuotaPlan.objects.filter(tenant=tenant_a).latest("created_at")
        assert qp.number.startswith("QP-")

    def test_create_assigns_correct_tenant(self, client_a, tenant_a):
        client_a.post(reverse("territories:quotaplan_create"), {
            "territory": "",
            "name": "Tenant Check QP",
            "period_type": "monthly",
            "fiscal_year": 2026,
            "status": "draft",
            "target_amount": "0.00",
            "stretch_amount": "0.00",
            "start_date": "",
            "end_date": "",
            "notes": "tc",
        })
        obj = QuotaPlan.objects.filter(tenant=tenant_a, notes="tc").first()
        assert obj is not None
        assert obj.tenant == tenant_a

    def test_detail_200(self, client_a, quota_plan_a):
        resp = client_a.get(reverse("territories:quotaplan_detail", args=[quota_plan_a.pk]))
        assert resp.status_code == 200

    def test_edit_get_200(self, client_a, quota_plan_a):
        resp = client_a.get(reverse("territories:quotaplan_edit", args=[quota_plan_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates(self, client_a, quota_plan_a, territory_a):
        client_a.post(reverse("territories:quotaplan_edit", args=[quota_plan_a.pk]), {
            "territory": territory_a.pk,
            "name": "Updated Q1 Plan",
            "period_type": "quarterly",
            "fiscal_year": 2026,
            "status": "proposed",
            "target_amount": "60000.00",
            "stretch_amount": "70000.00",
            "start_date": "",
            "end_date": "",
            "notes": "",
        })
        quota_plan_a.refresh_from_db()
        assert quota_plan_a.name == "Updated Q1 Plan"

    def test_delete_post_deletes(self, client_a, tenant_a):
        obj = QuotaPlan.objects.create(
            tenant=tenant_a, name="Delete QP", fiscal_year=2026,
        )
        client_a.post(reverse("territories:quotaplan_delete", args=[obj.pk]))
        assert not QuotaPlan.objects.filter(pk=obj.pk).exists()

    def test_detail_404_for_other_tenant(self, client_a, quota_plan_b):
        resp = client_a.get(reverse("territories:quotaplan_detail", args=[quota_plan_b.pk]))
        assert resp.status_code == 404

    def test_edit_404_for_other_tenant(self, client_a, quota_plan_b):
        resp = client_a.get(reverse("territories:quotaplan_edit", args=[quota_plan_b.pk]))
        assert resp.status_code == 404


# ============================================================ CoverageModel CRUD
@pytest.mark.django_db
class TestCoverageModelCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("territories:coveragemodel_list"))
        assert resp.status_code == 200

    def test_list_context_has_models(self, client_a, coverage_model_a):
        resp = client_a.get(reverse("territories:coveragemodel_list"))
        assert "models" in resp.context

    def test_list_seeded_model_appears(self, client_a, coverage_model_a):
        resp = client_a.get(reverse("territories:coveragemodel_list"))
        pks = [m.pk for m in resp.context["models"]]
        assert coverage_model_a.pk in pks

    def test_list_search_works(self, client_a, coverage_model_a):
        resp = client_a.get(reverse("territories:coveragemodel_list") + "?q=Direct")
        assert resp.status_code == 200
        pks = [m.pk for m in resp.context["models"]]
        assert coverage_model_a.pk in pks

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("territories:coveragemodel_create"))
        assert resp.status_code == 200

    def test_create_post_creates_model(self, client_a, tenant_a):
        before = CoverageModel.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("territories:coveragemodel_create"), {
            "name": "New Coverage Model",
            "model_type": "hybrid",
            "status": "proposed",
            "target_ratio": "30.00",
            "rep_capacity": 6,
            "coverage_score": "65.00",
            "description": "",
        })
        assert CoverageModel.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a):
        client_a.post(reverse("territories:coveragemodel_create"), {
            "name": "Tenant Check CM",
            "model_type": "partner",
            "status": "pilot",
            "target_ratio": "0.00",
            "rep_capacity": 0,
            "coverage_score": "0.00",
            "description": "check",
        })
        obj = CoverageModel.objects.filter(name="Tenant Check CM").first()
        assert obj is not None
        assert obj.tenant == tenant_a

    def test_detail_200(self, client_a, coverage_model_a):
        resp = client_a.get(reverse("territories:coveragemodel_detail", args=[coverage_model_a.pk]))
        assert resp.status_code == 200

    def test_edit_get_200(self, client_a, coverage_model_a):
        resp = client_a.get(reverse("territories:coveragemodel_edit", args=[coverage_model_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates(self, client_a, coverage_model_a):
        client_a.post(reverse("territories:coveragemodel_edit", args=[coverage_model_a.pk]), {
            "name": "Updated Direct Model",
            "model_type": "direct",
            "status": "adopted",
            "target_ratio": "55.00",
            "rep_capacity": 7,
            "coverage_score": "80.00",
            "description": "Updated",
        })
        coverage_model_a.refresh_from_db()
        assert coverage_model_a.name == "Updated Direct Model"

    def test_delete_post_deletes(self, client_a, tenant_a):
        obj = CoverageModel.objects.create(
            tenant=tenant_a, name="Delete CM", model_type="direct",
        )
        client_a.post(reverse("territories:coveragemodel_delete", args=[obj.pk]))
        assert not CoverageModel.objects.filter(pk=obj.pk).exists()

    def test_detail_404_for_other_tenant(self, client_a, coverage_model_b):
        resp = client_a.get(
            reverse("territories:coveragemodel_detail", args=[coverage_model_b.pk])
        )
        assert resp.status_code == 404

    def test_edit_404_for_other_tenant(self, client_a, coverage_model_b):
        resp = client_a.get(
            reverse("territories:coveragemodel_edit", args=[coverage_model_b.pk])
        )
        assert resp.status_code == 404


# ============================================================ TerritoryPerformance CRUD
@pytest.mark.django_db
class TestTerritoryPerformanceCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("territories:territoryperformance_list"))
        assert resp.status_code == 200

    def test_list_context_has_snapshots(self, client_a, performance_a):
        resp = client_a.get(reverse("territories:territoryperformance_list"))
        assert "snapshots" in resp.context

    def test_list_seeded_snapshot_appears(self, client_a, performance_a):
        resp = client_a.get(reverse("territories:territoryperformance_list"))
        pks = [s.pk for s in resp.context["snapshots"]]
        assert performance_a.pk in pks

    def test_list_search_works(self, client_a, performance_a):
        resp = client_a.get(reverse("territories:territoryperformance_list") + "?q=Q1 2026")
        assert resp.status_code == 200
        pks = [s.pk for s in resp.context["snapshots"]]
        assert performance_a.pk in pks

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("territories:territoryperformance_create"))
        assert resp.status_code == 200

    def test_create_post_creates_snapshot(self, client_a, tenant_a, territory_a):
        before = TerritoryPerformance.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("territories:territoryperformance_create"), {
            "territory": territory_a.pk,
            "period_type": "monthly",
            "period_label": "Jan 2026",
            "rating": "on_track",
            "quota_amount": "10000.00",
            "actual_amount": "9500.00",
            "pipeline_amount": "12000.00",
            "deals_won": 3,
            "period_end": "",
        })
        assert TerritoryPerformance.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a, territory_a):
        client_a.post(reverse("territories:territoryperformance_create"), {
            "territory": territory_a.pk,
            "period_type": "quarterly",
            "period_label": "Tenant Check Q",
            "rating": "exceeding",
            "quota_amount": "0.00",
            "actual_amount": "0.00",
            "pipeline_amount": "0.00",
            "deals_won": 0,
            "period_end": "",
        })
        obj = TerritoryPerformance.objects.filter(period_label="Tenant Check Q").first()
        assert obj is not None
        assert obj.tenant == tenant_a

    def test_detail_200(self, client_a, performance_a):
        resp = client_a.get(
            reverse("territories:territoryperformance_detail", args=[performance_a.pk])
        )
        assert resp.status_code == 200

    def test_edit_get_200(self, client_a, performance_a):
        resp = client_a.get(
            reverse("territories:territoryperformance_edit", args=[performance_a.pk])
        )
        assert resp.status_code == 200

    def test_edit_post_updates(self, client_a, performance_a, territory_a):
        client_a.post(
            reverse("territories:territoryperformance_edit", args=[performance_a.pk]),
            {
                "territory": territory_a.pk,
                "period_type": "quarterly",
                "period_label": "Q1 2026 Updated",
                "rating": "exceeding",
                "quota_amount": "50000.00",
                "actual_amount": "55000.00",
                "pipeline_amount": "65000.00",
                "deals_won": 7,
                "period_end": "",
            },
        )
        performance_a.refresh_from_db()
        assert performance_a.period_label == "Q1 2026 Updated"

    def test_delete_post_deletes(self, client_a, tenant_a, territory_a):
        obj = TerritoryPerformance.objects.create(
            tenant=tenant_a, territory=territory_a,
            period_type=TerritoryPerformance.PERIOD_MONTHLY,
        )
        client_a.post(reverse("territories:territoryperformance_delete", args=[obj.pk]))
        assert not TerritoryPerformance.objects.filter(pk=obj.pk).exists()

    def test_detail_404_for_other_tenant(self, client_a, performance_b):
        resp = client_a.get(
            reverse("territories:territoryperformance_detail", args=[performance_b.pk])
        )
        assert resp.status_code == 404

    def test_edit_404_for_other_tenant(self, client_a, performance_b):
        resp = client_a.get(
            reverse("territories:territoryperformance_edit", args=[performance_b.pk])
        )
        assert resp.status_code == 404
