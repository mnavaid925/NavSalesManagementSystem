"""Tests for forecasting.models: ForecastCategory, Forecast, Quota, ForecastAdjustment, ForecastAccuracy."""
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.forecasting.models import (
    Forecast, ForecastAccuracy, ForecastAdjustment, ForecastCategory, Quota,
)


# ============================================================ ForecastCategory
@pytest.mark.django_db
class TestForecastCategory:
    def test_str_returns_name(self, category_a):
        assert str(category_a) == "Pipeline A"

    def test_default_commitment_is_pipeline(self, tenant_a):
        cat = ForecastCategory.objects.create(tenant=tenant_a, name="My Cat")
        assert cat.commitment == ForecastCategory.COMMIT_PIPELINE

    def test_default_probability_is_50(self, tenant_a):
        cat = ForecastCategory.objects.create(tenant=tenant_a, name="Cat50")
        assert cat.probability == 50

    def test_default_weight_is_1(self, tenant_a):
        cat = ForecastCategory.objects.create(tenant=tenant_a, name="CatW")
        assert cat.weight == 1

    def test_default_is_active_true(self, tenant_a):
        cat = ForecastCategory.objects.create(tenant=tenant_a, name="CatActive")
        assert cat.is_active is True

    def test_commit_choices_contain_all_five(self):
        choices = dict(ForecastCategory.COMMIT_CHOICES)
        assert ForecastCategory.COMMIT_OMITTED in choices
        assert ForecastCategory.COMMIT_PIPELINE in choices
        assert ForecastCategory.COMMIT_BEST_CASE in choices
        assert ForecastCategory.COMMIT_COMMIT in choices
        assert ForecastCategory.COMMIT_CLOSED in choices

    def test_ordering_by_name(self, tenant_a):
        ForecastCategory.objects.create(tenant=tenant_a, name="Zebra")
        ForecastCategory.objects.create(tenant=tenant_a, name="Alpha")
        names = list(ForecastCategory.objects.filter(tenant=tenant_a).values_list("name", flat=True))
        assert names == sorted(names)

    def test_created_at_auto_set(self, category_a):
        assert category_a.created_at is not None

    def test_updated_at_auto_set(self, category_a):
        assert category_a.updated_at is not None


# ============================================================ Forecast
@pytest.mark.django_db
class TestForecast:
    def test_auto_number_generated_on_save(self, tenant_a):
        fc = Forecast.objects.create(tenant=tenant_a, name="Auto Num Test")
        assert fc.number.startswith("FCT-")

    def test_auto_number_format_five_digits(self, tenant_a):
        fc = Forecast.objects.create(tenant=tenant_a, name="Fmt Test")
        parts = fc.number.split("-")
        assert len(parts) == 2
        assert len(parts[1]) == 5
        assert parts[1].isdigit()

    def test_first_forecast_is_FCT_00001(self, tenant_a):
        fc = Forecast.objects.create(tenant=tenant_a, name="First")
        assert fc.number == "FCT-00001"

    def test_auto_number_increments_per_tenant(self, tenant_a):
        fc1 = Forecast.objects.create(tenant=tenant_a, name="Fc1")
        fc2 = Forecast.objects.create(tenant=tenant_a, name="Fc2")
        assert fc1.number == "FCT-00001"
        assert fc2.number == "FCT-00002"

    def test_auto_number_isolated_per_tenant(self, tenant_a, tenant_b):
        fc_a = Forecast.objects.create(tenant=tenant_a, name="A Forecast")
        fc_b = Forecast.objects.create(tenant=tenant_b, name="B Forecast")
        assert fc_a.number == "FCT-00001"
        assert fc_b.number == "FCT-00001"

    def test_str_returns_number(self, forecast_a):
        assert forecast_a.number in str(forecast_a)

    def test_str_returns_name_when_no_number(self, tenant_a):
        fc = Forecast(tenant=tenant_a, name="NoNum")
        # Not yet saved, number is blank
        assert str(fc) == "NoNum"

    def test_default_status_is_draft(self, tenant_a):
        fc = Forecast.objects.create(tenant=tenant_a, name="Draft Test")
        assert fc.status == Forecast.STATUS_DRAFT

    def test_default_period_type_is_quarter(self, tenant_a):
        fc = Forecast.objects.create(tenant=tenant_a, name="Period Test")
        assert fc.period_type == Forecast.PERIOD_QUARTER

    def test_default_ai_confidence_is_medium(self, tenant_a):
        fc = Forecast.objects.create(tenant=tenant_a, name="Confidence Test")
        assert fc.ai_confidence == Forecast.CONFIDENCE_MEDIUM

    def test_status_choices_contain_all_four(self):
        choices = dict(Forecast.STATUS_CHOICES)
        assert Forecast.STATUS_DRAFT in choices
        assert Forecast.STATUS_SUBMITTED in choices
        assert Forecast.STATUS_APPROVED in choices
        assert Forecast.STATUS_CLOSED in choices

    def test_period_choices_contain_all_three(self):
        choices = dict(Forecast.PERIOD_CHOICES)
        assert Forecast.PERIOD_MONTH in choices
        assert Forecast.PERIOD_QUARTER in choices
        assert Forecast.PERIOD_YEAR in choices

    def test_confidence_choices_contain_all_three(self):
        choices = dict(Forecast.CONFIDENCE_CHOICES)
        assert Forecast.CONFIDENCE_LOW in choices
        assert Forecast.CONFIDENCE_MEDIUM in choices
        assert Forecast.CONFIDENCE_HIGH in choices

    def test_save_sets_submitted_at_when_status_submitted(self, tenant_a):
        fc = Forecast.objects.create(tenant=tenant_a, name="Submit Me", status=Forecast.STATUS_DRAFT)
        assert fc.submitted_at is None
        fc.status = Forecast.STATUS_SUBMITTED
        fc.save()
        assert fc.submitted_at is not None

    def test_save_does_not_overwrite_submitted_at(self, tenant_a):
        fc = Forecast.objects.create(tenant=tenant_a, name="Already Sub", status=Forecast.STATUS_SUBMITTED)
        original_ts = fc.submitted_at
        fc.name = "Updated"
        fc.save()
        fc.refresh_from_db()
        assert fc.submitted_at == original_ts

    def test_unique_together_tenant_number(self, tenant_a):
        Forecast.objects.create(tenant=tenant_a, name="First")  # gets FCT-00001
        import django.db.utils as db_utils
        with pytest.raises(db_utils.IntegrityError):
            Forecast.objects.create(tenant=tenant_a, number="FCT-00001", name="Duplicate")

    def test_default_pipeline_amount_is_zero(self, tenant_a):
        fc = Forecast.objects.create(tenant=tenant_a, name="Zero Amounts")
        assert fc.pipeline_amount == 0

    def test_category_can_be_null(self, tenant_a):
        fc = Forecast.objects.create(tenant=tenant_a, name="No Category")
        assert fc.category is None


# ============================================================ Quota
@pytest.mark.django_db
class TestQuota:
    def test_str_includes_owner_name(self, quota_a):
        result = str(quota_a)
        assert "Alice" in result

    def test_str_includes_period_label(self, quota_a):
        result = str(quota_a)
        assert "Q3 2026" in result

    def test_str_uses_period_type_display_when_no_label(self, tenant_a):
        quota = Quota.objects.create(
            tenant=tenant_a,
            owner_name="Bob",
            period_type=Quota.PERIOD_MONTH,
        )
        result = str(quota)
        assert "Bob" in result
        assert "Monthly" in result

    def test_default_status_is_active(self, tenant_a):
        q = Quota.objects.create(tenant=tenant_a, owner_name="Rep")
        assert q.status == Quota.STATUS_ACTIVE

    def test_default_period_type_is_quarter(self, tenant_a):
        q = Quota.objects.create(tenant=tenant_a, owner_name="Rep")
        assert q.period_type == Quota.PERIOD_QUARTER

    def test_default_target_amount_is_zero(self, tenant_a):
        q = Quota.objects.create(tenant=tenant_a, owner_name="Rep")
        assert q.target_amount == 0

    def test_default_attained_amount_is_zero(self, tenant_a):
        q = Quota.objects.create(tenant=tenant_a, owner_name="Rep")
        assert q.attained_amount == 0

    def test_status_choices_contain_all_four(self):
        choices = dict(Quota.STATUS_CHOICES)
        assert Quota.STATUS_ACTIVE in choices
        assert Quota.STATUS_ACHIEVED in choices
        assert Quota.STATUS_MISSED in choices
        assert Quota.STATUS_ARCHIVED in choices

    def test_period_choices_contain_all_three(self):
        choices = dict(Quota.PERIOD_CHOICES)
        assert Quota.PERIOD_MONTH in choices
        assert Quota.PERIOD_QUARTER in choices
        assert Quota.PERIOD_YEAR in choices

    def test_attainment_pct_computed(self, quota_a):
        # quota_a has target=150000, attained=75000 -> 50.0%
        # quota_a fixture is refresh_from_db so values are Decimal
        assert quota_a.attainment_pct == 50.0

    def test_attainment_pct_zero_when_no_target(self, tenant_a):
        q = Quota.objects.create(tenant=tenant_a, owner_name="Zero Target", target_amount=Decimal("0"))
        q.refresh_from_db()
        assert q.attainment_pct == 0

    def test_attainment_pct_over_100_allowed(self, tenant_a):
        q = Quota.objects.create(
            tenant=tenant_a,
            owner_name="Over Achiever",
            target_amount=Decimal("100000.00"),
            attained_amount=Decimal("120000.00"),
        )
        q.refresh_from_db()
        assert q.attainment_pct == 120.0


# ============================================================ ForecastAdjustment
@pytest.mark.django_db
class TestForecastAdjustment:
    def test_str_includes_type_display(self, adjustment_a):
        result = str(adjustment_a)
        assert "Uplift" in result

    def test_str_includes_amount(self, adjustment_a):
        result = str(adjustment_a)
        assert "5000" in result

    def test_default_status_is_pending(self, tenant_a, forecast_a):
        adj = ForecastAdjustment.objects.create(
            tenant=tenant_a,
            forecast=forecast_a,
            adjustment_type=ForecastAdjustment.TYPE_OVERRIDE,
            amount="1000.00",
        )
        assert adj.status == ForecastAdjustment.STATUS_PENDING

    def test_default_type_is_uplift(self, tenant_a, forecast_a):
        adj = ForecastAdjustment.objects.create(
            tenant=tenant_a,
            forecast=forecast_a,
            amount="500.00",
        )
        assert adj.adjustment_type == ForecastAdjustment.TYPE_UPLIFT

    def test_type_choices_contain_all_four(self):
        choices = dict(ForecastAdjustment.TYPE_CHOICES)
        assert ForecastAdjustment.TYPE_UPLIFT in choices
        assert ForecastAdjustment.TYPE_HAIRCUT in choices
        assert ForecastAdjustment.TYPE_OVERRIDE in choices
        assert ForecastAdjustment.TYPE_ROLLUP in choices

    def test_status_choices_contain_all_three(self):
        choices = dict(ForecastAdjustment.STATUS_CHOICES)
        assert ForecastAdjustment.STATUS_PENDING in choices
        assert ForecastAdjustment.STATUS_APPROVED in choices
        assert ForecastAdjustment.STATUS_REJECTED in choices

    def test_save_sets_approved_at_when_approved(self, tenant_a, forecast_a):
        adj = ForecastAdjustment.objects.create(
            tenant=tenant_a,
            forecast=forecast_a,
            amount="2000.00",
            status=ForecastAdjustment.STATUS_PENDING,
        )
        assert adj.approved_at is None
        adj.status = ForecastAdjustment.STATUS_APPROVED
        adj.save()
        assert adj.approved_at is not None

    def test_save_does_not_overwrite_approved_at(self, tenant_a, forecast_a):
        adj = ForecastAdjustment.objects.create(
            tenant=tenant_a,
            forecast=forecast_a,
            amount="500.00",
            status=ForecastAdjustment.STATUS_APPROVED,
        )
        original_ts = adj.approved_at
        adj.reason = "Updated"
        adj.save()
        adj.refresh_from_db()
        assert adj.approved_at == original_ts

    def test_approved_at_not_set_for_pending(self, adjustment_a):
        assert adjustment_a.approved_at is None

    def test_ordering_is_descending_created_at(self, tenant_a, forecast_a):
        """Model Meta ordering is ['-created_at'], so later rows should come first."""
        meta_ordering = ForecastAdjustment._meta.ordering
        assert "-created_at" in meta_ordering


# ============================================================ ForecastAccuracy
@pytest.mark.django_db
class TestForecastAccuracy:
    def test_str_includes_period_label(self, accuracy_a):
        result = str(accuracy_a)
        assert "Q2 2026" in result

    def test_str_includes_accuracy_pct(self, accuracy_a):
        result = str(accuracy_a)
        assert "95" in result

    def test_str_shows_period_fallback_when_no_label(self, tenant_a):
        acc = ForecastAccuracy.objects.create(
            tenant=tenant_a,
            forecasted_amount=Decimal("100.00"),
            actual_amount=Decimal("90.00"),
            accuracy_pct=Decimal("90.00"),
        )
        result = str(acc)
        assert "Period" in result

    def test_save_computes_variance_amount(self, tenant_a):
        acc = ForecastAccuracy.objects.create(
            tenant=tenant_a,
            forecasted_amount=Decimal("100000.00"),
            actual_amount=Decimal("95000.00"),
            accuracy_pct=Decimal("95.00"),
        )
        # variance = actual - forecasted = 95000 - 100000 = -5000
        assert acc.variance_amount == Decimal("-5000.00")

    def test_save_recomputes_variance_on_update(self, accuracy_a):
        accuracy_a.actual_amount = Decimal("110000.00")
        accuracy_a.forecasted_amount = Decimal("100000.00")
        accuracy_a.save()
        accuracy_a.refresh_from_db()
        assert accuracy_a.variance_amount == Decimal("10000.00")

    def test_default_grade_is_good(self, tenant_a):
        acc = ForecastAccuracy.objects.create(
            tenant=tenant_a,
            forecasted_amount=Decimal("100.00"),
            actual_amount=Decimal("90.00"),
            accuracy_pct=Decimal("90.00"),
        )
        assert acc.grade == ForecastAccuracy.GRADE_GOOD

    def test_grade_choices_contain_all_four(self):
        choices = dict(ForecastAccuracy.GRADE_CHOICES)
        assert ForecastAccuracy.GRADE_EXCELLENT in choices
        assert ForecastAccuracy.GRADE_GOOD in choices
        assert ForecastAccuracy.GRADE_FAIR in choices
        assert ForecastAccuracy.GRADE_POOR in choices

    def test_analyzed_on_defaults_to_today(self, tenant_a):
        acc = ForecastAccuracy.objects.create(
            tenant=tenant_a,
            forecasted_amount=Decimal("100.00"),
            actual_amount=Decimal("90.00"),
            accuracy_pct=Decimal("90.00"),
        )
        assert acc.analyzed_on == timezone.localdate()

    def test_forecast_fk_can_be_null(self, tenant_a):
        acc = ForecastAccuracy.objects.create(
            tenant=tenant_a,
            forecasted_amount=Decimal("50.00"),
            actual_amount=Decimal("50.00"),
            accuracy_pct=Decimal("100.00"),
        )
        assert acc.forecast is None

    def test_ordering_by_analyzed_on_desc(self, tenant_a):
        from datetime import date
        acc1 = ForecastAccuracy.objects.create(
            tenant=tenant_a,
            forecasted_amount=Decimal("100.00"),
            actual_amount=Decimal("90.00"),
            accuracy_pct=Decimal("90.00"),
            analyzed_on=date(2026, 1, 1),
        )
        acc2 = ForecastAccuracy.objects.create(
            tenant=tenant_a,
            forecasted_amount=Decimal("100.00"),
            actual_amount=Decimal("95.00"),
            accuracy_pct=Decimal("95.00"),
            analyzed_on=date(2026, 3, 1),
        )
        ids = list(ForecastAccuracy.objects.filter(tenant=tenant_a).values_list("id", flat=True))
        assert ids[0] == acc2.pk
