"""Tests for forecasting.forms: required fields, field exclusions, tenant-scoped FK querysets."""
import pytest
from django.utils import timezone

from apps.forecasting.forms import (
    ForecastAccuracyForm, ForecastAdjustmentForm, ForecastCategoryForm,
    ForecastForm, QuotaForm,
)
from apps.forecasting.models import Forecast, ForecastCategory


# ============================================================ ForecastCategoryForm
@pytest.mark.django_db
class TestForecastCategoryForm:
    def test_valid_form(self):
        form = ForecastCategoryForm(data={
            "name": "Pipeline",
            "commitment": "pipeline",
            "probability": 40,
            "weight": "1.00",
            "is_active": True,
            "description": "Test description",
        })
        assert form.is_valid(), form.errors

    def test_missing_name_invalid(self):
        form = ForecastCategoryForm(data={
            "commitment": "pipeline",
            "probability": 40,
            "weight": "1.00",
            "is_active": True,
        })
        assert not form.is_valid()
        assert "name" in form.errors

    def test_invalid_commitment_choice_invalid(self):
        form = ForecastCategoryForm(data={
            "name": "Bad Commit",
            "commitment": "nonexistent",
            "probability": 40,
            "weight": "1.00",
        })
        assert not form.is_valid()

    def test_tenant_not_in_form_fields(self):
        form = ForecastCategoryForm()
        assert "tenant" not in form.fields

    def test_created_at_not_in_form_fields(self):
        form = ForecastCategoryForm()
        assert "created_at" not in form.fields

    def test_updated_at_not_in_form_fields(self):
        form = ForecastCategoryForm()
        assert "updated_at" not in form.fields

    def test_all_expected_fields_present(self):
        form = ForecastCategoryForm()
        expected = {"name", "commitment", "probability", "weight", "is_active", "description"}
        assert expected.issubset(set(form.fields.keys()))


# ============================================================ ForecastForm
@pytest.mark.django_db
class TestForecastForm:
    def test_valid_form_minimal(self, tenant_a):
        form = ForecastForm(data={
            "category": "",
            "name": "Q3 Forecast",
            "owner_name": "Alice",
            "period_type": "quarter",
            "period_label": "Q3 2026",
            "period_start": "",
            "period_end": "",
            "pipeline_amount": "100000.00",
            "commit_amount": "60000.00",
            "best_case_amount": "80000.00",
            "ai_predicted_amount": "65000.00",
            "ai_confidence": "medium",
            "status": "draft",
            "notes": "",
        }, tenant=tenant_a)
        assert form.is_valid(), form.errors

    def test_missing_name_invalid(self, tenant_a):
        form = ForecastForm(data={
            "period_type": "quarter",
            "status": "draft",
        }, tenant=tenant_a)
        assert not form.is_valid()
        assert "name" in form.errors

    def test_number_not_in_form_fields(self, tenant_a):
        form = ForecastForm(tenant=tenant_a)
        assert "number" not in form.fields

    def test_tenant_not_in_form_fields(self, tenant_a):
        form = ForecastForm(tenant=tenant_a)
        assert "tenant" not in form.fields

    def test_submitted_at_not_in_form_fields(self, tenant_a):
        """submitted_at is system-set, not a form field."""
        form = ForecastForm(tenant=tenant_a)
        assert "submitted_at" not in form.fields

    def test_category_queryset_scoped_to_tenant(self, tenant_a, tenant_b, category_a, category_b):
        form = ForecastForm(tenant=tenant_a)
        cat_pks = [c.pk for c in form.fields["category"].queryset]
        assert category_a.pk in cat_pks
        assert category_b.pk not in cat_pks

    def test_category_queryset_empty_when_no_tenant(self):
        """No tenant passed -> queryset is empty (no cross-tenant leak)."""
        form = ForecastForm(tenant=None)
        assert form.fields["category"].queryset.count() == 0

    def test_category_not_required(self, tenant_a):
        form = ForecastForm(tenant=tenant_a)
        assert form.fields["category"].required is False

    def test_invalid_status_choice_invalid(self, tenant_a):
        form = ForecastForm(data={
            "name": "Bad Status",
            "period_type": "quarter",
            "status": "nonexistent_status",
        }, tenant=tenant_a)
        assert not form.is_valid()


# ============================================================ QuotaForm
@pytest.mark.django_db
class TestQuotaForm:
    def test_valid_form(self):
        form = QuotaForm(data={
            "owner_name": "Alice",
            "period_type": "quarter",
            "period_label": "Q3 2026",
            "period_start": "",
            "period_end": "",
            "target_amount": "150000.00",
            "attained_amount": "75000.00",
            "status": "active",
            "notes": "",
        })
        assert form.is_valid(), form.errors

    def test_missing_owner_name_invalid(self):
        form = QuotaForm(data={
            "period_type": "quarter",
            "target_amount": "100000.00",
            "status": "active",
        })
        assert not form.is_valid()
        assert "owner_name" in form.errors

    def test_tenant_not_in_form_fields(self):
        form = QuotaForm()
        assert "tenant" not in form.fields

    def test_created_at_not_in_form_fields(self):
        form = QuotaForm()
        assert "created_at" not in form.fields

    def test_all_expected_fields_present(self):
        form = QuotaForm()
        expected = {
            "owner_name", "period_type", "period_label", "period_start", "period_end",
            "target_amount", "attained_amount", "status", "notes",
        }
        assert expected.issubset(set(form.fields.keys()))

    def test_invalid_status_choice_invalid(self):
        form = QuotaForm(data={
            "owner_name": "Alice",
            "period_type": "quarter",
            "target_amount": "100000.00",
            "status": "INVALID",
        })
        assert not form.is_valid()


# ============================================================ ForecastAdjustmentForm
@pytest.mark.django_db
class TestForecastAdjustmentForm:
    def test_valid_form(self, tenant_a, forecast_a):
        form = ForecastAdjustmentForm(data={
            "forecast": forecast_a.pk,
            "adjustment_type": "uplift",
            "amount": "5000.00",
            "adjusted_by": "Manager Alice",
            "status": "pending",
            "reason": "Good pipeline",
        }, tenant=tenant_a)
        assert form.is_valid(), form.errors

    def test_missing_forecast_invalid(self, tenant_a):
        form = ForecastAdjustmentForm(data={
            "adjustment_type": "uplift",
            "amount": "5000.00",
            "status": "pending",
        }, tenant=tenant_a)
        assert not form.is_valid()

    def test_tenant_not_in_form_fields(self, tenant_a):
        form = ForecastAdjustmentForm(tenant=tenant_a)
        assert "tenant" not in form.fields

    def test_approved_at_not_in_form_fields(self, tenant_a):
        """approved_at is system-set, not a form field."""
        form = ForecastAdjustmentForm(tenant=tenant_a)
        assert "approved_at" not in form.fields

    def test_forecast_queryset_scoped_to_tenant(self, tenant_a, tenant_b, forecast_a, forecast_b):
        form = ForecastAdjustmentForm(tenant=tenant_a)
        forecast_pks = [f.pk for f in form.fields["forecast"].queryset]
        assert forecast_a.pk in forecast_pks
        assert forecast_b.pk not in forecast_pks

    def test_forecast_queryset_empty_when_no_tenant(self):
        """No tenant -> queryset is empty (no cross-tenant leak)."""
        form = ForecastAdjustmentForm(tenant=None)
        assert form.fields["forecast"].queryset.count() == 0

    def test_invalid_adjustment_type_invalid(self, tenant_a, forecast_a):
        form = ForecastAdjustmentForm(data={
            "forecast": forecast_a.pk,
            "adjustment_type": "INVALID",
            "amount": "1000.00",
            "status": "pending",
        }, tenant=tenant_a)
        assert not form.is_valid()

    def test_all_expected_fields_present(self, tenant_a):
        form = ForecastAdjustmentForm(tenant=tenant_a)
        expected = {"forecast", "adjustment_type", "amount", "adjusted_by", "status", "reason"}
        assert expected.issubset(set(form.fields.keys()))


# ============================================================ ForecastAccuracyForm
@pytest.mark.django_db
class TestForecastAccuracyForm:
    def test_valid_form(self, tenant_a, forecast_a):
        today = timezone.localdate().isoformat()
        form = ForecastAccuracyForm(data={
            "forecast": forecast_a.pk,
            "period_label": "Q2 2026",
            "forecasted_amount": "100000.00",
            "actual_amount": "95000.00",
            "accuracy_pct": "95.00",
            "grade": "excellent",
            "analyzed_on": today,
            "notes": "",
        }, tenant=tenant_a)
        assert form.is_valid(), form.errors

    def test_valid_form_without_forecast(self, tenant_a):
        today = timezone.localdate().isoformat()
        form = ForecastAccuracyForm(data={
            "forecast": "",
            "period_label": "Q2 2026",
            "forecasted_amount": "100000.00",
            "actual_amount": "90000.00",
            "accuracy_pct": "90.00",
            "grade": "good",
            "analyzed_on": today,
            "notes": "",
        }, tenant=tenant_a)
        assert form.is_valid(), form.errors

    def test_tenant_not_in_form_fields(self, tenant_a):
        form = ForecastAccuracyForm(tenant=tenant_a)
        assert "tenant" not in form.fields

    def test_variance_amount_not_in_form_fields(self, tenant_a):
        """variance_amount is system-computed, not a form field."""
        form = ForecastAccuracyForm(tenant=tenant_a)
        assert "variance_amount" not in form.fields

    def test_forecast_queryset_scoped_to_tenant(self, tenant_a, tenant_b, forecast_a, forecast_b):
        form = ForecastAccuracyForm(tenant=tenant_a)
        forecast_pks = [f.pk for f in form.fields["forecast"].queryset]
        assert forecast_a.pk in forecast_pks
        assert forecast_b.pk not in forecast_pks

    def test_forecast_queryset_empty_when_no_tenant(self):
        """No tenant -> queryset is empty (no cross-tenant leak)."""
        form = ForecastAccuracyForm(tenant=None)
        assert form.fields["forecast"].queryset.count() == 0

    def test_forecast_not_required(self, tenant_a):
        form = ForecastAccuracyForm(tenant=tenant_a)
        assert form.fields["forecast"].required is False

    def test_all_expected_fields_present(self, tenant_a):
        form = ForecastAccuracyForm(tenant=tenant_a)
        expected = {
            "forecast", "period_label", "forecasted_amount", "actual_amount",
            "accuracy_pct", "grade", "analyzed_on", "notes",
        }
        assert expected.issubset(set(form.fields.keys()))

    def test_invalid_grade_choice_invalid(self, tenant_a):
        today = timezone.localdate().isoformat()
        form = ForecastAccuracyForm(data={
            "forecast": "",
            "period_label": "Q1 2026",
            "forecasted_amount": "100000.00",
            "actual_amount": "90000.00",
            "accuracy_pct": "90.00",
            "grade": "INVALID_GRADE",
            "analyzed_on": today,
            "notes": "",
        }, tenant=tenant_a)
        assert not form.is_valid()
