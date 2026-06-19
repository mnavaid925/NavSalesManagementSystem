"""Security tests: multi-tenant isolation and authorization for success module."""
import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from apps.success.models import (
    HealthScore, Renewal, OnboardingPlan, Advocacy, QBR,
)


# ============================================================ Anonymous redirects
@pytest.mark.django_db
class TestAnonymousRedirects:
    """Unauthenticated requests must be redirected, never served a 200."""

    def _anon(self):
        return Client()

    def test_healthscore_list_redirects(self):
        resp = self._anon().get(reverse("success:healthscore_list"))
        assert resp.status_code in (301, 302)

    def test_healthscore_create_redirects(self):
        resp = self._anon().get(reverse("success:healthscore_create"))
        assert resp.status_code in (301, 302)

    def test_renewal_list_redirects(self):
        resp = self._anon().get(reverse("success:renewal_list"))
        assert resp.status_code in (301, 302)

    def test_renewal_create_redirects(self):
        resp = self._anon().get(reverse("success:renewal_create"))
        assert resp.status_code in (301, 302)

    def test_onboardingplan_list_redirects(self):
        resp = self._anon().get(reverse("success:onboardingplan_list"))
        assert resp.status_code in (301, 302)

    def test_onboardingplan_create_redirects(self):
        resp = self._anon().get(reverse("success:onboardingplan_create"))
        assert resp.status_code in (301, 302)

    def test_advocacy_list_redirects(self):
        resp = self._anon().get(reverse("success:advocacy_list"))
        assert resp.status_code in (301, 302)

    def test_advocacy_create_redirects(self):
        resp = self._anon().get(reverse("success:advocacy_create"))
        assert resp.status_code in (301, 302)

    def test_qbr_list_redirects(self):
        resp = self._anon().get(reverse("success:qbr_list"))
        assert resp.status_code in (301, 302)

    def test_qbr_create_redirects(self):
        resp = self._anon().get(reverse("success:qbr_create"))
        assert resp.status_code in (301, 302)

    def test_anonymous_post_to_healthscore_delete_does_not_delete(self, tenant_a):
        hs = HealthScore.objects.create(
            tenant=tenant_a,
            account_name="Anon Delete Corp",
            last_reviewed=timezone.localdate()
        )
        resp = self._anon().post(reverse("success:healthscore_delete", args=[hs.pk]))
        assert resp.status_code in (301, 302)
        assert HealthScore.objects.filter(pk=hs.pk).exists()

    def test_anonymous_post_to_renewal_delete_does_not_delete(self, tenant_a):
        Renewal.objects.filter(tenant=tenant_a).delete()
        r = Renewal.objects.create(
            tenant=tenant_a, account_name="Anon Delete Renewal",
            renewal_date=timezone.localdate()
        )
        resp = self._anon().post(reverse("success:renewal_delete", args=[r.pk]))
        assert resp.status_code in (301, 302)
        assert Renewal.objects.filter(pk=r.pk).exists()

    def test_anonymous_post_to_qbr_delete_does_not_delete(self, tenant_a):
        qbr = QBR.objects.create(
            tenant=tenant_a,
            account_name="Anon Delete QBR Corp",
            period_label="2026-Q1",
            scheduled_on=timezone.localdate()
        )
        resp = self._anon().post(reverse("success:qbr_delete", args=[qbr.pk]))
        assert resp.status_code in (301, 302)
        assert QBR.objects.filter(pk=qbr.pk).exists()


# ============================================================ Non-admin rep blocked on write views
@pytest.mark.django_db
class TestRepBlockedFromWriteViews:
    """Users with is_tenant_admin=False must be blocked from write views."""

    def test_rep_cannot_create_healthscore(self, rep_client_a):
        resp = rep_client_a.get(reverse("success:healthscore_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_edit_healthscore(self, rep_client_a, healthscore_a):
        resp = rep_client_a.get(reverse("success:healthscore_edit", args=[healthscore_a.pk]))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_delete_healthscore(self, rep_client_a, healthscore_a):
        resp = rep_client_a.post(reverse("success:healthscore_delete", args=[healthscore_a.pk]))
        assert resp.status_code in (301, 302)
        assert HealthScore.objects.filter(pk=healthscore_a.pk).exists()

    def test_rep_cannot_create_renewal(self, rep_client_a):
        resp = rep_client_a.get(reverse("success:renewal_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_edit_renewal(self, rep_client_a, renewal_a):
        resp = rep_client_a.get(reverse("success:renewal_edit", args=[renewal_a.pk]))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_delete_renewal(self, rep_client_a, renewal_a):
        resp = rep_client_a.post(reverse("success:renewal_delete", args=[renewal_a.pk]))
        assert resp.status_code in (301, 302)
        assert Renewal.objects.filter(pk=renewal_a.pk).exists()

    def test_rep_cannot_create_onboardingplan(self, rep_client_a):
        resp = rep_client_a.get(reverse("success:onboardingplan_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_edit_onboardingplan(self, rep_client_a, onboardingplan_a):
        resp = rep_client_a.get(reverse("success:onboardingplan_edit", args=[onboardingplan_a.pk]))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_delete_onboardingplan(self, rep_client_a, onboardingplan_a):
        resp = rep_client_a.post(reverse("success:onboardingplan_delete", args=[onboardingplan_a.pk]))
        assert resp.status_code in (301, 302)
        assert OnboardingPlan.objects.filter(pk=onboardingplan_a.pk).exists()

    def test_rep_cannot_create_advocacy(self, rep_client_a):
        resp = rep_client_a.get(reverse("success:advocacy_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_edit_advocacy(self, rep_client_a, advocacy_a):
        resp = rep_client_a.get(reverse("success:advocacy_edit", args=[advocacy_a.pk]))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_delete_advocacy(self, rep_client_a, advocacy_a):
        resp = rep_client_a.post(reverse("success:advocacy_delete", args=[advocacy_a.pk]))
        assert resp.status_code in (301, 302)
        assert Advocacy.objects.filter(pk=advocacy_a.pk).exists()

    def test_rep_cannot_create_qbr(self, rep_client_a):
        resp = rep_client_a.get(reverse("success:qbr_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_edit_qbr(self, rep_client_a, qbr_a):
        resp = rep_client_a.get(reverse("success:qbr_edit", args=[qbr_a.pk]))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_delete_qbr(self, rep_client_a, qbr_a):
        resp = rep_client_a.post(reverse("success:qbr_delete", args=[qbr_a.pk]))
        assert resp.status_code in (301, 302)
        assert QBR.objects.filter(pk=qbr_a.pk).exists()

    def test_rep_can_view_healthscore_list(self, rep_client_a):
        """Reps can VIEW (read-only) list pages."""
        resp = rep_client_a.get(reverse("success:healthscore_list"))
        assert resp.status_code == 200

    def test_rep_can_view_renewal_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("success:renewal_list"))
        assert resp.status_code == 200

    def test_rep_can_view_onboardingplan_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("success:onboardingplan_list"))
        assert resp.status_code == 200

    def test_rep_can_view_advocacy_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("success:advocacy_list"))
        assert resp.status_code == 200

    def test_rep_can_view_qbr_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("success:qbr_list"))
        assert resp.status_code == 200

    def test_rep_can_view_healthscore_detail(self, rep_client_a, healthscore_a):
        resp = rep_client_a.get(reverse("success:healthscore_detail", args=[healthscore_a.pk]))
        assert resp.status_code == 200

    def test_rep_can_view_renewal_detail(self, rep_client_a, renewal_a):
        resp = rep_client_a.get(reverse("success:renewal_detail", args=[renewal_a.pk]))
        assert resp.status_code == 200

    def test_rep_can_view_qbr_detail(self, rep_client_a, qbr_a):
        resp = rep_client_a.get(reverse("success:qbr_detail", args=[qbr_a.pk]))
        assert resp.status_code == 200


# ============================================================ Cross-tenant isolation (IDOR -> 404)
@pytest.mark.django_db
class TestCrossTenantIsolation404:
    """Tenant A client must receive 404 on ALL Tenant B resource URLs."""

    # --- health scores ---
    def test_healthscore_detail_cross_tenant_404(self, client_a, healthscore_b):
        resp = client_a.get(reverse("success:healthscore_detail", args=[healthscore_b.pk]))
        assert resp.status_code == 404

    def test_healthscore_edit_cross_tenant_404(self, client_a, healthscore_b):
        resp = client_a.get(reverse("success:healthscore_edit", args=[healthscore_b.pk]))
        assert resp.status_code == 404

    def test_healthscore_delete_cross_tenant_404(self, client_a, healthscore_b):
        resp = client_a.post(reverse("success:healthscore_delete", args=[healthscore_b.pk]))
        assert resp.status_code == 404

    # --- renewals ---
    def test_renewal_detail_cross_tenant_404(self, client_a, renewal_b):
        resp = client_a.get(reverse("success:renewal_detail", args=[renewal_b.pk]))
        assert resp.status_code == 404

    def test_renewal_edit_cross_tenant_404(self, client_a, renewal_b):
        resp = client_a.get(reverse("success:renewal_edit", args=[renewal_b.pk]))
        assert resp.status_code == 404

    def test_renewal_delete_cross_tenant_404(self, client_a, renewal_b):
        resp = client_a.post(reverse("success:renewal_delete", args=[renewal_b.pk]))
        assert resp.status_code == 404

    # --- onboarding plans ---
    def test_onboardingplan_detail_cross_tenant_404(self, client_a, onboardingplan_b):
        resp = client_a.get(reverse("success:onboardingplan_detail", args=[onboardingplan_b.pk]))
        assert resp.status_code == 404

    def test_onboardingplan_edit_cross_tenant_404(self, client_a, onboardingplan_b):
        resp = client_a.get(reverse("success:onboardingplan_edit", args=[onboardingplan_b.pk]))
        assert resp.status_code == 404

    def test_onboardingplan_delete_cross_tenant_404(self, client_a, onboardingplan_b):
        resp = client_a.post(reverse("success:onboardingplan_delete", args=[onboardingplan_b.pk]))
        assert resp.status_code == 404

    # --- advocacy ---
    def test_advocacy_detail_cross_tenant_404(self, client_a, advocacy_b):
        resp = client_a.get(reverse("success:advocacy_detail", args=[advocacy_b.pk]))
        assert resp.status_code == 404

    def test_advocacy_edit_cross_tenant_404(self, client_a, advocacy_b):
        resp = client_a.get(reverse("success:advocacy_edit", args=[advocacy_b.pk]))
        assert resp.status_code == 404

    def test_advocacy_delete_cross_tenant_404(self, client_a, advocacy_b):
        resp = client_a.post(reverse("success:advocacy_delete", args=[advocacy_b.pk]))
        assert resp.status_code == 404

    # --- QBRs ---
    def test_qbr_detail_cross_tenant_404(self, client_a, qbr_b):
        resp = client_a.get(reverse("success:qbr_detail", args=[qbr_b.pk]))
        assert resp.status_code == 404

    def test_qbr_edit_cross_tenant_404(self, client_a, qbr_b):
        resp = client_a.get(reverse("success:qbr_edit", args=[qbr_b.pk]))
        assert resp.status_code == 404

    def test_qbr_delete_cross_tenant_404(self, client_a, qbr_b):
        resp = client_a.post(reverse("success:qbr_delete", args=[qbr_b.pk]))
        assert resp.status_code == 404


# ============================================================ List isolation
@pytest.mark.django_db
class TestListIsolation:
    """List views for Tenant A must never include Tenant B rows."""

    def test_healthscore_list_excludes_tenant_b(self, client_a, healthscore_a, healthscore_b):
        resp = client_a.get(reverse("success:healthscore_list"))
        pks = [h.pk for h in resp.context["healthscores"]]
        assert healthscore_a.pk in pks
        assert healthscore_b.pk not in pks

    def test_renewal_list_excludes_tenant_b(self, client_a, renewal_a, renewal_b):
        resp = client_a.get(reverse("success:renewal_list"))
        pks = [r.pk for r in resp.context["renewals"]]
        assert renewal_a.pk in pks
        assert renewal_b.pk not in pks

    def test_onboardingplan_list_excludes_tenant_b(self, client_a, onboardingplan_a, onboardingplan_b):
        resp = client_a.get(reverse("success:onboardingplan_list"))
        pks = [op.pk for op in resp.context["onboardingplans"]]
        assert onboardingplan_a.pk in pks
        assert onboardingplan_b.pk not in pks

    def test_advocacy_list_excludes_tenant_b(self, client_a, advocacy_a, advocacy_b):
        resp = client_a.get(reverse("success:advocacy_list"))
        pks = [a.pk for a in resp.context["advocacies"]]
        assert advocacy_a.pk in pks
        assert advocacy_b.pk not in pks

    def test_qbr_list_excludes_tenant_b(self, client_a, qbr_a, qbr_b):
        resp = client_a.get(reverse("success:qbr_list"))
        pks = [q.pk for q in resp.context["qbrs"]]
        assert qbr_a.pk in pks
        assert qbr_b.pk not in pks


# ============================================================ CSRF / anonymous POST
@pytest.mark.django_db
class TestCSRFAndAnonymousPost:
    """Anonymous POST to create/delete must redirect (not mutate data)."""

    def test_anon_post_healthscore_create_redirects(self):
        c = Client(enforce_csrf_checks=True)
        resp = c.post(reverse("success:healthscore_create"), {
            "account_name": "CSRF Corp",
            "owner": "",
            "score": "50",
            "risk_level": "medium",
            "trend": "stable",
            "arr": "0",
            "last_reviewed": timezone.localdate().isoformat(),
            "notes": "",
        })
        assert resp.status_code in (301, 302, 403)

    def test_anon_post_renewal_create_redirects(self):
        c = Client(enforce_csrf_checks=True)
        resp = c.post(reverse("success:renewal_create"), {
            "account_name": "CSRF Renewal Corp",
            "owner": "",
            "renewal_type": "renewal",
            "status": "open",
            "arr_current": "0",
            "arr_proposed": "0",
            "probability": "50",
            "renewal_date": timezone.localdate().isoformat(),
            "notes": "",
        })
        assert resp.status_code in (301, 302, 403)

    def test_anon_post_qbr_create_redirects(self):
        c = Client(enforce_csrf_checks=True)
        resp = c.post(reverse("success:qbr_create"), {
            "account_name": "CSRF QBR Corp",
            "period_label": "2026-Q1",
            "owner": "",
            "status": "scheduled",
            "sentiment": "neutral",
            "scheduled_on": timezone.localdate().isoformat(),
            "health_summary": "",
            "notes": "",
        })
        assert resp.status_code in (301, 302, 403)
