"""Security tests: multi-tenant isolation, auth enforcement, and CSRF for orders."""
import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from apps.orders.models import (
    Fulfillment, Order, OrderAmendment, OrderLine, RevenueSchedule,
)


# ══════════════════════════════════════════════════════════════ Anonymous redirects
@pytest.mark.django_db
class TestAnonymousRedirects:
    """Anonymous users must be redirected to login for ALL orders views."""

    def _anon(self):
        return Client()

    def test_order_list_redirects_anonymous(self):
        resp = self._anon().get(reverse("orders:order_list"))
        assert resp.status_code in (301, 302)

    def test_order_detail_redirects_anonymous(self, order_a):
        resp = self._anon().get(reverse("orders:order_detail", args=[order_a.pk]))
        assert resp.status_code in (301, 302)

    def test_order_create_redirects_anonymous(self):
        resp = self._anon().get(reverse("orders:order_create"))
        assert resp.status_code in (301, 302)

    def test_order_edit_redirects_anonymous(self, order_a):
        resp = self._anon().get(reverse("orders:order_edit", args=[order_a.pk]))
        assert resp.status_code in (301, 302)

    def test_orderline_list_redirects_anonymous(self):
        resp = self._anon().get(reverse("orders:orderline_list"))
        assert resp.status_code in (301, 302)

    def test_orderline_create_redirects_anonymous(self):
        resp = self._anon().get(reverse("orders:orderline_create"))
        assert resp.status_code in (301, 302)

    def test_fulfillment_list_redirects_anonymous(self):
        resp = self._anon().get(reverse("orders:fulfillment_list"))
        assert resp.status_code in (301, 302)

    def test_fulfillment_create_redirects_anonymous(self):
        resp = self._anon().get(reverse("orders:fulfillment_create"))
        assert resp.status_code in (301, 302)

    def test_orderamendment_list_redirects_anonymous(self):
        resp = self._anon().get(reverse("orders:orderamendment_list"))
        assert resp.status_code in (301, 302)

    def test_orderamendment_create_redirects_anonymous(self):
        resp = self._anon().get(reverse("orders:orderamendment_create"))
        assert resp.status_code in (301, 302)

    def test_revenueschedule_list_redirects_anonymous(self):
        resp = self._anon().get(reverse("orders:revenueschedule_list"))
        assert resp.status_code in (301, 302)

    def test_revenueschedule_create_redirects_anonymous(self):
        resp = self._anon().get(reverse("orders:revenueschedule_create"))
        assert resp.status_code in (301, 302)


# ══════════════════════════════════════════════════════════════ Anonymous POST → not mutated
@pytest.mark.django_db
class TestAnonymousPostCannotMutate:
    """Anonymous POST to delete/create must redirect and NOT mutate the database."""

    def test_anonymous_cannot_delete_order(self, order_a):
        c = Client()
        resp = c.post(reverse("orders:order_delete", args=[order_a.pk]))
        assert resp.status_code in (301, 302)
        assert Order.objects.filter(pk=order_a.pk).exists()

    def test_anonymous_cannot_delete_orderline(self, orderline_a):
        c = Client()
        resp = c.post(reverse("orders:orderline_delete", args=[orderline_a.pk]))
        assert resp.status_code in (301, 302)
        assert OrderLine.objects.filter(pk=orderline_a.pk).exists()

    def test_anonymous_cannot_delete_fulfillment(self, fulfillment_a):
        c = Client()
        resp = c.post(reverse("orders:fulfillment_delete", args=[fulfillment_a.pk]))
        assert resp.status_code in (301, 302)
        assert Fulfillment.objects.filter(pk=fulfillment_a.pk).exists()

    def test_anonymous_cannot_delete_amendment(self, amendment_a):
        c = Client()
        resp = c.post(reverse("orders:orderamendment_delete", args=[amendment_a.pk]))
        assert resp.status_code in (301, 302)
        assert OrderAmendment.objects.filter(pk=amendment_a.pk).exists()

    def test_anonymous_cannot_delete_revenueschedule(self, revenueschedule_a):
        c = Client()
        resp = c.post(reverse("orders:revenueschedule_delete", args=[revenueschedule_a.pk]))
        assert resp.status_code in (301, 302)
        assert RevenueSchedule.objects.filter(pk=revenueschedule_a.pk).exists()


# ══════════════════════════════════════════════════════════════ Rep (non-admin) blocked from write views
@pytest.mark.django_db
class TestRepBlockedFromWriteViews:
    """Non-admin sales rep must be blocked (redirect) from all write views."""

    def test_rep_cannot_create_order(self, rep_client_a):
        resp = rep_client_a.get(reverse("orders:order_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_edit_order(self, rep_client_a, order_a):
        resp = rep_client_a.get(reverse("orders:order_edit", args=[order_a.pk]))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_delete_order(self, rep_client_a, order_a):
        resp = rep_client_a.post(reverse("orders:order_delete", args=[order_a.pk]))
        assert resp.status_code in (301, 302)
        assert Order.objects.filter(pk=order_a.pk).exists()

    def test_rep_cannot_create_orderline(self, rep_client_a):
        resp = rep_client_a.get(reverse("orders:orderline_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_edit_orderline(self, rep_client_a, orderline_a):
        resp = rep_client_a.get(reverse("orders:orderline_edit", args=[orderline_a.pk]))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_delete_orderline(self, rep_client_a, orderline_a):
        resp = rep_client_a.post(reverse("orders:orderline_delete", args=[orderline_a.pk]))
        assert resp.status_code in (301, 302)
        assert OrderLine.objects.filter(pk=orderline_a.pk).exists()

    def test_rep_cannot_create_fulfillment(self, rep_client_a):
        resp = rep_client_a.get(reverse("orders:fulfillment_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_edit_fulfillment(self, rep_client_a, fulfillment_a):
        resp = rep_client_a.get(reverse("orders:fulfillment_edit", args=[fulfillment_a.pk]))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_delete_fulfillment(self, rep_client_a, fulfillment_a):
        resp = rep_client_a.post(reverse("orders:fulfillment_delete", args=[fulfillment_a.pk]))
        assert resp.status_code in (301, 302)
        assert Fulfillment.objects.filter(pk=fulfillment_a.pk).exists()

    def test_rep_cannot_create_amendment(self, rep_client_a):
        resp = rep_client_a.get(reverse("orders:orderamendment_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_edit_amendment(self, rep_client_a, amendment_a):
        resp = rep_client_a.get(reverse("orders:orderamendment_edit", args=[amendment_a.pk]))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_delete_amendment(self, rep_client_a, amendment_a):
        resp = rep_client_a.post(reverse("orders:orderamendment_delete", args=[amendment_a.pk]))
        assert resp.status_code in (301, 302)
        assert OrderAmendment.objects.filter(pk=amendment_a.pk).exists()

    def test_rep_cannot_create_revenueschedule(self, rep_client_a):
        resp = rep_client_a.get(reverse("orders:revenueschedule_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_edit_revenueschedule(self, rep_client_a, revenueschedule_a):
        resp = rep_client_a.get(reverse("orders:revenueschedule_edit", args=[revenueschedule_a.pk]))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_delete_revenueschedule(self, rep_client_a, revenueschedule_a):
        resp = rep_client_a.post(reverse("orders:revenueschedule_delete", args=[revenueschedule_a.pk]))
        assert resp.status_code in (301, 302)
        assert RevenueSchedule.objects.filter(pk=revenueschedule_a.pk).exists()

    def test_rep_can_view_order_list(self, rep_client_a):
        """Reps can VIEW read-only list pages."""
        resp = rep_client_a.get(reverse("orders:order_list"))
        assert resp.status_code == 200

    def test_rep_can_view_order_detail(self, rep_client_a, order_a):
        resp = rep_client_a.get(reverse("orders:order_detail", args=[order_a.pk]))
        assert resp.status_code == 200

    def test_rep_can_view_fulfillment_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("orders:fulfillment_list"))
        assert resp.status_code == 200


# ══════════════════════════════════════════════════════════════ Cross-tenant IDOR → 404
@pytest.mark.django_db
class TestCrossTenantIsolation404:
    """Tenant A must receive 404 on ALL Tenant B resource URLs."""

    # -- Orders
    def test_order_detail_cross_tenant_404(self, client_a, order_b):
        resp = client_a.get(reverse("orders:order_detail", args=[order_b.pk]))
        assert resp.status_code == 404

    def test_order_edit_cross_tenant_404(self, client_a, order_b):
        resp = client_a.get(reverse("orders:order_edit", args=[order_b.pk]))
        assert resp.status_code == 404

    def test_order_delete_cross_tenant_404(self, client_a, order_b):
        resp = client_a.post(reverse("orders:order_delete", args=[order_b.pk]))
        assert resp.status_code == 404
        assert Order.objects.filter(pk=order_b.pk).exists()

    # -- OrderLines
    def test_orderline_detail_cross_tenant_404(self, client_a, orderline_b):
        resp = client_a.get(reverse("orders:orderline_detail", args=[orderline_b.pk]))
        assert resp.status_code == 404

    def test_orderline_edit_cross_tenant_404(self, client_a, orderline_b):
        resp = client_a.get(reverse("orders:orderline_edit", args=[orderline_b.pk]))
        assert resp.status_code == 404

    def test_orderline_delete_cross_tenant_404(self, client_a, orderline_b):
        resp = client_a.post(reverse("orders:orderline_delete", args=[orderline_b.pk]))
        assert resp.status_code == 404
        assert OrderLine.objects.filter(pk=orderline_b.pk).exists()

    # -- Fulfillments
    def test_fulfillment_detail_cross_tenant_404(self, client_a, fulfillment_b):
        resp = client_a.get(reverse("orders:fulfillment_detail", args=[fulfillment_b.pk]))
        assert resp.status_code == 404

    def test_fulfillment_edit_cross_tenant_404(self, client_a, fulfillment_b):
        resp = client_a.get(reverse("orders:fulfillment_edit", args=[fulfillment_b.pk]))
        assert resp.status_code == 404

    def test_fulfillment_delete_cross_tenant_404(self, client_a, fulfillment_b):
        resp = client_a.post(reverse("orders:fulfillment_delete", args=[fulfillment_b.pk]))
        assert resp.status_code == 404
        assert Fulfillment.objects.filter(pk=fulfillment_b.pk).exists()

    # -- Amendments
    def test_amendment_detail_cross_tenant_404(self, client_a, amendment_b):
        resp = client_a.get(reverse("orders:orderamendment_detail", args=[amendment_b.pk]))
        assert resp.status_code == 404

    def test_amendment_edit_cross_tenant_404(self, client_a, amendment_b):
        resp = client_a.get(reverse("orders:orderamendment_edit", args=[amendment_b.pk]))
        assert resp.status_code == 404

    def test_amendment_delete_cross_tenant_404(self, client_a, amendment_b):
        resp = client_a.post(reverse("orders:orderamendment_delete", args=[amendment_b.pk]))
        assert resp.status_code == 404
        assert OrderAmendment.objects.filter(pk=amendment_b.pk).exists()

    # -- RevenueSchedules
    def test_revenueschedule_detail_cross_tenant_404(self, client_a, revenueschedule_b):
        resp = client_a.get(reverse("orders:revenueschedule_detail", args=[revenueschedule_b.pk]))
        assert resp.status_code == 404

    def test_revenueschedule_edit_cross_tenant_404(self, client_a, revenueschedule_b):
        resp = client_a.get(reverse("orders:revenueschedule_edit", args=[revenueschedule_b.pk]))
        assert resp.status_code == 404

    def test_revenueschedule_delete_cross_tenant_404(self, client_a, revenueschedule_b):
        resp = client_a.post(reverse("orders:revenueschedule_delete", args=[revenueschedule_b.pk]))
        assert resp.status_code == 404
        assert RevenueSchedule.objects.filter(pk=revenueschedule_b.pk).exists()


# ══════════════════════════════════════════════════════════════ List isolation
@pytest.mark.django_db
class TestListIsolation:
    """List views for Tenant A must never include Tenant B rows."""

    def test_order_list_excludes_tenant_b(self, client_a, order_a, order_b):
        resp = client_a.get(reverse("orders:order_list"))
        pks = [o.pk for o in resp.context["orders"]]
        assert order_a.pk in pks
        assert order_b.pk not in pks

    def test_orderline_list_excludes_tenant_b(self, client_a, orderline_a, orderline_b):
        resp = client_a.get(reverse("orders:orderline_list"))
        pks = [l.pk for l in resp.context["lines"]]
        assert orderline_a.pk in pks
        assert orderline_b.pk not in pks

    def test_fulfillment_list_excludes_tenant_b(self, client_a, fulfillment_a, fulfillment_b):
        resp = client_a.get(reverse("orders:fulfillment_list"))
        pks = [f.pk for f in resp.context["fulfillments"]]
        assert fulfillment_a.pk in pks
        assert fulfillment_b.pk not in pks

    def test_amendment_list_excludes_tenant_b(self, client_a, amendment_a, amendment_b):
        resp = client_a.get(reverse("orders:orderamendment_list"))
        pks = [a.pk for a in resp.context["amendments"]]
        assert amendment_a.pk in pks
        assert amendment_b.pk not in pks

    def test_revenueschedule_list_excludes_tenant_b(
        self, client_a, revenueschedule_a, revenueschedule_b
    ):
        resp = client_a.get(reverse("orders:revenueschedule_list"))
        pks = [s.pk for s in resp.context["schedules"]]
        assert revenueschedule_a.pk in pks
        assert revenueschedule_b.pk not in pks

    def test_orderline_list_orders_context_excludes_tenant_b(
        self, client_a, order_a, order_b
    ):
        """The orders dropdown in the orderline list must not contain tenant B orders."""
        resp = client_a.get(reverse("orders:orderline_list"))
        order_pks = [o.pk for o in resp.context["orders"]]
        assert order_a.pk in order_pks
        assert order_b.pk not in order_pks

    def test_amendment_list_orders_context_excludes_tenant_b(
        self, client_a, order_a, order_b
    ):
        """The orders dropdown in the amendment list must not contain tenant B orders."""
        resp = client_a.get(reverse("orders:orderamendment_list"))
        order_pks = [o.pk for o in resp.context["orders"]]
        assert order_a.pk in order_pks
        assert order_b.pk not in order_pks
