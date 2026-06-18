"""Tests for compensation models: CommissionPlan, Earning, Clawback, GlobalPlanVariation, Payout."""
import pytest
from django.utils import timezone

from apps.compensation.models import (
    Clawback, CommissionPlan, Earning, GlobalPlanVariation, Payout,
)


# ============================================================ CommissionPlan
@pytest.mark.django_db
class TestCommissionPlan:
    def test_str_returns_name(self, plan_a):
        assert str(plan_a) == "Plan Alpha"

    def test_default_plan_type_is_flat(self, tenant_a):
        plan = CommissionPlan.objects.create(
            tenant=tenant_a, name="Default Type Plan", effective_from=timezone.localdate()
        )
        assert plan.plan_type == CommissionPlan.TYPE_FLAT

    def test_default_status_is_draft(self, tenant_a):
        plan = CommissionPlan.objects.create(
            tenant=tenant_a, name="Draft Plan", effective_from=timezone.localdate()
        )
        assert plan.status == CommissionPlan.STATUS_DRAFT

    def test_default_base_rate_is_zero(self, tenant_a):
        plan = CommissionPlan.objects.create(
            tenant=tenant_a, name="Zero Rate Plan", effective_from=timezone.localdate()
        )
        assert plan.base_rate == 0

    def test_default_target_quota_is_zero(self, tenant_a):
        plan = CommissionPlan.objects.create(
            tenant=tenant_a, name="Zero Quota Plan", effective_from=timezone.localdate()
        )
        assert plan.target_quota == 0

    def test_type_choices_contain_all_four(self):
        choices = dict(CommissionPlan.TYPE_CHOICES)
        assert CommissionPlan.TYPE_FLAT in choices
        assert CommissionPlan.TYPE_TIERED in choices
        assert CommissionPlan.TYPE_ACCELERATOR in choices
        assert CommissionPlan.TYPE_BONUS in choices

    def test_status_choices_contain_all_four(self):
        choices = dict(CommissionPlan.STATUS_CHOICES)
        assert CommissionPlan.STATUS_DRAFT in choices
        assert CommissionPlan.STATUS_ACTIVE in choices
        assert CommissionPlan.STATUS_PAUSED in choices
        assert CommissionPlan.STATUS_ARCHIVED in choices

    def test_effective_from_defaults_to_today(self, tenant_a):
        plan = CommissionPlan.objects.create(tenant=tenant_a, name="Today Plan")
        assert plan.effective_from == timezone.localdate()

    def test_effective_to_is_nullable(self, tenant_a):
        plan = CommissionPlan.objects.create(
            tenant=tenant_a, name="No End Plan", effective_from=timezone.localdate()
        )
        assert plan.effective_to is None

    def test_tenant_fk_set(self, plan_a, tenant_a):
        assert plan_a.tenant == tenant_a

    def test_created_at_set_automatically(self, plan_a):
        assert plan_a.created_at is not None

    def test_updated_at_set_automatically(self, plan_a):
        assert plan_a.updated_at is not None


# ============================================================ Earning
@pytest.mark.django_db
class TestEarning:
    def test_auto_number_generated_on_save(self, earning_a):
        assert earning_a.number.startswith("EARN-")

    def test_auto_number_format_five_digits(self, earning_a):
        parts = earning_a.number.split("-")
        assert len(parts) == 2
        assert len(parts[1]) == 5
        assert parts[1].isdigit()

    def test_first_earning_is_EARN_00001(self, tenant_a):
        # Clean slate for this tenant
        Earning.objects.filter(tenant=tenant_a).delete()
        e = Earning.objects.create(
            tenant=tenant_a, rep_name="Test Rep", earned_on=timezone.localdate()
        )
        assert e.number == "EARN-00001"

    def test_auto_number_increments_per_tenant(self, tenant_a):
        Earning.objects.filter(tenant=tenant_a).delete()
        e1 = Earning.objects.create(
            tenant=tenant_a, rep_name="Rep 1", earned_on=timezone.localdate()
        )
        e2 = Earning.objects.create(
            tenant=tenant_a, rep_name="Rep 2", earned_on=timezone.localdate()
        )
        assert e1.number == "EARN-00001"
        assert e2.number == "EARN-00002"

    def test_auto_number_isolated_per_tenant(self, tenant_a, tenant_b):
        Earning.objects.filter(tenant=tenant_a).delete()
        Earning.objects.filter(tenant=tenant_b).delete()
        ea = Earning.objects.create(
            tenant=tenant_a, rep_name="Rep A", earned_on=timezone.localdate()
        )
        eb = Earning.objects.create(
            tenant=tenant_b, rep_name="Rep B", earned_on=timezone.localdate()
        )
        assert ea.number == "EARN-00001"
        assert eb.number == "EARN-00001"

    def test_str_returns_number(self, earning_a):
        assert earning_a.number in str(earning_a)

    def test_str_fallback_when_no_number(self, tenant_a):
        e = Earning(tenant=tenant_a, rep_name="Unsaved Rep")
        # not saved — number is blank
        result = str(e)
        assert result is not None

    def test_unique_together_tenant_number(self, tenant_a):
        Earning.objects.filter(tenant=tenant_a).delete()
        e = Earning.objects.create(
            tenant=tenant_a, rep_name="First Rep", earned_on=timezone.localdate()
        )
        import django.db.utils as db_utils
        with pytest.raises(db_utils.IntegrityError):
            Earning.objects.create(
                tenant=tenant_a, number=e.number, rep_name="Dup Rep",
                earned_on=timezone.localdate()
            )

    def test_approved_at_set_when_status_approved(self, tenant_a):
        Earning.objects.filter(tenant=tenant_a).delete()
        e = Earning.objects.create(
            tenant=tenant_a, rep_name="Approved Rep",
            status=Earning.STATUS_APPROVED, earned_on=timezone.localdate()
        )
        assert e.approved_at is not None

    def test_approved_at_set_when_status_paid(self, tenant_a):
        Earning.objects.filter(tenant=tenant_a).delete()
        e = Earning.objects.create(
            tenant=tenant_a, rep_name="Paid Rep",
            status=Earning.STATUS_PAID, earned_on=timezone.localdate()
        )
        assert e.approved_at is not None

    def test_approved_at_cleared_when_status_pending(self, earning_a):
        earning_a.status = Earning.STATUS_APPROVED
        earning_a.save()
        assert earning_a.approved_at is not None
        earning_a.status = Earning.STATUS_PENDING
        earning_a.save()
        earning_a.refresh_from_db()
        assert earning_a.approved_at is None

    def test_approved_at_cleared_when_status_disputed(self, earning_a):
        earning_a.status = Earning.STATUS_APPROVED
        earning_a.save()
        earning_a.status = Earning.STATUS_DISPUTED
        earning_a.save()
        earning_a.refresh_from_db()
        assert earning_a.approved_at is None

    def test_default_status_is_pending(self, tenant_a):
        Earning.objects.filter(tenant=tenant_a).delete()
        e = Earning.objects.create(
            tenant=tenant_a, rep_name="Default Rep", earned_on=timezone.localdate()
        )
        assert e.status == Earning.STATUS_PENDING

    def test_status_choices_contain_all_four(self):
        choices = dict(Earning.STATUS_CHOICES)
        assert Earning.STATUS_PENDING in choices
        assert Earning.STATUS_APPROVED in choices
        assert Earning.STATUS_PAID in choices
        assert Earning.STATUS_DISPUTED in choices

    def test_tenant_fk_set(self, earning_a, tenant_a):
        assert earning_a.tenant == tenant_a


# ============================================================ Clawback
@pytest.mark.django_db
class TestClawback:
    def test_str_shows_reason_and_rep(self, clawback_a):
        result = str(clawback_a)
        assert "Alice Smith" in result
        # reason display should be present
        assert "cancellation" in result.lower() or "Deal cancellation" in result

    def test_default_reason_is_cancellation(self, tenant_a):
        cb = Clawback.objects.create(
            tenant=tenant_a, rep_name="Test Rep", amount="100.00",
            effective_on=timezone.localdate()
        )
        assert cb.reason == Clawback.REASON_CANCELLATION

    def test_default_status_is_open(self, tenant_a):
        cb = Clawback.objects.create(
            tenant=tenant_a, rep_name="Test Rep", amount="100.00",
            effective_on=timezone.localdate()
        )
        assert cb.status == Clawback.STATUS_OPEN

    def test_applied_at_set_when_status_applied(self, tenant_a):
        cb = Clawback.objects.create(
            tenant=tenant_a, rep_name="Applied Rep",
            status=Clawback.STATUS_APPLIED, amount="200.00",
            effective_on=timezone.localdate()
        )
        assert cb.applied_at is not None

    def test_applied_at_cleared_when_not_applied(self, clawback_a):
        clawback_a.status = Clawback.STATUS_APPLIED
        clawback_a.save()
        assert clawback_a.applied_at is not None
        clawback_a.status = Clawback.STATUS_OPEN
        clawback_a.save()
        clawback_a.refresh_from_db()
        assert clawback_a.applied_at is None

    def test_applied_at_cleared_for_waived(self, tenant_a):
        cb = Clawback.objects.create(
            tenant=tenant_a, rep_name="Waived Rep",
            status=Clawback.STATUS_APPLIED, amount="100.00",
            effective_on=timezone.localdate()
        )
        cb.status = Clawback.STATUS_WAIVED
        cb.save()
        cb.refresh_from_db()
        assert cb.applied_at is None

    def test_reason_choices_contain_all_five(self):
        choices = dict(Clawback.REASON_CHOICES)
        assert Clawback.REASON_CANCELLATION in choices
        assert Clawback.REASON_REFUND in choices
        assert Clawback.REASON_CHARGEBACK in choices
        assert Clawback.REASON_CORRECTION in choices
        assert Clawback.REASON_OTHER in choices

    def test_status_choices_contain_all_four(self):
        choices = dict(Clawback.STATUS_CHOICES)
        assert Clawback.STATUS_OPEN in choices
        assert Clawback.STATUS_APPLIED in choices
        assert Clawback.STATUS_WAIVED in choices
        assert Clawback.STATUS_DISPUTED in choices

    def test_tenant_fk_set(self, clawback_a, tenant_a):
        assert clawback_a.tenant == tenant_a

    def test_earning_fk_optional(self, tenant_a):
        cb = Clawback.objects.create(
            tenant=tenant_a, rep_name="No Earning Rep", amount="50.00",
            effective_on=timezone.localdate()
        )
        assert cb.earning is None


# ============================================================ GlobalPlanVariation
@pytest.mark.django_db
class TestGlobalPlanVariation:
    def test_str_shows_region_and_currency(self, variation_a):
        result = str(variation_a)
        assert "North America" in result
        assert "USD" in result

    def test_default_currency_is_usd(self, tenant_a):
        v = GlobalPlanVariation.objects.create(
            tenant=tenant_a, region="Test Region", effective_from=timezone.localdate()
        )
        assert v.currency == GlobalPlanVariation.CURRENCY_USD

    def test_default_status_is_active(self, tenant_a):
        v = GlobalPlanVariation.objects.create(
            tenant=tenant_a, region="Test Region 2", effective_from=timezone.localdate()
        )
        assert v.status == GlobalPlanVariation.STATUS_ACTIVE

    def test_default_fx_rate_is_one(self, tenant_a):
        v = GlobalPlanVariation.objects.create(
            tenant=tenant_a, region="Test Region 3", effective_from=timezone.localdate()
        )
        assert v.fx_rate == 1

    def test_currency_choices_contain_all_seven(self):
        choices = dict(GlobalPlanVariation.CURRENCY_CHOICES)
        assert GlobalPlanVariation.CURRENCY_USD in choices
        assert GlobalPlanVariation.CURRENCY_EUR in choices
        assert GlobalPlanVariation.CURRENCY_GBP in choices
        assert GlobalPlanVariation.CURRENCY_JPY in choices
        assert GlobalPlanVariation.CURRENCY_AUD in choices
        assert GlobalPlanVariation.CURRENCY_CAD in choices
        assert GlobalPlanVariation.CURRENCY_INR in choices

    def test_status_choices_contain_all_three(self):
        choices = dict(GlobalPlanVariation.STATUS_CHOICES)
        assert GlobalPlanVariation.STATUS_ACTIVE in choices
        assert GlobalPlanVariation.STATUS_PENDING in choices
        assert GlobalPlanVariation.STATUS_RETIRED in choices

    def test_plan_fk_optional(self, tenant_a):
        v = GlobalPlanVariation.objects.create(
            tenant=tenant_a, region="No Plan Region", effective_from=timezone.localdate()
        )
        assert v.plan is None

    def test_tenant_fk_set(self, variation_a, tenant_a):
        assert variation_a.tenant == tenant_a


# ============================================================ Payout
@pytest.mark.django_db
class TestPayout:
    def test_auto_number_generated_on_save(self, payout_a):
        assert payout_a.number.startswith("PAY-")

    def test_auto_number_format_five_digits(self, payout_a):
        parts = payout_a.number.split("-")
        assert len(parts) == 2
        assert len(parts[1]) == 5
        assert parts[1].isdigit()

    def test_first_payout_is_PAY_00001(self, tenant_a):
        Payout.objects.filter(tenant=tenant_a).delete()
        p = Payout.objects.create(
            tenant=tenant_a, rep_name="Test Rep", scheduled_on=timezone.localdate()
        )
        assert p.number == "PAY-00001"

    def test_auto_number_increments_per_tenant(self, tenant_a):
        Payout.objects.filter(tenant=tenant_a).delete()
        p1 = Payout.objects.create(
            tenant=tenant_a, rep_name="Rep 1", scheduled_on=timezone.localdate()
        )
        p2 = Payout.objects.create(
            tenant=tenant_a, rep_name="Rep 2", scheduled_on=timezone.localdate()
        )
        assert p1.number == "PAY-00001"
        assert p2.number == "PAY-00002"

    def test_auto_number_isolated_per_tenant(self, tenant_a, tenant_b):
        Payout.objects.filter(tenant=tenant_a).delete()
        Payout.objects.filter(tenant=tenant_b).delete()
        pa = Payout.objects.create(
            tenant=tenant_a, rep_name="Rep A", scheduled_on=timezone.localdate()
        )
        pb = Payout.objects.create(
            tenant=tenant_b, rep_name="Rep B", scheduled_on=timezone.localdate()
        )
        assert pa.number == "PAY-00001"
        assert pb.number == "PAY-00001"

    def test_str_returns_number(self, payout_a):
        assert payout_a.number in str(payout_a)

    def test_str_fallback_when_no_number(self, tenant_a):
        p = Payout(tenant=tenant_a, rep_name="Unsaved Rep")
        result = str(p)
        assert result is not None

    def test_unique_together_tenant_number(self, tenant_a):
        Payout.objects.filter(tenant=tenant_a).delete()
        p = Payout.objects.create(
            tenant=tenant_a, rep_name="First Rep", scheduled_on=timezone.localdate()
        )
        import django.db.utils as db_utils
        with pytest.raises(db_utils.IntegrityError):
            Payout.objects.create(
                tenant=tenant_a, number=p.number, rep_name="Dup Rep",
                scheduled_on=timezone.localdate()
            )

    def test_paid_at_set_when_status_paid(self, tenant_a):
        Payout.objects.filter(tenant=tenant_a).delete()
        p = Payout.objects.create(
            tenant=tenant_a, rep_name="Paid Rep",
            status=Payout.STATUS_PAID, scheduled_on=timezone.localdate()
        )
        assert p.paid_at is not None

    def test_paid_at_not_set_when_status_scheduled(self, payout_a):
        assert payout_a.status == Payout.STATUS_SCHEDULED
        assert payout_a.paid_at is None

    def test_default_status_is_scheduled(self, tenant_a):
        Payout.objects.filter(tenant=tenant_a).delete()
        p = Payout.objects.create(
            tenant=tenant_a, rep_name="Default Rep", scheduled_on=timezone.localdate()
        )
        assert p.status == Payout.STATUS_SCHEDULED

    def test_default_method_is_payroll(self, tenant_a):
        Payout.objects.filter(tenant=tenant_a).delete()
        p = Payout.objects.create(
            tenant=tenant_a, rep_name="Default Method Rep", scheduled_on=timezone.localdate()
        )
        assert p.method == Payout.METHOD_PAYROLL

    def test_method_choices_contain_all_four(self):
        choices = dict(Payout.METHOD_CHOICES)
        assert Payout.METHOD_PAYROLL in choices
        assert Payout.METHOD_BANK in choices
        assert Payout.METHOD_CHECK in choices
        assert Payout.METHOD_WALLET in choices

    def test_status_choices_contain_all_five(self):
        choices = dict(Payout.STATUS_CHOICES)
        assert Payout.STATUS_SCHEDULED in choices
        assert Payout.STATUS_PROCESSING in choices
        assert Payout.STATUS_PAID in choices
        assert Payout.STATUS_FAILED in choices
        assert Payout.STATUS_CANCELED in choices

    def test_tenant_fk_set(self, payout_a, tenant_a):
        assert payout_a.tenant == tenant_a
