"""Tests for forecasting views: CRUD for all forecasting models."""
from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.forecasting.models import (
    Forecast, ForecastAccuracy, ForecastAdjustment, ForecastCategory, Quota,
)


# ============================================================ ForecastCategory CRUD
@pytest.mark.django_db
class TestForecastCategoryCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("forecasting:forecastcategory_list"))
        assert resp.status_code == 200

    def test_list_context_has_categories(self, client_a, category_a):
        resp = client_a.get(reverse("forecasting:forecastcategory_list"))
        assert "categories" in resp.context
        pks = [c.pk for c in resp.context["categories"]]
        assert category_a.pk in pks

    def test_list_context_has_commit_choices(self, client_a):
        resp = client_a.get(reverse("forecasting:forecastcategory_list"))
        assert "commit_choices" in resp.context

    def test_list_context_has_total(self, client_a):
        resp = client_a.get(reverse("forecasting:forecastcategory_list"))
        assert "total" in resp.context

    def test_list_search_filters_results(self, client_a, category_a):
        resp = client_a.get(reverse("forecasting:forecastcategory_list") + "?q=Pipeline+A")
        pks = [c.pk for c in resp.context["categories"]]
        assert category_a.pk in pks

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("forecasting:forecastcategory_create"))
        assert resp.status_code == 200

    def test_create_post_creates_object(self, client_a, tenant_a):
        before = ForecastCategory.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("forecasting:forecastcategory_create"), {
            "name": "New Cat",
            "commitment": "best_case",
            "probability": 60,
            "weight": "1.00",
            "is_active": True,
            "description": "",
        })
        assert ForecastCategory.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_post_assigns_tenant(self, client_a, tenant_a):
        client_a.post(reverse("forecasting:forecastcategory_create"), {
            "name": "Tenant Cat",
            "commitment": "commit",
            "probability": 80,
            "weight": "1.00",
            "is_active": True,
            "description": "",
        })
        obj = ForecastCategory.objects.filter(tenant=tenant_a, name="Tenant Cat").first()
        assert obj is not None
        assert obj.tenant == tenant_a

    def test_create_post_redirects_on_success(self, client_a):
        resp = client_a.post(reverse("forecasting:forecastcategory_create"), {
            "name": "Redirect Cat",
            "commitment": "pipeline",
            "probability": 30,
            "weight": "1.00",
            "is_active": True,
            "description": "",
        })
        assert resp.status_code in (301, 302)

    def test_detail_200(self, client_a, category_a):
        resp = client_a.get(reverse("forecasting:forecastcategory_detail", args=[category_a.pk]))
        assert resp.status_code == 200

    def test_detail_context_has_obj(self, client_a, category_a):
        resp = client_a.get(reverse("forecasting:forecastcategory_detail", args=[category_a.pk]))
        assert "obj" in resp.context
        assert resp.context["obj"].pk == category_a.pk

    def test_edit_get_200(self, client_a, category_a):
        resp = client_a.get(reverse("forecasting:forecastcategory_edit", args=[category_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_object(self, client_a, category_a):
        client_a.post(reverse("forecasting:forecastcategory_edit", args=[category_a.pk]), {
            "name": "Updated Cat",
            "commitment": "closed",
            "probability": 90,
            "weight": "1.00",
            "is_active": True,
            "description": "Updated",
        })
        category_a.refresh_from_db()
        assert category_a.name == "Updated Cat"

    def test_delete_post_removes_object(self, client_a, tenant_a):
        cat = ForecastCategory.objects.create(tenant=tenant_a, name="ToDelete")
        client_a.post(reverse("forecasting:forecastcategory_delete", args=[cat.pk]))
        assert not ForecastCategory.objects.filter(pk=cat.pk).exists()

    def test_delete_post_redirects(self, client_a, tenant_a):
        cat = ForecastCategory.objects.create(tenant=tenant_a, name="ToDelete2")
        resp = client_a.post(reverse("forecasting:forecastcategory_delete", args=[cat.pk]))
        assert resp.status_code in (301, 302)

    def test_detail_404_for_other_tenant(self, client_a, category_b):
        resp = client_a.get(reverse("forecasting:forecastcategory_detail", args=[category_b.pk]))
        assert resp.status_code == 404

    def test_edit_404_for_other_tenant(self, client_a, category_b):
        resp = client_a.get(reverse("forecasting:forecastcategory_edit", args=[category_b.pk]))
        assert resp.status_code == 404

    def test_delete_404_for_other_tenant(self, client_a, category_b):
        resp = client_a.post(reverse("forecasting:forecastcategory_delete", args=[category_b.pk]))
        assert resp.status_code == 404


# ============================================================ Forecast CRUD
@pytest.mark.django_db
class TestForecastCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("forecasting:forecast_list"))
        assert resp.status_code == 200

    def test_list_context_has_forecasts(self, client_a, forecast_a):
        resp = client_a.get(reverse("forecasting:forecast_list"))
        assert "forecasts" in resp.context
        pks = [f.pk for f in resp.context["forecasts"]]
        assert forecast_a.pk in pks

    def test_list_context_has_status_choices(self, client_a):
        resp = client_a.get(reverse("forecasting:forecast_list"))
        assert "status_choices" in resp.context

    def test_list_context_has_period_choices(self, client_a):
        resp = client_a.get(reverse("forecasting:forecast_list"))
        assert "period_choices" in resp.context

    def test_list_context_has_categories(self, client_a):
        resp = client_a.get(reverse("forecasting:forecast_list"))
        assert "categories" in resp.context

    def test_list_context_has_total(self, client_a):
        resp = client_a.get(reverse("forecasting:forecast_list"))
        assert "total" in resp.context

    def test_list_filter_by_status(self, client_a, forecast_a):
        resp = client_a.get(reverse("forecasting:forecast_list") + "?status=draft")
        pks = [f.pk for f in resp.context["forecasts"]]
        assert forecast_a.pk in pks

    def test_list_filter_by_period_type(self, client_a, forecast_a):
        resp = client_a.get(reverse("forecasting:forecast_list") + "?period_type=quarter")
        pks = [f.pk for f in resp.context["forecasts"]]
        assert forecast_a.pk in pks

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("forecasting:forecast_create"))
        assert resp.status_code == 200

    def test_create_post_creates_object(self, client_a, tenant_a):
        before = Forecast.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("forecasting:forecast_create"), {
            "category": "",
            "name": "New Forecast",
            "owner_name": "Alice",
            "period_type": "quarter",
            "period_label": "Q4 2026",
            "period_start": "",
            "period_end": "",
            "pipeline_amount": "50000.00",
            "commit_amount": "30000.00",
            "best_case_amount": "40000.00",
            "ai_predicted_amount": "32000.00",
            "ai_confidence": "medium",
            "status": "draft",
            "notes": "",
        })
        assert Forecast.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_post_assigns_tenant(self, client_a, tenant_a):
        client_a.post(reverse("forecasting:forecast_create"), {
            "category": "",
            "name": "Tenant Forecast",
            "owner_name": "Bob",
            "period_type": "month",
            "period_label": "Jan 2027",
            "period_start": "",
            "period_end": "",
            "pipeline_amount": "20000.00",
            "commit_amount": "10000.00",
            "best_case_amount": "15000.00",
            "ai_predicted_amount": "11000.00",
            "ai_confidence": "low",
            "status": "draft",
            "notes": "",
        })
        obj = Forecast.objects.filter(tenant=tenant_a, name="Tenant Forecast").first()
        assert obj is not None
        assert obj.tenant == tenant_a

    def test_create_post_auto_numbers(self, client_a, tenant_a):
        Forecast.objects.filter(tenant=tenant_a).delete()
        client_a.post(reverse("forecasting:forecast_create"), {
            "category": "",
            "name": "Auto Num Forecast",
            "owner_name": "Charlie",
            "period_type": "year",
            "period_label": "FY 2027",
            "period_start": "",
            "period_end": "",
            "pipeline_amount": "500000.00",
            "commit_amount": "300000.00",
            "best_case_amount": "400000.00",
            "ai_predicted_amount": "320000.00",
            "ai_confidence": "high",
            "status": "draft",
            "notes": "",
        })
        obj = Forecast.objects.filter(tenant=tenant_a, name="Auto Num Forecast").first()
        assert obj is not None
        assert obj.number.startswith("FCT-")

    def test_detail_200(self, client_a, forecast_a):
        resp = client_a.get(reverse("forecasting:forecast_detail", args=[forecast_a.pk]))
        assert resp.status_code == 200

    def test_detail_context_has_obj(self, client_a, forecast_a):
        resp = client_a.get(reverse("forecasting:forecast_detail", args=[forecast_a.pk]))
        assert "obj" in resp.context
        assert resp.context["obj"].pk == forecast_a.pk

    def test_detail_context_has_adjustments(self, client_a, forecast_a):
        resp = client_a.get(reverse("forecasting:forecast_detail", args=[forecast_a.pk]))
        assert "adjustments" in resp.context

    def test_edit_get_200(self, client_a, forecast_a):
        resp = client_a.get(reverse("forecasting:forecast_edit", args=[forecast_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_object(self, client_a, forecast_a):
        client_a.post(reverse("forecasting:forecast_edit", args=[forecast_a.pk]), {
            "category": "",
            "name": "Updated Forecast",
            "owner_name": "Updated Owner",
            "period_type": "month",
            "period_label": "Updated Period",
            "period_start": "",
            "period_end": "",
            "pipeline_amount": "200000.00",
            "commit_amount": "120000.00",
            "best_case_amount": "160000.00",
            "ai_predicted_amount": "125000.00",
            "ai_confidence": "high",
            "status": "submitted",
            "notes": "Updated notes",
        })
        forecast_a.refresh_from_db()
        assert forecast_a.name == "Updated Forecast"

    def test_delete_post_removes_object(self, client_a, tenant_a, category_a):
        fc = Forecast.objects.create(tenant=tenant_a, name="ToDelete Forecast")
        client_a.post(reverse("forecasting:forecast_delete", args=[fc.pk]))
        assert not Forecast.objects.filter(pk=fc.pk).exists()

    def test_detail_404_for_other_tenant(self, client_a, forecast_b):
        resp = client_a.get(reverse("forecasting:forecast_detail", args=[forecast_b.pk]))
        assert resp.status_code == 404

    def test_edit_404_for_other_tenant(self, client_a, forecast_b):
        resp = client_a.get(reverse("forecasting:forecast_edit", args=[forecast_b.pk]))
        assert resp.status_code == 404

    def test_delete_404_for_other_tenant(self, client_a, forecast_b):
        resp = client_a.post(reverse("forecasting:forecast_delete", args=[forecast_b.pk]))
        assert resp.status_code == 404


# ============================================================ Quota CRUD
@pytest.mark.django_db
class TestQuotaCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("forecasting:quota_list"))
        assert resp.status_code == 200

    def test_list_context_has_quotas(self, client_a, quota_a):
        resp = client_a.get(reverse("forecasting:quota_list"))
        assert "quotas" in resp.context
        pks = [q.pk for q in resp.context["quotas"]]
        assert quota_a.pk in pks

    def test_list_context_has_status_choices(self, client_a):
        resp = client_a.get(reverse("forecasting:quota_list"))
        assert "status_choices" in resp.context

    def test_list_context_has_period_choices(self, client_a):
        resp = client_a.get(reverse("forecasting:quota_list"))
        assert "period_choices" in resp.context

    def test_list_context_has_total(self, client_a):
        resp = client_a.get(reverse("forecasting:quota_list"))
        assert "total" in resp.context

    def test_list_search_filters_by_owner(self, client_a, quota_a):
        resp = client_a.get(reverse("forecasting:quota_list") + "?q=Alice")
        pks = [q.pk for q in resp.context["quotas"]]
        assert quota_a.pk in pks

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("forecasting:quota_create"))
        assert resp.status_code == 200

    def test_create_post_creates_object(self, client_a, tenant_a):
        before = Quota.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("forecasting:quota_create"), {
            "owner_name": "New Rep",
            "period_type": "month",
            "period_label": "July 2026",
            "period_start": "",
            "period_end": "",
            "target_amount": "50000.00",
            "attained_amount": "0.00",
            "status": "active",
            "notes": "",
        })
        assert Quota.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_post_assigns_tenant(self, client_a, tenant_a):
        client_a.post(reverse("forecasting:quota_create"), {
            "owner_name": "Tenant Rep",
            "period_type": "year",
            "period_label": "FY 2027",
            "period_start": "",
            "period_end": "",
            "target_amount": "1000000.00",
            "attained_amount": "0.00",
            "status": "active",
            "notes": "",
        })
        obj = Quota.objects.filter(tenant=tenant_a, owner_name="Tenant Rep").first()
        assert obj is not None
        assert obj.tenant == tenant_a

    def test_detail_200(self, client_a, quota_a):
        resp = client_a.get(reverse("forecasting:quota_detail", args=[quota_a.pk]))
        assert resp.status_code == 200

    def test_detail_context_has_obj(self, client_a, quota_a):
        resp = client_a.get(reverse("forecasting:quota_detail", args=[quota_a.pk]))
        assert "obj" in resp.context
        assert resp.context["obj"].pk == quota_a.pk

    def test_edit_get_200(self, client_a, quota_a):
        resp = client_a.get(reverse("forecasting:quota_edit", args=[quota_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_object(self, client_a, quota_a):
        client_a.post(reverse("forecasting:quota_edit", args=[quota_a.pk]), {
            "owner_name": "Updated Alice",
            "period_type": "quarter",
            "period_label": "Q4 2026",
            "period_start": "",
            "period_end": "",
            "target_amount": "200000.00",
            "attained_amount": "100000.00",
            "status": "active",
            "notes": "updated",
        })
        quota_a.refresh_from_db()
        assert quota_a.owner_name == "Updated Alice"

    def test_delete_post_removes_object(self, client_a, tenant_a):
        q = Quota.objects.create(tenant=tenant_a, owner_name="ToDelete", target_amount="10000.00")
        client_a.post(reverse("forecasting:quota_delete", args=[q.pk]))
        assert not Quota.objects.filter(pk=q.pk).exists()

    def test_detail_404_for_other_tenant(self, client_a, quota_b):
        resp = client_a.get(reverse("forecasting:quota_detail", args=[quota_b.pk]))
        assert resp.status_code == 404

    def test_edit_404_for_other_tenant(self, client_a, quota_b):
        resp = client_a.get(reverse("forecasting:quota_edit", args=[quota_b.pk]))
        assert resp.status_code == 404

    def test_delete_404_for_other_tenant(self, client_a, quota_b):
        resp = client_a.post(reverse("forecasting:quota_delete", args=[quota_b.pk]))
        assert resp.status_code == 404


# ============================================================ ForecastAdjustment CRUD
@pytest.mark.django_db
class TestForecastAdjustmentCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("forecasting:forecastadjustment_list"))
        assert resp.status_code == 200

    def test_list_context_has_adjustments(self, client_a, adjustment_a):
        resp = client_a.get(reverse("forecasting:forecastadjustment_list"))
        assert "adjustments" in resp.context
        pks = [a.pk for a in resp.context["adjustments"]]
        assert adjustment_a.pk in pks

    def test_list_context_has_status_choices(self, client_a):
        resp = client_a.get(reverse("forecasting:forecastadjustment_list"))
        assert "status_choices" in resp.context

    def test_list_context_has_type_choices(self, client_a):
        resp = client_a.get(reverse("forecasting:forecastadjustment_list"))
        assert "type_choices" in resp.context

    def test_list_context_has_total(self, client_a):
        resp = client_a.get(reverse("forecasting:forecastadjustment_list"))
        assert "total" in resp.context

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("forecasting:forecastadjustment_create"))
        assert resp.status_code == 200

    def test_create_post_creates_object(self, client_a, tenant_a, forecast_a):
        before = ForecastAdjustment.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("forecasting:forecastadjustment_create"), {
            "forecast": forecast_a.pk,
            "adjustment_type": "haircut",
            "amount": "-5000.00",
            "adjusted_by": "Director",
            "status": "pending",
            "reason": "Conservatism",
        })
        assert ForecastAdjustment.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_post_assigns_tenant(self, client_a, tenant_a, forecast_a):
        client_a.post(reverse("forecasting:forecastadjustment_create"), {
            "forecast": forecast_a.pk,
            "adjustment_type": "override",
            "amount": "10000.00",
            "adjusted_by": "VP Sales",
            "status": "pending",
            "reason": "Board decision",
        })
        obj = ForecastAdjustment.objects.filter(tenant=tenant_a, adjusted_by="VP Sales").first()
        assert obj is not None
        assert obj.tenant == tenant_a

    def test_detail_200(self, client_a, adjustment_a):
        resp = client_a.get(reverse("forecasting:forecastadjustment_detail", args=[adjustment_a.pk]))
        assert resp.status_code == 200

    def test_detail_context_has_obj(self, client_a, adjustment_a):
        resp = client_a.get(reverse("forecasting:forecastadjustment_detail", args=[adjustment_a.pk]))
        assert "obj" in resp.context
        assert resp.context["obj"].pk == adjustment_a.pk

    def test_edit_get_200(self, client_a, adjustment_a):
        resp = client_a.get(reverse("forecasting:forecastadjustment_edit", args=[adjustment_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_object(self, client_a, adjustment_a, forecast_a):
        client_a.post(reverse("forecasting:forecastadjustment_edit", args=[adjustment_a.pk]), {
            "forecast": forecast_a.pk,
            "adjustment_type": "rollup",
            "amount": "8000.00",
            "adjusted_by": "Updated Manager",
            "status": "approved",
            "reason": "Updated reason",
        })
        adjustment_a.refresh_from_db()
        assert adjustment_a.adjusted_by == "Updated Manager"

    def test_delete_post_removes_object(self, client_a, tenant_a, forecast_a):
        adj = ForecastAdjustment.objects.create(
            tenant=tenant_a, forecast=forecast_a, amount="1000.00"
        )
        client_a.post(reverse("forecasting:forecastadjustment_delete", args=[adj.pk]))
        assert not ForecastAdjustment.objects.filter(pk=adj.pk).exists()

    def test_detail_404_for_other_tenant(self, client_a, adjustment_b):
        resp = client_a.get(reverse("forecasting:forecastadjustment_detail", args=[adjustment_b.pk]))
        assert resp.status_code == 404

    def test_edit_404_for_other_tenant(self, client_a, adjustment_b):
        resp = client_a.get(reverse("forecasting:forecastadjustment_edit", args=[adjustment_b.pk]))
        assert resp.status_code == 404

    def test_delete_404_for_other_tenant(self, client_a, adjustment_b):
        resp = client_a.post(reverse("forecasting:forecastadjustment_delete", args=[adjustment_b.pk]))
        assert resp.status_code == 404


# ============================================================ ForecastAccuracy CRUD
@pytest.mark.django_db
class TestForecastAccuracyCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("forecasting:forecastaccuracy_list"))
        assert resp.status_code == 200

    def test_list_context_has_records(self, client_a, accuracy_a):
        resp = client_a.get(reverse("forecasting:forecastaccuracy_list"))
        assert "records" in resp.context
        pks = [r.pk for r in resp.context["records"]]
        assert accuracy_a.pk in pks

    def test_list_context_has_grade_choices(self, client_a):
        resp = client_a.get(reverse("forecasting:forecastaccuracy_list"))
        assert "grade_choices" in resp.context

    def test_list_context_has_total(self, client_a):
        resp = client_a.get(reverse("forecasting:forecastaccuracy_list"))
        assert "total" in resp.context

    def test_list_filter_by_grade(self, client_a, accuracy_a):
        resp = client_a.get(reverse("forecasting:forecastaccuracy_list") + "?grade=excellent")
        pks = [r.pk for r in resp.context["records"]]
        assert accuracy_a.pk in pks

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("forecasting:forecastaccuracy_create"))
        assert resp.status_code == 200

    def test_create_post_creates_object(self, client_a, tenant_a, forecast_a):
        before = ForecastAccuracy.objects.filter(tenant=tenant_a).count()
        today = timezone.localdate().isoformat()
        client_a.post(reverse("forecasting:forecastaccuracy_create"), {
            "forecast": forecast_a.pk,
            "period_label": "Q1 2026",
            "forecasted_amount": "120000.00",
            "actual_amount": "110000.00",
            "accuracy_pct": "91.67",
            "grade": "good",
            "analyzed_on": today,
            "notes": "",
        })
        assert ForecastAccuracy.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_post_assigns_tenant(self, client_a, tenant_a, forecast_a):
        today = timezone.localdate().isoformat()
        client_a.post(reverse("forecasting:forecastaccuracy_create"), {
            "forecast": forecast_a.pk,
            "period_label": "Q1 2026 T",
            "forecasted_amount": "80000.00",
            "actual_amount": "75000.00",
            "accuracy_pct": "93.75",
            "grade": "excellent",
            "analyzed_on": today,
            "notes": "tenant check",
        })
        obj = ForecastAccuracy.objects.filter(tenant=tenant_a, notes="tenant check").first()
        assert obj is not None
        assert obj.tenant == tenant_a

    def test_create_post_computes_variance(self, client_a, tenant_a, forecast_a):
        today = timezone.localdate().isoformat()
        client_a.post(reverse("forecasting:forecastaccuracy_create"), {
            "forecast": forecast_a.pk,
            "period_label": "Q3 2026 Var",
            "forecasted_amount": "100000.00",
            "actual_amount": "90000.00",
            "accuracy_pct": "90.00",
            "grade": "good",
            "analyzed_on": today,
            "notes": "variance check",
        })
        obj = ForecastAccuracy.objects.filter(tenant=tenant_a, notes="variance check").first()
        assert obj is not None
        assert obj.variance_amount == -10000

    def test_detail_200(self, client_a, accuracy_a):
        resp = client_a.get(reverse("forecasting:forecastaccuracy_detail", args=[accuracy_a.pk]))
        assert resp.status_code == 200

    def test_detail_context_has_obj(self, client_a, accuracy_a):
        resp = client_a.get(reverse("forecasting:forecastaccuracy_detail", args=[accuracy_a.pk]))
        assert "obj" in resp.context
        assert resp.context["obj"].pk == accuracy_a.pk

    def test_edit_get_200(self, client_a, accuracy_a):
        resp = client_a.get(reverse("forecasting:forecastaccuracy_edit", args=[accuracy_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_object(self, client_a, accuracy_a, forecast_a):
        today = timezone.localdate().isoformat()
        client_a.post(reverse("forecasting:forecastaccuracy_edit", args=[accuracy_a.pk]), {
            "forecast": forecast_a.pk,
            "period_label": "Q2 2026 Updated",
            "forecasted_amount": "110000.00",
            "actual_amount": "105000.00",
            "accuracy_pct": "95.45",
            "grade": "excellent",
            "analyzed_on": today,
            "notes": "updated notes",
        })
        accuracy_a.refresh_from_db()
        assert accuracy_a.period_label == "Q2 2026 Updated"

    def test_delete_post_removes_object(self, client_a, tenant_a, forecast_a):
        acc = ForecastAccuracy.objects.create(
            tenant=tenant_a,
            forecast=forecast_a,
            period_label="Q4 Delete",
            forecasted_amount=Decimal("50000.00"),
            actual_amount=Decimal("45000.00"),
            accuracy_pct=Decimal("90.00"),
        )
        client_a.post(reverse("forecasting:forecastaccuracy_delete", args=[acc.pk]))
        assert not ForecastAccuracy.objects.filter(pk=acc.pk).exists()

    def test_detail_404_for_other_tenant(self, client_a, accuracy_b):
        resp = client_a.get(reverse("forecasting:forecastaccuracy_detail", args=[accuracy_b.pk]))
        assert resp.status_code == 404

    def test_edit_404_for_other_tenant(self, client_a, accuracy_b):
        resp = client_a.get(reverse("forecasting:forecastaccuracy_edit", args=[accuracy_b.pk]))
        assert resp.status_code == 404

    def test_delete_404_for_other_tenant(self, client_a, accuracy_b):
        resp = client_a.post(reverse("forecasting:forecastaccuracy_delete", args=[accuracy_b.pk]))
        assert resp.status_code == 404
