"""Tests for compensation views: CRUD for all 5 compensation models."""
import pytest
from django.urls import reverse
from django.utils import timezone

from apps.compensation.models import (
    Clawback, CommissionPlan, Earning, GlobalPlanVariation, Payout,
)


# ============================================================ CommissionPlan CRUD
@pytest.mark.django_db
class TestCommissionPlanCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("compensation:commissionplan_list"))
        assert resp.status_code == 200

    def test_list_context_has_plans(self, client_a, plan_a):
        resp = client_a.get(reverse("compensation:commissionplan_list"))
        assert "plans" in resp.context

    def test_list_seeded_object_appears(self, client_a, plan_a):
        resp = client_a.get(reverse("compensation:commissionplan_list"))
        pks = [p.pk for p in resp.context["plans"]]
        assert plan_a.pk in pks

    def test_list_has_type_choices(self, client_a):
        resp = client_a.get(reverse("compensation:commissionplan_list"))
        assert "type_choices" in resp.context

    def test_list_has_status_choices(self, client_a):
        resp = client_a.get(reverse("compensation:commissionplan_list"))
        assert "status_choices" in resp.context

    def test_list_search_filters_by_name(self, client_a, plan_a):
        resp = client_a.get(reverse("compensation:commissionplan_list") + "?q=Plan+Alpha")
        pks = [p.pk for p in resp.context["plans"]]
        assert plan_a.pk in pks

    def test_list_search_excludes_non_matches(self, client_a, plan_a):
        resp = client_a.get(reverse("compensation:commissionplan_list") + "?q=ZZZNOMATCH")
        pks = [p.pk for p in resp.context["plans"]]
        assert plan_a.pk not in pks

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("compensation:commissionplan_create"))
        assert resp.status_code == 200

    def test_create_post_creates_plan(self, client_a, tenant_a):
        before = CommissionPlan.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("compensation:commissionplan_create"), {
            "name": "New Test Plan",
            "code": "NTP",
            "plan_type": "flat",
            "status": "draft",
            "base_rate": "3.00",
            "target_quota": "50000.00",
            "effective_from": timezone.localdate().isoformat(),
            "effective_to": "",
            "description": "",
        })
        assert CommissionPlan.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a):
        client_a.post(reverse("compensation:commissionplan_create"), {
            "name": "Tenant Check Plan",
            "code": "TCP",
            "plan_type": "tiered",
            "status": "draft",
            "base_rate": "4.00",
            "target_quota": "75000.00",
            "effective_from": timezone.localdate().isoformat(),
            "effective_to": "",
            "description": "check tenant",
        })
        plan = CommissionPlan.objects.filter(description="check tenant").first()
        assert plan is not None
        assert plan.tenant == tenant_a

    def test_detail_200(self, client_a, plan_a):
        resp = client_a.get(reverse("compensation:commissionplan_detail", args=[plan_a.pk]))
        assert resp.status_code == 200

    def test_detail_context_has_obj(self, client_a, plan_a):
        resp = client_a.get(reverse("compensation:commissionplan_detail", args=[plan_a.pk]))
        assert resp.context["obj"] == plan_a

    def test_edit_get_200(self, client_a, plan_a):
        resp = client_a.get(reverse("compensation:commissionplan_edit", args=[plan_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_plan(self, client_a, plan_a):
        client_a.post(reverse("compensation:commissionplan_edit", args=[plan_a.pk]), {
            "name": "Updated Plan Alpha",
            "code": "ALPHA",
            "plan_type": "flat",
            "status": "active",
            "base_rate": "6.00",
            "target_quota": "100000.00",
            "effective_from": timezone.localdate().isoformat(),
            "effective_to": "",
            "description": "",
        })
        plan_a.refresh_from_db()
        assert plan_a.name == "Updated Plan Alpha"
        assert str(plan_a.base_rate) == "6.00"

    def test_delete_post_removes_plan(self, client_a, tenant_a):
        plan = CommissionPlan.objects.create(
            tenant=tenant_a, name="To Delete Plan", effective_from=timezone.localdate()
        )
        client_a.post(reverse("compensation:commissionplan_delete", args=[plan.pk]))
        assert not CommissionPlan.objects.filter(pk=plan.pk).exists()

    def test_delete_redirects_to_list(self, client_a, tenant_a):
        plan = CommissionPlan.objects.create(
            tenant=tenant_a, name="Redirect Plan", effective_from=timezone.localdate()
        )
        resp = client_a.post(reverse("compensation:commissionplan_delete", args=[plan.pk]))
        assert resp.status_code in (301, 302)


# ============================================================ Earning CRUD
@pytest.mark.django_db
class TestEarningCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("compensation:earning_list"))
        assert resp.status_code == 200

    def test_list_context_has_earnings(self, client_a, earning_a):
        resp = client_a.get(reverse("compensation:earning_list"))
        assert "earnings" in resp.context

    def test_list_seeded_object_appears(self, client_a, earning_a):
        resp = client_a.get(reverse("compensation:earning_list"))
        pks = [e.pk for e in resp.context["earnings"]]
        assert earning_a.pk in pks

    def test_list_has_status_choices(self, client_a):
        resp = client_a.get(reverse("compensation:earning_list"))
        assert "status_choices" in resp.context

    def test_list_has_plans_context(self, client_a):
        resp = client_a.get(reverse("compensation:earning_list"))
        assert "plans" in resp.context

    def test_list_search_filters_by_rep_name(self, client_a, earning_a):
        resp = client_a.get(reverse("compensation:earning_list") + "?q=Alice+Smith")
        pks = [e.pk for e in resp.context["earnings"]]
        assert earning_a.pk in pks

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("compensation:earning_create"))
        assert resp.status_code == 200

    def test_create_post_creates_earning(self, client_a, tenant_a):
        before = Earning.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("compensation:earning_create"), {
            "plan": "",
            "rep_name": "New Rep",
            "deal_reference": "DEAL-NEW",
            "deal_amount": "20000.00",
            "commission_amount": "1000.00",
            "status": "pending",
            "earned_on": timezone.localdate().isoformat(),
            "notes": "",
        })
        assert Earning.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a):
        client_a.post(reverse("compensation:earning_create"), {
            "plan": "",
            "rep_name": "Tenant Check Rep",
            "deal_reference": "DEAL-TC",
            "deal_amount": "15000.00",
            "commission_amount": "750.00",
            "status": "pending",
            "earned_on": timezone.localdate().isoformat(),
            "notes": "tenant-check",
        })
        e = Earning.objects.filter(notes="tenant-check").first()
        assert e is not None
        assert e.tenant == tenant_a

    def test_create_auto_numbers_earning(self, client_a, tenant_a):
        client_a.post(reverse("compensation:earning_create"), {
            "plan": "",
            "rep_name": "Numbered Rep",
            "deal_reference": "DEAL-NR",
            "deal_amount": "10000.00",
            "commission_amount": "500.00",
            "status": "pending",
            "earned_on": timezone.localdate().isoformat(),
            "notes": "auto-number-check",
        })
        e = Earning.objects.filter(notes="auto-number-check").first()
        assert e is not None
        assert e.number.startswith("EARN-")

    def test_detail_200(self, client_a, earning_a):
        resp = client_a.get(reverse("compensation:earning_detail", args=[earning_a.pk]))
        assert resp.status_code == 200

    def test_detail_context_has_obj(self, client_a, earning_a):
        resp = client_a.get(reverse("compensation:earning_detail", args=[earning_a.pk]))
        assert resp.context["obj"] == earning_a

    def test_edit_get_200(self, client_a, earning_a):
        resp = client_a.get(reverse("compensation:earning_edit", args=[earning_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_earning(self, client_a, earning_a):
        client_a.post(reverse("compensation:earning_edit", args=[earning_a.pk]), {
            "plan": "",
            "rep_name": "Updated Alice",
            "deal_reference": earning_a.deal_reference,
            "deal_amount": str(earning_a.deal_amount),
            "commission_amount": str(earning_a.commission_amount),
            "status": "approved",
            "earned_on": earning_a.earned_on.isoformat(),
            "notes": "",
        })
        earning_a.refresh_from_db()
        assert earning_a.rep_name == "Updated Alice"
        assert earning_a.status == Earning.STATUS_APPROVED

    def test_delete_post_removes_earning(self, client_a, tenant_a):
        Earning.objects.filter(tenant=tenant_a).delete()
        e = Earning.objects.create(
            tenant=tenant_a, rep_name="To Delete Rep", earned_on=timezone.localdate()
        )
        client_a.post(reverse("compensation:earning_delete", args=[e.pk]))
        assert not Earning.objects.filter(pk=e.pk).exists()


# ============================================================ Clawback CRUD
@pytest.mark.django_db
class TestClawbackCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("compensation:clawback_list"))
        assert resp.status_code == 200

    def test_list_context_has_clawbacks(self, client_a, clawback_a):
        resp = client_a.get(reverse("compensation:clawback_list"))
        assert "clawbacks" in resp.context

    def test_list_seeded_object_appears(self, client_a, clawback_a):
        resp = client_a.get(reverse("compensation:clawback_list"))
        pks = [c.pk for c in resp.context["clawbacks"]]
        assert clawback_a.pk in pks

    def test_list_has_reason_choices(self, client_a):
        resp = client_a.get(reverse("compensation:clawback_list"))
        assert "reason_choices" in resp.context

    def test_list_has_status_choices(self, client_a):
        resp = client_a.get(reverse("compensation:clawback_list"))
        assert "status_choices" in resp.context

    def test_list_search_filters_by_rep_name(self, client_a, clawback_a):
        resp = client_a.get(reverse("compensation:clawback_list") + "?q=Alice+Smith")
        pks = [c.pk for c in resp.context["clawbacks"]]
        assert clawback_a.pk in pks

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("compensation:clawback_create"))
        assert resp.status_code == 200

    def test_create_post_creates_clawback(self, client_a, tenant_a):
        before = Clawback.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("compensation:clawback_create"), {
            "earning": "",
            "rep_name": "New Rep Claw",
            "reason": "refund",
            "status": "open",
            "amount": "200.00",
            "effective_on": timezone.localdate().isoformat(),
            "notes": "",
        })
        assert Clawback.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a):
        client_a.post(reverse("compensation:clawback_create"), {
            "earning": "",
            "rep_name": "Tenant Claw Rep",
            "reason": "correction",
            "status": "open",
            "amount": "100.00",
            "effective_on": timezone.localdate().isoformat(),
            "notes": "claw-tenant-check",
        })
        cb = Clawback.objects.filter(notes="claw-tenant-check").first()
        assert cb is not None
        assert cb.tenant == tenant_a

    def test_detail_200(self, client_a, clawback_a):
        resp = client_a.get(reverse("compensation:clawback_detail", args=[clawback_a.pk]))
        assert resp.status_code == 200

    def test_detail_context_has_obj(self, client_a, clawback_a):
        resp = client_a.get(reverse("compensation:clawback_detail", args=[clawback_a.pk]))
        assert resp.context["obj"] == clawback_a

    def test_edit_get_200(self, client_a, clawback_a):
        resp = client_a.get(reverse("compensation:clawback_edit", args=[clawback_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_clawback(self, client_a, clawback_a):
        client_a.post(reverse("compensation:clawback_edit", args=[clawback_a.pk]), {
            "earning": "",
            "rep_name": "Updated Alice Claw",
            "reason": "refund",
            "status": "open",
            "amount": "600.00",
            "effective_on": clawback_a.effective_on.isoformat(),
            "notes": "",
        })
        clawback_a.refresh_from_db()
        assert clawback_a.rep_name == "Updated Alice Claw"
        assert str(clawback_a.amount) == "600.00"

    def test_delete_post_removes_clawback(self, client_a, tenant_a):
        cb = Clawback.objects.create(
            tenant=tenant_a, rep_name="To Delete Claw",
            amount="50.00", effective_on=timezone.localdate()
        )
        client_a.post(reverse("compensation:clawback_delete", args=[cb.pk]))
        assert not Clawback.objects.filter(pk=cb.pk).exists()


# ============================================================ GlobalPlanVariation CRUD
@pytest.mark.django_db
class TestGlobalPlanVariationCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("compensation:globalplanvariation_list"))
        assert resp.status_code == 200

    def test_list_context_has_variations(self, client_a, variation_a):
        resp = client_a.get(reverse("compensation:globalplanvariation_list"))
        assert "variations" in resp.context

    def test_list_seeded_object_appears(self, client_a, variation_a):
        resp = client_a.get(reverse("compensation:globalplanvariation_list"))
        pks = [v.pk for v in resp.context["variations"]]
        assert variation_a.pk in pks

    def test_list_has_currency_choices(self, client_a):
        resp = client_a.get(reverse("compensation:globalplanvariation_list"))
        assert "currency_choices" in resp.context

    def test_list_has_status_choices(self, client_a):
        resp = client_a.get(reverse("compensation:globalplanvariation_list"))
        assert "status_choices" in resp.context

    def test_list_has_plans_context(self, client_a):
        resp = client_a.get(reverse("compensation:globalplanvariation_list"))
        assert "plans" in resp.context

    def test_list_search_filters_by_region(self, client_a, variation_a):
        resp = client_a.get(reverse("compensation:globalplanvariation_list") + "?q=North+America")
        pks = [v.pk for v in resp.context["variations"]]
        assert variation_a.pk in pks

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("compensation:globalplanvariation_create"))
        assert resp.status_code == 200

    def test_create_post_creates_variation(self, client_a, tenant_a):
        before = GlobalPlanVariation.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("compensation:globalplanvariation_create"), {
            "plan": "",
            "region": "APAC",
            "currency": "AUD",
            "status": "active",
            "fx_rate": "1.500000",
            "local_quota": "120000.00",
            "rate_adjustment": "0.50",
            "effective_from": timezone.localdate().isoformat(),
            "notes": "",
        })
        assert GlobalPlanVariation.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a):
        client_a.post(reverse("compensation:globalplanvariation_create"), {
            "plan": "",
            "region": "Tenant Check Region",
            "currency": "GBP",
            "status": "active",
            "fx_rate": "0.780000",
            "local_quota": "90000.00",
            "rate_adjustment": "0.00",
            "effective_from": timezone.localdate().isoformat(),
            "notes": "var-tenant-check",
        })
        v = GlobalPlanVariation.objects.filter(notes="var-tenant-check").first()
        assert v is not None
        assert v.tenant == tenant_a

    def test_detail_200(self, client_a, variation_a):
        resp = client_a.get(reverse("compensation:globalplanvariation_detail", args=[variation_a.pk]))
        assert resp.status_code == 200

    def test_detail_context_has_obj(self, client_a, variation_a):
        resp = client_a.get(reverse("compensation:globalplanvariation_detail", args=[variation_a.pk]))
        assert resp.context["obj"] == variation_a

    def test_edit_get_200(self, client_a, variation_a):
        resp = client_a.get(reverse("compensation:globalplanvariation_edit", args=[variation_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_variation(self, client_a, variation_a):
        client_a.post(reverse("compensation:globalplanvariation_edit", args=[variation_a.pk]), {
            "plan": "",
            "region": "Updated North America",
            "currency": "USD",
            "status": "active",
            "fx_rate": "1.000000",
            "local_quota": "110000.00",
            "rate_adjustment": "0.50",
            "effective_from": variation_a.effective_from.isoformat(),
            "notes": "",
        })
        variation_a.refresh_from_db()
        assert variation_a.region == "Updated North America"

    def test_delete_post_removes_variation(self, client_a, tenant_a):
        v = GlobalPlanVariation.objects.create(
            tenant=tenant_a, region="To Delete Region", effective_from=timezone.localdate()
        )
        client_a.post(reverse("compensation:globalplanvariation_delete", args=[v.pk]))
        assert not GlobalPlanVariation.objects.filter(pk=v.pk).exists()


# ============================================================ Payout CRUD
@pytest.mark.django_db
class TestPayoutCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("compensation:payout_list"))
        assert resp.status_code == 200

    def test_list_context_has_payouts(self, client_a, payout_a):
        resp = client_a.get(reverse("compensation:payout_list"))
        assert "payouts" in resp.context

    def test_list_seeded_object_appears(self, client_a, payout_a):
        resp = client_a.get(reverse("compensation:payout_list"))
        pks = [p.pk for p in resp.context["payouts"]]
        assert payout_a.pk in pks

    def test_list_has_method_choices(self, client_a):
        resp = client_a.get(reverse("compensation:payout_list"))
        assert "method_choices" in resp.context

    def test_list_has_status_choices(self, client_a):
        resp = client_a.get(reverse("compensation:payout_list"))
        assert "status_choices" in resp.context

    def test_list_search_filters_by_rep_name(self, client_a, payout_a):
        resp = client_a.get(reverse("compensation:payout_list") + "?q=Alice+Smith")
        pks = [p.pk for p in resp.context["payouts"]]
        assert payout_a.pk in pks

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("compensation:payout_create"))
        assert resp.status_code == 200

    def test_create_post_creates_payout(self, client_a, tenant_a):
        before = Payout.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("compensation:payout_create"), {
            "rep_name": "New Payout Rep",
            "method": "payroll",
            "status": "scheduled",
            "gross_amount": "6000.00",
            "deductions": "600.00",
            "net_amount": "5400.00",
            "period_label": "2026-Q2",
            "scheduled_on": timezone.localdate().isoformat(),
            "reference": "",
            "notes": "",
        })
        assert Payout.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a):
        client_a.post(reverse("compensation:payout_create"), {
            "rep_name": "Tenant Payout Rep",
            "method": "bank_transfer",
            "status": "scheduled",
            "gross_amount": "4000.00",
            "deductions": "400.00",
            "net_amount": "3600.00",
            "period_label": "2026-Q3",
            "scheduled_on": timezone.localdate().isoformat(),
            "reference": "",
            "notes": "payout-tenant-check",
        })
        p = Payout.objects.filter(notes="payout-tenant-check").first()
        assert p is not None
        assert p.tenant == tenant_a

    def test_create_auto_numbers_payout(self, client_a, tenant_a):
        client_a.post(reverse("compensation:payout_create"), {
            "rep_name": "Numbered Payout Rep",
            "method": "payroll",
            "status": "scheduled",
            "gross_amount": "2000.00",
            "deductions": "200.00",
            "net_amount": "1800.00",
            "period_label": "2026-Q4",
            "scheduled_on": timezone.localdate().isoformat(),
            "reference": "",
            "notes": "auto-number-payout",
        })
        p = Payout.objects.filter(notes="auto-number-payout").first()
        assert p is not None
        assert p.number.startswith("PAY-")

    def test_detail_200(self, client_a, payout_a):
        resp = client_a.get(reverse("compensation:payout_detail", args=[payout_a.pk]))
        assert resp.status_code == 200

    def test_detail_context_has_obj(self, client_a, payout_a):
        resp = client_a.get(reverse("compensation:payout_detail", args=[payout_a.pk]))
        assert resp.context["obj"] == payout_a

    def test_edit_get_200(self, client_a, payout_a):
        resp = client_a.get(reverse("compensation:payout_edit", args=[payout_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_payout(self, client_a, payout_a):
        client_a.post(reverse("compensation:payout_edit", args=[payout_a.pk]), {
            "rep_name": "Updated Alice Payout",
            "method": "bank_transfer",
            "status": "scheduled",
            "gross_amount": "5500.00",
            "deductions": "550.00",
            "net_amount": "4950.00",
            "period_label": "2026-Q1",
            "scheduled_on": payout_a.scheduled_on.isoformat(),
            "reference": "",
            "notes": "",
        })
        payout_a.refresh_from_db()
        assert payout_a.rep_name == "Updated Alice Payout"
        assert payout_a.method == Payout.METHOD_BANK

    def test_delete_post_removes_payout(self, client_a, tenant_a):
        Payout.objects.filter(tenant=tenant_a).delete()
        p = Payout.objects.create(
            tenant=tenant_a, rep_name="To Delete Payout Rep",
            scheduled_on=timezone.localdate()
        )
        client_a.post(reverse("compensation:payout_delete", args=[p.pk]))
        assert not Payout.objects.filter(pk=p.pk).exists()

    def test_delete_redirects_to_list(self, client_a, tenant_a):
        Payout.objects.filter(tenant=tenant_a).delete()
        p = Payout.objects.create(
            tenant=tenant_a, rep_name="Redirect Payout Rep",
            scheduled_on=timezone.localdate()
        )
        resp = client_a.post(reverse("compensation:payout_delete", args=[p.pk]))
        assert resp.status_code in (301, 302)
