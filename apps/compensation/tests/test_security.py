"""Security tests: multi-tenant isolation and authorization for compensation module."""
import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from apps.compensation.models import (
    Clawback, CommissionPlan, Earning, GlobalPlanVariation, Payout,
)


# ============================================================ Anonymous redirects
@pytest.mark.django_db
class TestAnonymousRedirects:
    """Unauthenticated requests must be redirected, never served a 200."""

    def _anon(self):
        return Client()

    def test_commissionplan_list_redirects(self):
        resp = self._anon().get(reverse("compensation:commissionplan_list"))
        assert resp.status_code in (301, 302)

    def test_commissionplan_create_redirects(self):
        resp = self._anon().get(reverse("compensation:commissionplan_create"))
        assert resp.status_code in (301, 302)

    def test_earning_list_redirects(self):
        resp = self._anon().get(reverse("compensation:earning_list"))
        assert resp.status_code in (301, 302)

    def test_earning_create_redirects(self):
        resp = self._anon().get(reverse("compensation:earning_create"))
        assert resp.status_code in (301, 302)

    def test_clawback_list_redirects(self):
        resp = self._anon().get(reverse("compensation:clawback_list"))
        assert resp.status_code in (301, 302)

    def test_clawback_create_redirects(self):
        resp = self._anon().get(reverse("compensation:clawback_create"))
        assert resp.status_code in (301, 302)

    def test_globalplanvariation_list_redirects(self):
        resp = self._anon().get(reverse("compensation:globalplanvariation_list"))
        assert resp.status_code in (301, 302)

    def test_globalplanvariation_create_redirects(self):
        resp = self._anon().get(reverse("compensation:globalplanvariation_create"))
        assert resp.status_code in (301, 302)

    def test_payout_list_redirects(self):
        resp = self._anon().get(reverse("compensation:payout_list"))
        assert resp.status_code in (301, 302)

    def test_payout_create_redirects(self):
        resp = self._anon().get(reverse("compensation:payout_create"))
        assert resp.status_code in (301, 302)

    def test_anonymous_post_to_commissionplan_delete_does_not_delete(self, tenant_a):
        plan = CommissionPlan.objects.create(
            tenant=tenant_a, name="Anon Delete Guard", effective_from=timezone.localdate()
        )
        resp = self._anon().post(
            reverse("compensation:commissionplan_delete", args=[plan.pk])
        )
        assert resp.status_code in (301, 302)
        assert CommissionPlan.objects.filter(pk=plan.pk).exists()

    def test_anonymous_post_to_earning_delete_does_not_delete(self, tenant_a):
        Earning.objects.filter(tenant=tenant_a).delete()
        e = Earning.objects.create(
            tenant=tenant_a, rep_name="Anon Rep", earned_on=timezone.localdate()
        )
        resp = self._anon().post(reverse("compensation:earning_delete", args=[e.pk]))
        assert resp.status_code in (301, 302)
        assert Earning.objects.filter(pk=e.pk).exists()

    def test_anonymous_post_to_payout_delete_does_not_delete(self, tenant_a):
        Payout.objects.filter(tenant=tenant_a).delete()
        p = Payout.objects.create(
            tenant=tenant_a, rep_name="Anon Payout Rep", scheduled_on=timezone.localdate()
        )
        resp = self._anon().post(reverse("compensation:payout_delete", args=[p.pk]))
        assert resp.status_code in (301, 302)
        assert Payout.objects.filter(pk=p.pk).exists()


# ============================================================ Non-admin rep blocked on write views
@pytest.mark.django_db
class TestRepBlockedFromWriteViews:
    """Sales reps (is_tenant_admin=False) must be blocked from write views."""

    def test_rep_cannot_create_commissionplan(self, rep_client_a):
        resp = rep_client_a.get(reverse("compensation:commissionplan_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_edit_commissionplan(self, rep_client_a, plan_a):
        resp = rep_client_a.get(reverse("compensation:commissionplan_edit", args=[plan_a.pk]))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_delete_commissionplan(self, rep_client_a, plan_a):
        resp = rep_client_a.post(reverse("compensation:commissionplan_delete", args=[plan_a.pk]))
        # Blocked: redirect away, plan still exists
        assert resp.status_code in (301, 302)
        assert CommissionPlan.objects.filter(pk=plan_a.pk).exists()

    def test_rep_cannot_create_earning(self, rep_client_a):
        resp = rep_client_a.get(reverse("compensation:earning_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_edit_earning(self, rep_client_a, earning_a):
        resp = rep_client_a.get(reverse("compensation:earning_edit", args=[earning_a.pk]))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_delete_earning(self, rep_client_a, earning_a):
        resp = rep_client_a.post(reverse("compensation:earning_delete", args=[earning_a.pk]))
        assert resp.status_code in (301, 302)
        assert Earning.objects.filter(pk=earning_a.pk).exists()

    def test_rep_cannot_create_clawback(self, rep_client_a):
        resp = rep_client_a.get(reverse("compensation:clawback_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_globalplanvariation(self, rep_client_a):
        resp = rep_client_a.get(reverse("compensation:globalplanvariation_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_payout(self, rep_client_a):
        resp = rep_client_a.get(reverse("compensation:payout_create"))
        assert resp.status_code in (301, 302)

    def test_rep_can_view_commissionplan_list(self, rep_client_a):
        """Reps can VIEW (read-only) list pages."""
        resp = rep_client_a.get(reverse("compensation:commissionplan_list"))
        assert resp.status_code == 200

    def test_rep_can_view_earning_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("compensation:earning_list"))
        assert resp.status_code == 200

    def test_rep_can_view_payout_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("compensation:payout_list"))
        assert resp.status_code == 200


# ============================================================ Cross-tenant isolation (IDOR → 404)
@pytest.mark.django_db
class TestCrossTenantIsolation404:
    """Tenant A client must receive 404 on ALL Tenant B resource URLs."""

    # --- commission plans ---
    def test_commissionplan_detail_cross_tenant_404(self, client_a, plan_b):
        resp = client_a.get(reverse("compensation:commissionplan_detail", args=[plan_b.pk]))
        assert resp.status_code == 404

    def test_commissionplan_edit_cross_tenant_404(self, client_a, plan_b):
        resp = client_a.get(reverse("compensation:commissionplan_edit", args=[plan_b.pk]))
        assert resp.status_code == 404

    def test_commissionplan_delete_cross_tenant_404(self, client_a, plan_b):
        resp = client_a.post(reverse("compensation:commissionplan_delete", args=[plan_b.pk]))
        assert resp.status_code == 404

    # --- earnings ---
    def test_earning_detail_cross_tenant_404(self, client_a, earning_b):
        resp = client_a.get(reverse("compensation:earning_detail", args=[earning_b.pk]))
        assert resp.status_code == 404

    def test_earning_edit_cross_tenant_404(self, client_a, earning_b):
        resp = client_a.get(reverse("compensation:earning_edit", args=[earning_b.pk]))
        assert resp.status_code == 404

    def test_earning_delete_cross_tenant_404(self, client_a, earning_b):
        resp = client_a.post(reverse("compensation:earning_delete", args=[earning_b.pk]))
        assert resp.status_code == 404

    # --- clawbacks ---
    def test_clawback_detail_cross_tenant_404(self, client_a, clawback_b):
        resp = client_a.get(reverse("compensation:clawback_detail", args=[clawback_b.pk]))
        assert resp.status_code == 404

    def test_clawback_edit_cross_tenant_404(self, client_a, clawback_b):
        resp = client_a.get(reverse("compensation:clawback_edit", args=[clawback_b.pk]))
        assert resp.status_code == 404

    def test_clawback_delete_cross_tenant_404(self, client_a, clawback_b):
        resp = client_a.post(reverse("compensation:clawback_delete", args=[clawback_b.pk]))
        assert resp.status_code == 404

    # --- global plan variations ---
    def test_globalplanvariation_detail_cross_tenant_404(self, client_a, variation_b):
        resp = client_a.get(reverse("compensation:globalplanvariation_detail", args=[variation_b.pk]))
        assert resp.status_code == 404

    def test_globalplanvariation_edit_cross_tenant_404(self, client_a, variation_b):
        resp = client_a.get(reverse("compensation:globalplanvariation_edit", args=[variation_b.pk]))
        assert resp.status_code == 404

    def test_globalplanvariation_delete_cross_tenant_404(self, client_a, variation_b):
        resp = client_a.post(reverse("compensation:globalplanvariation_delete", args=[variation_b.pk]))
        assert resp.status_code == 404

    # --- payouts ---
    def test_payout_detail_cross_tenant_404(self, client_a, payout_b):
        resp = client_a.get(reverse("compensation:payout_detail", args=[payout_b.pk]))
        assert resp.status_code == 404

    def test_payout_edit_cross_tenant_404(self, client_a, payout_b):
        resp = client_a.get(reverse("compensation:payout_edit", args=[payout_b.pk]))
        assert resp.status_code == 404

    def test_payout_delete_cross_tenant_404(self, client_a, payout_b):
        resp = client_a.post(reverse("compensation:payout_delete", args=[payout_b.pk]))
        assert resp.status_code == 404


# ============================================================ List isolation
@pytest.mark.django_db
class TestListIsolation:
    """List views for Tenant A must never include Tenant B rows."""

    def test_commissionplan_list_excludes_tenant_b(self, client_a, plan_a, plan_b):
        resp = client_a.get(reverse("compensation:commissionplan_list"))
        pks = [p.pk for p in resp.context["plans"]]
        assert plan_a.pk in pks
        assert plan_b.pk not in pks

    def test_earning_list_excludes_tenant_b(self, client_a, earning_a, earning_b):
        resp = client_a.get(reverse("compensation:earning_list"))
        pks = [e.pk for e in resp.context["earnings"]]
        assert earning_a.pk in pks
        assert earning_b.pk not in pks

    def test_clawback_list_excludes_tenant_b(self, client_a, clawback_a, clawback_b):
        resp = client_a.get(reverse("compensation:clawback_list"))
        pks = [c.pk for c in resp.context["clawbacks"]]
        assert clawback_a.pk in pks
        assert clawback_b.pk not in pks

    def test_globalplanvariation_list_excludes_tenant_b(self, client_a, variation_a, variation_b):
        resp = client_a.get(reverse("compensation:globalplanvariation_list"))
        pks = [v.pk for v in resp.context["variations"]]
        assert variation_a.pk in pks
        assert variation_b.pk not in pks

    def test_payout_list_excludes_tenant_b(self, client_a, payout_a, payout_b):
        resp = client_a.get(reverse("compensation:payout_list"))
        pks = [p.pk for p in resp.context["payouts"]]
        assert payout_a.pk in pks
        assert payout_b.pk not in pks


# ============================================================ CSRF / anonymous POST
@pytest.mark.django_db
class TestCSRFAndAnonymousPost:
    """Anonymous POST to create/delete must redirect (not mutate data)."""

    def test_anon_post_commissionplan_create_redirects(self):
        c = Client(enforce_csrf_checks=True)
        resp = c.post(reverse("compensation:commissionplan_create"), {
            "name": "CSRF Plan", "code": "", "plan_type": "flat", "status": "draft",
            "base_rate": "0", "target_quota": "0",
            "effective_from": timezone.localdate().isoformat(),
        })
        assert resp.status_code in (301, 302, 403)

    def test_anon_post_payout_create_redirects(self):
        c = Client(enforce_csrf_checks=True)
        resp = c.post(reverse("compensation:payout_create"), {
            "rep_name": "CSRF Payout Rep", "method": "payroll", "status": "scheduled",
            "gross_amount": "1000", "deductions": "100", "net_amount": "900",
            "scheduled_on": timezone.localdate().isoformat(),
        })
        assert resp.status_code in (301, 302, 403)
