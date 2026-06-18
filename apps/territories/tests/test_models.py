"""Tests for territories.models: Territory, TerritoryAssignment, QuotaPlan,
CoverageModel, TerritoryPerformance."""
import pytest
from decimal import Decimal

import django.db.utils as db_utils
from django.utils import timezone

from apps.territories.models import (
    CoverageModel, QuotaPlan, Territory, TerritoryAssignment, TerritoryPerformance,
)


# ============================================================ Territory
@pytest.mark.django_db
class TestTerritory:
    def test_str_returns_name(self, territory_a):
        assert str(territory_a) == "North Region"

    def test_default_status_is_draft(self, tenant_a):
        t = Territory.objects.create(tenant=tenant_a, name="Draft Terr")
        assert t.status == Territory.STATUS_DRAFT

    def test_default_type_is_geographic(self, tenant_a):
        t = Territory.objects.create(tenant=tenant_a, name="Geo Terr")
        assert t.territory_type == Territory.TYPE_GEOGRAPHIC

    def test_default_account_count_is_zero(self, tenant_a):
        t = Territory.objects.create(tenant=tenant_a, name="Zero Count")
        assert t.account_count == 0

    def test_default_annual_potential_is_zero(self, tenant_a):
        t = Territory.objects.create(tenant=tenant_a, name="Zero Potential")
        assert t.annual_potential == Decimal("0")

    def test_type_choices_contain_all_five(self):
        choices = dict(Territory.TYPE_CHOICES)
        assert Territory.TYPE_GEOGRAPHIC in choices
        assert Territory.TYPE_INDUSTRY in choices
        assert Territory.TYPE_ACCOUNT in choices
        assert Territory.TYPE_PRODUCT in choices
        assert Territory.TYPE_NAMED_ACCOUNT in choices

    def test_status_choices_contain_all_four(self):
        choices = dict(Territory.STATUS_CHOICES)
        assert Territory.STATUS_DRAFT in choices
        assert Territory.STATUS_ACTIVE in choices
        assert Territory.STATUS_UNDER_REVIEW in choices
        assert Territory.STATUS_ARCHIVED in choices

    def test_created_at_auto_set(self, territory_a):
        assert territory_a.created_at is not None

    def test_updated_at_auto_set(self, territory_a):
        assert territory_a.updated_at is not None

    def test_ordering_by_name(self, tenant_a):
        Territory.objects.create(tenant=tenant_a, name="Z Territory")
        Territory.objects.create(tenant=tenant_a, name="A Territory")
        names = list(
            Territory.objects.filter(tenant=tenant_a).values_list("name", flat=True)
        )
        assert names == sorted(names)


# ============================================================ TerritoryAssignment
@pytest.mark.django_db
class TestTerritoryAssignment:
    def test_str_includes_rep_name_and_territory(self, assignment_a):
        result = str(assignment_a)
        assert "Alice Smith" in result
        assert "North Region" in result

    def test_default_role_is_owner(self, tenant_a, territory_a):
        a = TerritoryAssignment.objects.create(
            tenant=tenant_a, territory=territory_a, rep_name="Rep X",
            effective_date=timezone.localdate(),
        )
        assert a.assignment_role == TerritoryAssignment.ROLE_OWNER

    def test_default_status_is_proposed(self, tenant_a, territory_a):
        a = TerritoryAssignment.objects.create(
            tenant=tenant_a, territory=territory_a, rep_name="Rep Y",
            effective_date=timezone.localdate(),
        )
        assert a.status == TerritoryAssignment.STATUS_PROPOSED

    def test_default_workload_percent_is_100(self, tenant_a, territory_a):
        a = TerritoryAssignment.objects.create(
            tenant=tenant_a, territory=territory_a, rep_name="Rep Z",
            effective_date=timezone.localdate(),
        )
        assert a.workload_percent == 100

    def test_role_choices_contain_all_four(self):
        choices = dict(TerritoryAssignment.ROLE_CHOICES)
        assert TerritoryAssignment.ROLE_OWNER in choices
        assert TerritoryAssignment.ROLE_OVERLAY in choices
        assert TerritoryAssignment.ROLE_BACKUP in choices
        assert TerritoryAssignment.ROLE_MANAGER in choices

    def test_status_choices_contain_all_four(self):
        choices = dict(TerritoryAssignment.STATUS_CHOICES)
        assert TerritoryAssignment.STATUS_PROPOSED in choices
        assert TerritoryAssignment.STATUS_ACTIVE in choices
        assert TerritoryAssignment.STATUS_REBALANCING in choices
        assert TerritoryAssignment.STATUS_ENDED in choices

    def test_created_at_auto_set(self, assignment_a):
        assert assignment_a.created_at is not None


# ============================================================ QuotaPlan
@pytest.mark.django_db
class TestQuotaPlan:
    def test_str_returns_number_when_set(self, quota_plan_a):
        assert str(quota_plan_a) == quota_plan_a.number

    def test_str_returns_name_when_no_number(self, tenant_a):
        # Build (not save) to check __str__ without number
        qp = QuotaPlan(tenant=tenant_a, name="Unsaved Plan")
        assert str(qp) == "Unsaved Plan"

    def test_auto_number_generated_on_save(self, tenant_a):
        qp = QuotaPlan.objects.create(
            tenant=tenant_a, name="Auto Number Plan",
            period_type=QuotaPlan.PERIOD_QUARTERLY, fiscal_year=2026,
        )
        assert qp.number.startswith("QP-")

    def test_auto_number_format_five_digits(self, tenant_a):
        qp = QuotaPlan.objects.create(
            tenant=tenant_a, name="Format Check", fiscal_year=2026,
        )
        parts = qp.number.split("-")
        assert len(parts) == 2
        assert parts[0] == "QP"
        assert len(parts[1]) == 5
        assert parts[1].isdigit()

    def test_first_quota_plan_is_QP_00001(self, tenant_a):
        qp = QuotaPlan.objects.create(
            tenant=tenant_a, name="First Plan", fiscal_year=2026,
        )
        assert qp.number == "QP-00001"

    def test_auto_number_increments_per_tenant(self, tenant_a):
        qp1 = QuotaPlan.objects.create(
            tenant=tenant_a, name="Plan 1", fiscal_year=2026,
        )
        qp2 = QuotaPlan.objects.create(
            tenant=tenant_a, name="Plan 2", fiscal_year=2026,
        )
        assert qp1.number == "QP-00001"
        assert qp2.number == "QP-00002"

    def test_auto_number_isolated_per_tenant(self, tenant_a, tenant_b):
        qp_a = QuotaPlan.objects.create(
            tenant=tenant_a, name="Plan A", fiscal_year=2026,
        )
        qp_b = QuotaPlan.objects.create(
            tenant=tenant_b, name="Plan B", fiscal_year=2026,
        )
        assert qp_a.number == "QP-00001"
        assert qp_b.number == "QP-00001"

    def test_unique_together_tenant_number(self, tenant_a):
        QuotaPlan.objects.create(tenant=tenant_a, name="Plan X", fiscal_year=2026)
        with pytest.raises(db_utils.IntegrityError):
            QuotaPlan.objects.create(
                tenant=tenant_a, name="Plan Y", number="QP-00001", fiscal_year=2026,
            )

    def test_default_status_is_draft(self, tenant_a):
        qp = QuotaPlan.objects.create(
            tenant=tenant_a, name="Draft Plan", fiscal_year=2026,
        )
        assert qp.status == QuotaPlan.STATUS_DRAFT

    def test_default_period_is_quarterly(self, tenant_a):
        qp = QuotaPlan.objects.create(
            tenant=tenant_a, name="Quarterly Default", fiscal_year=2026,
        )
        assert qp.period_type == QuotaPlan.PERIOD_QUARTERLY

    def test_approved_at_set_when_status_approved(self, tenant_a):
        qp = QuotaPlan.objects.create(
            tenant=tenant_a, name="To Approve", fiscal_year=2026,
            status=QuotaPlan.STATUS_APPROVED,
        )
        assert qp.approved_at is not None

    def test_approved_at_not_set_for_draft(self, tenant_a):
        qp = QuotaPlan.objects.create(
            tenant=tenant_a, name="Draft Only", fiscal_year=2026,
        )
        assert qp.approved_at is None

    def test_period_choices_contain_all_three(self):
        choices = dict(QuotaPlan.PERIOD_CHOICES)
        assert QuotaPlan.PERIOD_MONTHLY in choices
        assert QuotaPlan.PERIOD_QUARTERLY in choices
        assert QuotaPlan.PERIOD_ANNUAL in choices

    def test_status_choices_contain_all_four(self):
        choices = dict(QuotaPlan.STATUS_CHOICES)
        assert QuotaPlan.STATUS_DRAFT in choices
        assert QuotaPlan.STATUS_PROPOSED in choices
        assert QuotaPlan.STATUS_APPROVED in choices
        assert QuotaPlan.STATUS_LOCKED in choices


# ============================================================ CoverageModel
@pytest.mark.django_db
class TestCoverageModel:
    def test_str_returns_name(self, coverage_model_a):
        assert str(coverage_model_a) == "Direct Field Model"

    def test_default_status_is_proposed(self, tenant_a):
        cm = CoverageModel.objects.create(tenant=tenant_a, name="New CM")
        assert cm.status == CoverageModel.STATUS_PROPOSED

    def test_default_model_type_is_direct(self, tenant_a):
        cm = CoverageModel.objects.create(tenant=tenant_a, name="Direct CM")
        assert cm.model_type == CoverageModel.MODEL_DIRECT

    def test_default_target_ratio_is_zero(self, tenant_a):
        cm = CoverageModel.objects.create(tenant=tenant_a, name="Zero Ratio CM")
        assert cm.target_ratio == Decimal("0")

    def test_default_rep_capacity_is_zero(self, tenant_a):
        cm = CoverageModel.objects.create(tenant=tenant_a, name="Zero Cap CM")
        assert cm.rep_capacity == 0

    def test_model_choices_contain_all_five(self):
        choices = dict(CoverageModel.MODEL_CHOICES)
        assert CoverageModel.MODEL_DIRECT in choices
        assert CoverageModel.MODEL_INSIDE in choices
        assert CoverageModel.MODEL_HYBRID in choices
        assert CoverageModel.MODEL_PARTNER in choices
        assert CoverageModel.MODEL_POD in choices

    def test_status_choices_contain_all_four(self):
        choices = dict(CoverageModel.STATUS_CHOICES)
        assert CoverageModel.STATUS_PROPOSED in choices
        assert CoverageModel.STATUS_PILOT in choices
        assert CoverageModel.STATUS_ADOPTED in choices
        assert CoverageModel.STATUS_RETIRED in choices

    def test_created_at_auto_set(self, coverage_model_a):
        assert coverage_model_a.created_at is not None


# ============================================================ TerritoryPerformance
@pytest.mark.django_db
class TestTerritoryPerformance:
    def test_str_includes_territory_name_and_period(self, performance_a):
        result = str(performance_a)
        assert "North Region" in result
        assert "Q1 2026" in result

    def test_str_uses_period_type_display_when_no_label(self, tenant_a, territory_a):
        perf = TerritoryPerformance.objects.create(
            tenant=tenant_a, territory=territory_a,
            period_type=TerritoryPerformance.PERIOD_MONTHLY,
            quota_amount=Decimal("10000.00"), actual_amount=Decimal("8000.00"),
        )
        result = str(perf)
        assert "North Region" in result
        assert "Monthly" in result

    def test_attainment_percent_computed_on_save(self, tenant_a, territory_a):
        perf = TerritoryPerformance.objects.create(
            tenant=tenant_a, territory=territory_a,
            quota_amount=Decimal("100000.00"), actual_amount=Decimal("75000.00"),
        )
        assert perf.attainment_percent == Decimal("75.00")

    def test_attainment_percent_zero_when_quota_is_zero(self, tenant_a, territory_a):
        perf = TerritoryPerformance.objects.create(
            tenant=tenant_a, territory=territory_a,
            quota_amount=Decimal("0"), actual_amount=Decimal("5000.00"),
        )
        # quota=0 means no division — attainment stays at default 0
        assert perf.attainment_percent == Decimal("0")

    def test_attainment_exceeds_100_when_actual_over_quota(self, tenant_a, territory_a):
        perf = TerritoryPerformance.objects.create(
            tenant=tenant_a, territory=territory_a,
            quota_amount=Decimal("50000.00"), actual_amount=Decimal("60000.00"),
        )
        assert perf.attainment_percent > Decimal("100")

    def test_default_rating_is_on_track(self, tenant_a, territory_a):
        perf = TerritoryPerformance.objects.create(
            tenant=tenant_a, territory=territory_a,
        )
        assert perf.rating == TerritoryPerformance.RATING_ON_TRACK

    def test_default_period_is_quarterly(self, tenant_a, territory_a):
        perf = TerritoryPerformance.objects.create(
            tenant=tenant_a, territory=territory_a,
        )
        assert perf.period_type == TerritoryPerformance.PERIOD_QUARTERLY

    def test_rating_choices_contain_all_four(self):
        choices = dict(TerritoryPerformance.RATING_CHOICES)
        assert TerritoryPerformance.RATING_EXCEEDING in choices
        assert TerritoryPerformance.RATING_ON_TRACK in choices
        assert TerritoryPerformance.RATING_AT_RISK in choices
        assert TerritoryPerformance.RATING_UNDERPERFORMING in choices

    def test_period_choices_contain_all_three(self):
        choices = dict(TerritoryPerformance.PERIOD_CHOICES)
        assert TerritoryPerformance.PERIOD_MONTHLY in choices
        assert TerritoryPerformance.PERIOD_QUARTERLY in choices
        assert TerritoryPerformance.PERIOD_ANNUAL in choices

    def test_created_at_auto_set(self, performance_a):
        assert performance_a.created_at is not None
