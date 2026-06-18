"""Tests for territories.forms: field presence, required fields, tenant-scoped FK querysets."""
import pytest
from django.utils import timezone

from apps.territories.forms import (
    CoverageModelForm, QuotaPlanForm, TerritoryAssignmentForm,
    TerritoryForm, TerritoryPerformanceForm,
)
from apps.territories.models import Territory


# ============================================================ TerritoryForm
@pytest.mark.django_db
class TestTerritoryForm:
    def test_valid_form(self):
        form = TerritoryForm(data={
            "name": "West Coast",
            "code": "WC-001",
            "territory_type": "geographic",
            "status": "draft",
            "region": "West",
            "country": "US",
            "description": "Pacific territories",
            "account_count": 10,
            "annual_potential": "100000.00",
        })
        assert form.is_valid(), form.errors

    def test_missing_name_is_invalid(self):
        form = TerritoryForm(data={
            "territory_type": "geographic",
            "status": "draft",
        })
        assert not form.is_valid()
        assert "name" in form.errors

    def test_tenant_not_in_form_fields(self):
        form = TerritoryForm()
        assert "tenant" not in form.fields

    def test_created_at_not_in_form_fields(self):
        form = TerritoryForm()
        assert "created_at" not in form.fields

    def test_updated_at_not_in_form_fields(self):
        form = TerritoryForm()
        assert "updated_at" not in form.fields

    def test_invalid_status_choice_invalid(self):
        form = TerritoryForm(data={
            "name": "Bad Status Terr",
            "territory_type": "geographic",
            "status": "not_a_real_status",
        })
        assert not form.is_valid()

    def test_invalid_type_choice_invalid(self):
        form = TerritoryForm(data={
            "name": "Bad Type Terr",
            "territory_type": "not_a_real_type",
            "status": "draft",
        })
        assert not form.is_valid()


# ============================================================ TerritoryAssignmentForm
@pytest.mark.django_db
class TestTerritoryAssignmentForm:
    def test_valid_form(self, tenant_a, territory_a):
        form = TerritoryAssignmentForm(
            data={
                "territory": territory_a.pk,
                "rep_name": "Alice Smith",
                "rep_email": "alice@example.com",
                "assignment_role": "owner",
                "status": "active",
                "workload_percent": 100,
                "effective_date": timezone.localdate().isoformat(),
                "end_date": "",
                "notes": "",
            },
            tenant=tenant_a,
        )
        assert form.is_valid(), form.errors

    def test_missing_rep_name_is_invalid(self, tenant_a, territory_a):
        form = TerritoryAssignmentForm(
            data={
                "territory": territory_a.pk,
                "rep_name": "",
                "assignment_role": "owner",
                "status": "proposed",
                "workload_percent": 100,
                "effective_date": timezone.localdate().isoformat(),
            },
            tenant=tenant_a,
        )
        assert not form.is_valid()
        assert "rep_name" in form.errors

    def test_tenant_not_in_form_fields(self, tenant_a):
        form = TerritoryAssignmentForm(tenant=tenant_a)
        assert "tenant" not in form.fields

    def test_created_at_not_in_form_fields(self, tenant_a):
        form = TerritoryAssignmentForm(tenant=tenant_a)
        assert "created_at" not in form.fields

    def test_territory_queryset_scoped_to_tenant(self, tenant_a, tenant_b, territory_a, territory_b):
        form = TerritoryAssignmentForm(tenant=tenant_a)
        territory_pks = list(form.fields["territory"].queryset.values_list("pk", flat=True))
        assert territory_a.pk in territory_pks
        assert territory_b.pk not in territory_pks

    def test_territory_queryset_empty_when_no_tenant(self):
        form = TerritoryAssignmentForm(tenant=None)
        assert form.fields["territory"].queryset.count() == 0

    def test_territory_queryset_never_uses_all(self, tenant_a, tenant_b, territory_a, territory_b):
        """The queryset must be tenant-scoped, never .all()."""
        form = TerritoryAssignmentForm(tenant=tenant_a)
        qs = form.fields["territory"].queryset
        # The queryset should NOT include other-tenant territories
        assert not qs.filter(tenant=tenant_b).exists()


# ============================================================ QuotaPlanForm
@pytest.mark.django_db
class TestQuotaPlanForm:
    def test_valid_form(self, tenant_a, territory_a):
        form = QuotaPlanForm(
            data={
                "territory": territory_a.pk,
                "name": "Q2 Plan",
                "period_type": "quarterly",
                "fiscal_year": 2026,
                "status": "draft",
                "target_amount": "75000.00",
                "stretch_amount": "90000.00",
                "start_date": "",
                "end_date": "",
                "notes": "",
            },
            tenant=tenant_a,
        )
        assert form.is_valid(), form.errors

    def test_valid_form_without_territory(self, tenant_a):
        form = QuotaPlanForm(
            data={
                "territory": "",
                "name": "No Territory Plan",
                "period_type": "annual",
                "fiscal_year": 2026,
                "status": "draft",
                "target_amount": "100000.00",
                "stretch_amount": "0.00",
                "start_date": "",
                "end_date": "",
                "notes": "",
            },
            tenant=tenant_a,
        )
        assert form.is_valid(), form.errors

    def test_missing_name_is_invalid(self, tenant_a):
        form = QuotaPlanForm(
            data={
                "territory": "",
                "name": "",
                "period_type": "quarterly",
                "fiscal_year": 2026,
                "status": "draft",
                "target_amount": "0.00",
            },
            tenant=tenant_a,
        )
        assert not form.is_valid()
        assert "name" in form.errors

    def test_number_not_in_form_fields(self, tenant_a):
        """number is auto-generated, must not be on the form."""
        form = QuotaPlanForm(tenant=tenant_a)
        assert "number" not in form.fields

    def test_tenant_not_in_form_fields(self, tenant_a):
        form = QuotaPlanForm(tenant=tenant_a)
        assert "tenant" not in form.fields

    def test_approved_at_not_in_form_fields(self, tenant_a):
        """approved_at is system-set, must not be on the form."""
        form = QuotaPlanForm(tenant=tenant_a)
        assert "approved_at" not in form.fields

    def test_territory_queryset_scoped_to_tenant(self, tenant_a, tenant_b, territory_a, territory_b):
        form = QuotaPlanForm(tenant=tenant_a)
        territory_pks = list(form.fields["territory"].queryset.values_list("pk", flat=True))
        assert territory_a.pk in territory_pks
        assert territory_b.pk not in territory_pks

    def test_territory_queryset_empty_when_no_tenant(self):
        form = QuotaPlanForm(tenant=None)
        assert form.fields["territory"].queryset.count() == 0


# ============================================================ CoverageModelForm
@pytest.mark.django_db
class TestCoverageModelForm:
    def test_valid_form(self):
        form = CoverageModelForm(data={
            "name": "Hybrid Coverage",
            "model_type": "hybrid",
            "status": "proposed",
            "target_ratio": "40.00",
            "rep_capacity": 8,
            "coverage_score": "75.50",
            "description": "Mix of field and inside sales.",
        })
        assert form.is_valid(), form.errors

    def test_missing_name_is_invalid(self):
        form = CoverageModelForm(data={
            "model_type": "direct",
            "status": "proposed",
            "target_ratio": "0.00",
            "rep_capacity": 0,
            "coverage_score": "0.00",
        })
        assert not form.is_valid()
        assert "name" in form.errors

    def test_tenant_not_in_form_fields(self):
        form = CoverageModelForm()
        assert "tenant" not in form.fields

    def test_created_at_not_in_form_fields(self):
        form = CoverageModelForm()
        assert "created_at" not in form.fields

    def test_invalid_model_type_invalid(self):
        form = CoverageModelForm(data={
            "name": "Bad Type",
            "model_type": "not_a_real_type",
            "status": "proposed",
            "target_ratio": "0.00",
            "rep_capacity": 0,
            "coverage_score": "0.00",
        })
        assert not form.is_valid()


# ============================================================ TerritoryPerformanceForm
@pytest.mark.django_db
class TestTerritoryPerformanceForm:
    def test_valid_form(self, tenant_a, territory_a):
        form = TerritoryPerformanceForm(
            data={
                "territory": territory_a.pk,
                "period_type": "quarterly",
                "period_label": "Q1 2026",
                "rating": "on_track",
                "quota_amount": "50000.00",
                "actual_amount": "45000.00",
                "pipeline_amount": "60000.00",
                "deals_won": 5,
                "period_end": "",
            },
            tenant=tenant_a,
        )
        assert form.is_valid(), form.errors

    def test_missing_territory_is_invalid(self, tenant_a):
        form = TerritoryPerformanceForm(
            data={
                "territory": "",
                "period_type": "quarterly",
                "period_label": "Q1 2026",
                "rating": "on_track",
                "quota_amount": "0.00",
                "actual_amount": "0.00",
                "pipeline_amount": "0.00",
                "deals_won": 0,
            },
            tenant=tenant_a,
        )
        assert not form.is_valid()
        assert "territory" in form.errors

    def test_tenant_not_in_form_fields(self, tenant_a):
        form = TerritoryPerformanceForm(tenant=tenant_a)
        assert "tenant" not in form.fields

    def test_attainment_percent_not_in_form_fields(self, tenant_a):
        """attainment_percent is computed in save(), must not be on the form."""
        form = TerritoryPerformanceForm(tenant=tenant_a)
        assert "attainment_percent" not in form.fields

    def test_created_at_not_in_form_fields(self, tenant_a):
        form = TerritoryPerformanceForm(tenant=tenant_a)
        assert "created_at" not in form.fields

    def test_territory_queryset_scoped_to_tenant(self, tenant_a, tenant_b, territory_a, territory_b):
        form = TerritoryPerformanceForm(tenant=tenant_a)
        territory_pks = list(form.fields["territory"].queryset.values_list("pk", flat=True))
        assert territory_a.pk in territory_pks
        assert territory_b.pk not in territory_pks

    def test_territory_queryset_empty_when_no_tenant(self):
        form = TerritoryPerformanceForm(tenant=None)
        assert form.fields["territory"].queryset.count() == 0

    def test_territory_queryset_never_uses_all(self, tenant_a, tenant_b, territory_a, territory_b):
        """The queryset must be tenant-scoped, never .all()."""
        form = TerritoryPerformanceForm(tenant=tenant_a)
        qs = form.fields["territory"].queryset
        assert not qs.filter(tenant=tenant_b).exists()
