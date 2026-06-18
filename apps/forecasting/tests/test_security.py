"""Security tests: multi-tenant isolation and authorization enforcement for forecasting."""
from decimal import Decimal

import pytest
from django.test import Client
from django.urls import reverse

from apps.forecasting.models import (
    Forecast, ForecastAccuracy, ForecastAdjustment, ForecastCategory, Quota,
)


# ============================================================ Anonymous redirects
@pytest.mark.django_db
class TestAnonymousRedirects:
    """All list and write views must redirect anonymous users."""

    def _anon(self):
        return Client()

    def test_forecastcategory_list_redirects(self):
        resp = self._anon().get(reverse("forecasting:forecastcategory_list"))
        assert resp.status_code in (301, 302)

    def test_forecastcategory_create_redirects(self):
        resp = self._anon().get(reverse("forecasting:forecastcategory_create"))
        assert resp.status_code in (301, 302)

    def test_forecast_list_redirects(self):
        resp = self._anon().get(reverse("forecasting:forecast_list"))
        assert resp.status_code in (301, 302)

    def test_forecast_create_redirects(self):
        resp = self._anon().get(reverse("forecasting:forecast_create"))
        assert resp.status_code in (301, 302)

    def test_quota_list_redirects(self):
        resp = self._anon().get(reverse("forecasting:quota_list"))
        assert resp.status_code in (301, 302)

    def test_quota_create_redirects(self):
        resp = self._anon().get(reverse("forecasting:quota_create"))
        assert resp.status_code in (301, 302)

    def test_forecastadjustment_list_redirects(self):
        resp = self._anon().get(reverse("forecasting:forecastadjustment_list"))
        assert resp.status_code in (301, 302)

    def test_forecastadjustment_create_redirects(self):
        resp = self._anon().get(reverse("forecasting:forecastadjustment_create"))
        assert resp.status_code in (301, 302)

    def test_forecastaccuracy_list_redirects(self):
        resp = self._anon().get(reverse("forecasting:forecastaccuracy_list"))
        assert resp.status_code in (301, 302)

    def test_forecastaccuracy_create_redirects(self):
        resp = self._anon().get(reverse("forecasting:forecastaccuracy_create"))
        assert resp.status_code in (301, 302)


# ============================================================ Anonymous POST (no mutation)
@pytest.mark.django_db
class TestAnonymousPostNoMutation:
    """Anonymous POSTs to create/delete must not mutate data."""

    def test_anonymous_cannot_create_forecast_category(self, tenant_a):
        c = Client()
        before = ForecastCategory.objects.filter(tenant=tenant_a).count()
        resp = c.post(reverse("forecasting:forecastcategory_create"), {
            "name": "Anon Cat",
            "commitment": "pipeline",
            "probability": 40,
            "weight": "1.00",
            "is_active": True,
        })
        assert resp.status_code in (301, 302)
        assert ForecastCategory.objects.filter(tenant=tenant_a).count() == before

    def test_anonymous_cannot_delete_forecast(self, tenant_a):
        fc = Forecast.objects.create(tenant=tenant_a, name="Anon Delete Test")
        c = Client()
        resp = c.post(reverse("forecasting:forecast_delete", args=[fc.pk]))
        assert resp.status_code in (301, 302)
        # Object still exists
        assert Forecast.objects.filter(pk=fc.pk).exists()

    def test_anonymous_cannot_delete_quota(self, tenant_a):
        q = Quota.objects.create(tenant=tenant_a, owner_name="Anon Quota")
        c = Client()
        resp = c.post(reverse("forecasting:quota_delete", args=[q.pk]))
        assert resp.status_code in (301, 302)
        assert Quota.objects.filter(pk=q.pk).exists()

    def test_anonymous_cannot_delete_adjustment(self, tenant_a, forecast_a):
        adj = ForecastAdjustment.objects.create(
            tenant=tenant_a, forecast=forecast_a, amount="100.00"
        )
        c = Client()
        resp = c.post(reverse("forecasting:forecastadjustment_delete", args=[adj.pk]))
        assert resp.status_code in (301, 302)
        assert ForecastAdjustment.objects.filter(pk=adj.pk).exists()

    def test_anonymous_cannot_delete_accuracy(self, tenant_a):
        acc = ForecastAccuracy.objects.create(
            tenant=tenant_a,
            forecasted_amount=Decimal("100.00"),
            actual_amount=Decimal("90.00"),
            accuracy_pct=Decimal("90.00"),
        )
        c = Client()
        resp = c.post(reverse("forecasting:forecastaccuracy_delete", args=[acc.pk]))
        assert resp.status_code in (301, 302)
        assert ForecastAccuracy.objects.filter(pk=acc.pk).exists()


# ============================================================ Rep blocked from write views
@pytest.mark.django_db
class TestRepBlockedFromWriteViews:
    """Non-admin reps are blocked from all create/edit/delete views."""

    def test_rep_cannot_create_forecast_category(self, rep_client_a):
        resp = rep_client_a.get(reverse("forecasting:forecastcategory_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_forecast(self, rep_client_a):
        resp = rep_client_a.get(reverse("forecasting:forecast_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_quota(self, rep_client_a):
        resp = rep_client_a.get(reverse("forecasting:quota_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_adjustment(self, rep_client_a):
        resp = rep_client_a.get(reverse("forecasting:forecastadjustment_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_accuracy(self, rep_client_a):
        resp = rep_client_a.get(reverse("forecasting:forecastaccuracy_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_edit_forecast_category(self, rep_client_a, category_a):
        resp = rep_client_a.get(reverse("forecasting:forecastcategory_edit", args=[category_a.pk]))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_edit_forecast(self, rep_client_a, forecast_a):
        resp = rep_client_a.get(reverse("forecasting:forecast_edit", args=[forecast_a.pk]))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_delete_forecast(self, rep_client_a, tenant_a):
        fc = Forecast.objects.create(tenant=tenant_a, name="Rep Delete Test")
        before_count = Forecast.objects.filter(tenant=tenant_a).count()
        resp = rep_client_a.post(reverse("forecasting:forecast_delete", args=[fc.pk]))
        # Should be redirected, object should still exist
        assert resp.status_code in (301, 302)
        assert Forecast.objects.filter(pk=fc.pk).exists()

    def test_rep_cannot_delete_quota(self, rep_client_a, tenant_a):
        q = Quota.objects.create(tenant=tenant_a, owner_name="Rep Del Quota")
        resp = rep_client_a.post(reverse("forecasting:quota_delete", args=[q.pk]))
        assert resp.status_code in (301, 302)
        assert Quota.objects.filter(pk=q.pk).exists()

    def test_rep_can_view_list_pages(self, rep_client_a):
        """Reps can VIEW (read-only) list pages."""
        resp = rep_client_a.get(reverse("forecasting:forecastcategory_list"))
        assert resp.status_code == 200

    def test_rep_can_view_forecast_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("forecasting:forecast_list"))
        assert resp.status_code == 200

    def test_rep_can_view_quota_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("forecasting:quota_list"))
        assert resp.status_code == 200


# ============================================================ Cross-tenant isolation (IDOR protection)
@pytest.mark.django_db
class TestCrossTenantIsolation404:
    """Tenant A must receive 404 on ALL Tenant B resource URLs."""

    # --- ForecastCategory
    def test_forecastcategory_detail_cross_tenant_404(self, client_a, category_b):
        resp = client_a.get(reverse("forecasting:forecastcategory_detail", args=[category_b.pk]))
        assert resp.status_code == 404

    def test_forecastcategory_edit_cross_tenant_404(self, client_a, category_b):
        resp = client_a.get(reverse("forecasting:forecastcategory_edit", args=[category_b.pk]))
        assert resp.status_code == 404

    def test_forecastcategory_delete_cross_tenant_404(self, client_a, category_b):
        resp = client_a.post(reverse("forecasting:forecastcategory_delete", args=[category_b.pk]))
        assert resp.status_code == 404

    # --- Forecast
    def test_forecast_detail_cross_tenant_404(self, client_a, forecast_b):
        resp = client_a.get(reverse("forecasting:forecast_detail", args=[forecast_b.pk]))
        assert resp.status_code == 404

    def test_forecast_edit_cross_tenant_404(self, client_a, forecast_b):
        resp = client_a.get(reverse("forecasting:forecast_edit", args=[forecast_b.pk]))
        assert resp.status_code == 404

    def test_forecast_delete_cross_tenant_404(self, client_a, forecast_b):
        resp = client_a.post(reverse("forecasting:forecast_delete", args=[forecast_b.pk]))
        assert resp.status_code == 404

    # --- Quota
    def test_quota_detail_cross_tenant_404(self, client_a, quota_b):
        resp = client_a.get(reverse("forecasting:quota_detail", args=[quota_b.pk]))
        assert resp.status_code == 404

    def test_quota_edit_cross_tenant_404(self, client_a, quota_b):
        resp = client_a.get(reverse("forecasting:quota_edit", args=[quota_b.pk]))
        assert resp.status_code == 404

    def test_quota_delete_cross_tenant_404(self, client_a, quota_b):
        resp = client_a.post(reverse("forecasting:quota_delete", args=[quota_b.pk]))
        assert resp.status_code == 404

    # --- ForecastAdjustment
    def test_forecastadjustment_detail_cross_tenant_404(self, client_a, adjustment_b):
        resp = client_a.get(reverse("forecasting:forecastadjustment_detail", args=[adjustment_b.pk]))
        assert resp.status_code == 404

    def test_forecastadjustment_edit_cross_tenant_404(self, client_a, adjustment_b):
        resp = client_a.get(reverse("forecasting:forecastadjustment_edit", args=[adjustment_b.pk]))
        assert resp.status_code == 404

    def test_forecastadjustment_delete_cross_tenant_404(self, client_a, adjustment_b):
        resp = client_a.post(reverse("forecasting:forecastadjustment_delete", args=[adjustment_b.pk]))
        assert resp.status_code == 404

    # --- ForecastAccuracy
    def test_forecastaccuracy_detail_cross_tenant_404(self, client_a, accuracy_b):
        resp = client_a.get(reverse("forecasting:forecastaccuracy_detail", args=[accuracy_b.pk]))
        assert resp.status_code == 404

    def test_forecastaccuracy_edit_cross_tenant_404(self, client_a, accuracy_b):
        resp = client_a.get(reverse("forecasting:forecastaccuracy_edit", args=[accuracy_b.pk]))
        assert resp.status_code == 404

    def test_forecastaccuracy_delete_cross_tenant_404(self, client_a, accuracy_b):
        resp = client_a.post(reverse("forecasting:forecastaccuracy_delete", args=[accuracy_b.pk]))
        assert resp.status_code == 404


# ============================================================ List isolation
@pytest.mark.django_db
class TestListIsolation:
    """List views for Tenant A must never include Tenant B rows."""

    def test_forecastcategory_list_excludes_tenant_b(self, client_a, category_a, category_b):
        resp = client_a.get(reverse("forecasting:forecastcategory_list"))
        pks = [c.pk for c in resp.context["categories"]]
        assert category_a.pk in pks
        assert category_b.pk not in pks

    def test_forecast_list_excludes_tenant_b(self, client_a, forecast_a, forecast_b):
        resp = client_a.get(reverse("forecasting:forecast_list"))
        pks = [f.pk for f in resp.context["forecasts"]]
        assert forecast_a.pk in pks
        assert forecast_b.pk not in pks

    def test_quota_list_excludes_tenant_b(self, client_a, quota_a, quota_b):
        resp = client_a.get(reverse("forecasting:quota_list"))
        pks = [q.pk for q in resp.context["quotas"]]
        assert quota_a.pk in pks
        assert quota_b.pk not in pks

    def test_forecastadjustment_list_excludes_tenant_b(self, client_a, adjustment_a, adjustment_b):
        resp = client_a.get(reverse("forecasting:forecastadjustment_list"))
        pks = [a.pk for a in resp.context["adjustments"]]
        assert adjustment_a.pk in pks
        assert adjustment_b.pk not in pks

    def test_forecastaccuracy_list_excludes_tenant_b(self, client_a, accuracy_a, accuracy_b):
        resp = client_a.get(reverse("forecasting:forecastaccuracy_list"))
        pks = [r.pk for r in resp.context["records"]]
        assert accuracy_a.pk in pks
        assert accuracy_b.pk not in pks


# ============================================================ CSRF enforcement
@pytest.mark.django_db
class TestCSRFEnforcement:
    """CSRF is enforced for mutation endpoints when not logged in."""

    def test_anonymous_post_to_create_forecast_category_blocked(self):
        c = Client(enforce_csrf_checks=True)
        resp = c.post(reverse("forecasting:forecastcategory_create"), {
            "name": "CSRF Test",
            "commitment": "pipeline",
            "probability": 40,
            "weight": "1.00",
        })
        # Either CSRF rejected (403) or redirect to login (302)
        assert resp.status_code in (301, 302, 403)

    def test_anonymous_post_to_delete_forecast_blocked(self, tenant_a):
        fc = Forecast.objects.create(tenant=tenant_a, name="CSRF Delete Test")
        c = Client(enforce_csrf_checks=True)
        resp = c.post(reverse("forecasting:forecast_delete", args=[fc.pk]))
        assert resp.status_code in (301, 302, 403)
        # Object should still exist
        assert Forecast.objects.filter(pk=fc.pk).exists()
