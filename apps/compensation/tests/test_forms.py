"""Tests for compensation forms: required fields, exclusions, and tenant-scoped FK querysets."""
import pytest
from django.utils import timezone

from apps.compensation.forms import (
    ClawbackForm, CommissionPlanForm, EarningForm, GlobalPlanVariationForm, PayoutForm,
)
from apps.compensation.models import CommissionPlan, Earning


# ============================================================ CommissionPlanForm
@pytest.mark.django_db
class TestCommissionPlanForm:
    def _valid_data(self):
        return {
            "name": "Test Plan",
            "code": "TST",
            "plan_type": CommissionPlan.TYPE_FLAT,
            "status": CommissionPlan.STATUS_DRAFT,
            "base_rate": "5.00",
            "target_quota": "100000.00",
            "effective_from": timezone.localdate().isoformat(),
            "effective_to": "",
            "description": "",
        }

    def test_valid_form(self):
        form = CommissionPlanForm(data=self._valid_data())
        assert form.is_valid(), form.errors

    def test_missing_name_invalid(self):
        data = self._valid_data()
        del data["name"]
        form = CommissionPlanForm(data=data)
        assert not form.is_valid()
        assert "name" in form.errors

    def test_missing_effective_from_invalid(self):
        data = self._valid_data()
        data["effective_from"] = ""
        form = CommissionPlanForm(data=data)
        assert not form.is_valid()
        assert "effective_from" in form.errors

    def test_invalid_plan_type_invalid(self):
        data = self._valid_data()
        data["plan_type"] = "invalid_type"
        form = CommissionPlanForm(data=data)
        assert not form.is_valid()

    def test_invalid_status_invalid(self):
        data = self._valid_data()
        data["status"] = "invalid_status"
        form = CommissionPlanForm(data=data)
        assert not form.is_valid()

    def test_tenant_not_in_form_fields(self):
        form = CommissionPlanForm()
        assert "tenant" not in form.fields

    def test_created_at_not_in_form_fields(self):
        form = CommissionPlanForm()
        assert "created_at" not in form.fields

    def test_updated_at_not_in_form_fields(self):
        form = CommissionPlanForm()
        assert "updated_at" not in form.fields


# ============================================================ EarningForm
@pytest.mark.django_db
class TestEarningForm:
    def _valid_data(self):
        return {
            "plan": "",
            "rep_name": "Alice Smith",
            "deal_reference": "DEAL-001",
            "deal_amount": "50000.00",
            "commission_amount": "2500.00",
            "status": Earning.STATUS_PENDING,
            "earned_on": timezone.localdate().isoformat(),
            "notes": "",
        }

    def test_valid_form(self, tenant_a):
        form = EarningForm(data=self._valid_data(), tenant=tenant_a)
        assert form.is_valid(), form.errors

    def test_missing_rep_name_invalid(self, tenant_a):
        data = self._valid_data()
        del data["rep_name"]
        form = EarningForm(data=data, tenant=tenant_a)
        assert not form.is_valid()
        assert "rep_name" in form.errors

    def test_number_not_in_form_fields(self, tenant_a):
        """number is auto-generated; must not appear in the form."""
        form = EarningForm(tenant=tenant_a)
        assert "number" not in form.fields

    def test_tenant_not_in_form_fields(self, tenant_a):
        form = EarningForm(tenant=tenant_a)
        assert "tenant" not in form.fields

    def test_approved_at_not_in_form_fields(self, tenant_a):
        """approved_at is system-set; must not appear in the form."""
        form = EarningForm(tenant=tenant_a)
        assert "approved_at" not in form.fields

    def test_plan_queryset_scoped_to_tenant(self, tenant_a, tenant_b, plan_a, plan_b):
        form = EarningForm(tenant=tenant_a)
        plan_pks = list(form.fields["plan"].queryset.values_list("pk", flat=True))
        assert plan_a.pk in plan_pks
        assert plan_b.pk not in plan_pks

    def test_plan_queryset_empty_without_tenant(self):
        """Without tenant, plan queryset must be .none() — no cross-tenant leak."""
        form = EarningForm(tenant=None)
        assert form.fields["plan"].queryset.count() == 0

    def test_plan_field_not_required(self, tenant_a):
        form = EarningForm(tenant=tenant_a)
        assert not form.fields["plan"].required

    def test_invalid_status_invalid(self, tenant_a):
        data = self._valid_data()
        data["status"] = "invalid_status"
        form = EarningForm(data=data, tenant=tenant_a)
        assert not form.is_valid()


# ============================================================ ClawbackForm
@pytest.mark.django_db
class TestClawbackForm:
    def _valid_data(self):
        return {
            "earning": "",
            "rep_name": "Alice Smith",
            "reason": "cancellation",
            "status": "open",
            "amount": "500.00",
            "effective_on": timezone.localdate().isoformat(),
            "notes": "",
        }

    def test_valid_form(self, tenant_a):
        form = ClawbackForm(data=self._valid_data(), tenant=tenant_a)
        assert form.is_valid(), form.errors

    def test_missing_rep_name_invalid(self, tenant_a):
        data = self._valid_data()
        del data["rep_name"]
        form = ClawbackForm(data=data, tenant=tenant_a)
        assert not form.is_valid()
        assert "rep_name" in form.errors

    def test_missing_amount_invalid(self, tenant_a):
        data = self._valid_data()
        del data["amount"]
        form = ClawbackForm(data=data, tenant=tenant_a)
        assert not form.is_valid()

    def test_tenant_not_in_form_fields(self, tenant_a):
        form = ClawbackForm(tenant=tenant_a)
        assert "tenant" not in form.fields

    def test_applied_at_not_in_form_fields(self, tenant_a):
        """applied_at is system-set; must not appear in the form."""
        form = ClawbackForm(tenant=tenant_a)
        assert "applied_at" not in form.fields

    def test_earning_queryset_scoped_to_tenant(self, tenant_a, tenant_b, earning_a, earning_b):
        form = ClawbackForm(tenant=tenant_a)
        earning_pks = list(form.fields["earning"].queryset.values_list("pk", flat=True))
        assert earning_a.pk in earning_pks
        assert earning_b.pk not in earning_pks

    def test_earning_queryset_empty_without_tenant(self):
        """Without tenant, earning queryset must be .none()."""
        form = ClawbackForm(tenant=None)
        assert form.fields["earning"].queryset.count() == 0

    def test_earning_field_not_required(self, tenant_a):
        form = ClawbackForm(tenant=tenant_a)
        assert not form.fields["earning"].required

    def test_invalid_reason_invalid(self, tenant_a):
        data = self._valid_data()
        data["reason"] = "invalid_reason"
        form = ClawbackForm(data=data, tenant=tenant_a)
        assert not form.is_valid()


# ============================================================ GlobalPlanVariationForm
@pytest.mark.django_db
class TestGlobalPlanVariationForm:
    def _valid_data(self):
        return {
            "plan": "",
            "region": "North America",
            "currency": "USD",
            "status": "active",
            "fx_rate": "1.000000",
            "local_quota": "100000.00",
            "rate_adjustment": "0.00",
            "effective_from": timezone.localdate().isoformat(),
            "notes": "",
        }

    def test_valid_form(self, tenant_a):
        form = GlobalPlanVariationForm(data=self._valid_data(), tenant=tenant_a)
        assert form.is_valid(), form.errors

    def test_missing_region_invalid(self, tenant_a):
        data = self._valid_data()
        del data["region"]
        form = GlobalPlanVariationForm(data=data, tenant=tenant_a)
        assert not form.is_valid()
        assert "region" in form.errors

    def test_tenant_not_in_form_fields(self, tenant_a):
        form = GlobalPlanVariationForm(tenant=tenant_a)
        assert "tenant" not in form.fields

    def test_plan_queryset_scoped_to_tenant(self, tenant_a, tenant_b, plan_a, plan_b):
        form = GlobalPlanVariationForm(tenant=tenant_a)
        plan_pks = list(form.fields["plan"].queryset.values_list("pk", flat=True))
        assert plan_a.pk in plan_pks
        assert plan_b.pk not in plan_pks

    def test_plan_queryset_empty_without_tenant(self):
        """Without tenant, plan queryset must be .none()."""
        form = GlobalPlanVariationForm(tenant=None)
        assert form.fields["plan"].queryset.count() == 0

    def test_plan_field_not_required(self, tenant_a):
        form = GlobalPlanVariationForm(tenant=tenant_a)
        assert not form.fields["plan"].required

    def test_invalid_currency_invalid(self, tenant_a):
        data = self._valid_data()
        data["currency"] = "XYZ"
        form = GlobalPlanVariationForm(data=data, tenant=tenant_a)
        assert not form.is_valid()

    def test_created_at_not_in_form_fields(self, tenant_a):
        form = GlobalPlanVariationForm(tenant=tenant_a)
        assert "created_at" not in form.fields


# ============================================================ PayoutForm
@pytest.mark.django_db
class TestPayoutForm:
    def _valid_data(self):
        return {
            "rep_name": "Alice Smith",
            "method": "payroll",
            "status": "scheduled",
            "gross_amount": "5000.00",
            "deductions": "500.00",
            "net_amount": "4500.00",
            "period_label": "2026-Q1",
            "scheduled_on": timezone.localdate().isoformat(),
            "reference": "",
            "notes": "",
        }

    def test_valid_form(self):
        form = PayoutForm(data=self._valid_data())
        assert form.is_valid(), form.errors

    def test_missing_rep_name_invalid(self):
        data = self._valid_data()
        del data["rep_name"]
        form = PayoutForm(data=data)
        assert not form.is_valid()
        assert "rep_name" in form.errors

    def test_number_not_in_form_fields(self):
        """number is auto-generated; must not appear in the form."""
        form = PayoutForm()
        assert "number" not in form.fields

    def test_tenant_not_in_form_fields(self):
        form = PayoutForm()
        assert "tenant" not in form.fields

    def test_paid_at_not_in_form_fields(self):
        """paid_at is system-set; must not appear in the form."""
        form = PayoutForm()
        assert "paid_at" not in form.fields

    def test_invalid_method_invalid(self):
        data = self._valid_data()
        data["method"] = "invalid_method"
        form = PayoutForm(data=data)
        assert not form.is_valid()

    def test_invalid_status_invalid(self):
        data = self._valid_data()
        data["status"] = "invalid_status"
        form = PayoutForm(data=data)
        assert not form.is_valid()

    def test_missing_scheduled_on_invalid(self):
        data = self._valid_data()
        data["scheduled_on"] = ""
        form = PayoutForm(data=data)
        assert not form.is_valid()
        assert "scheduled_on" in form.errors
