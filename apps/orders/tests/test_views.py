"""Tests for orders views: list, detail, create, edit, delete for all five models."""
import pytest
from django.urls import reverse
from django.utils import timezone

from apps.orders.models import (
    Fulfillment, Order, OrderAmendment, OrderLine, RevenueSchedule,
)


# ══════════════════════════════════════════════════════════════ Order views
@pytest.mark.django_db
class TestOrderListView:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("orders:order_list"))
        assert resp.status_code == 200

    def test_list_context_has_orders(self, client_a, order_a):
        resp = client_a.get(reverse("orders:order_list"))
        assert "orders" in resp.context

    def test_list_seeded_order_appears(self, client_a, order_a):
        resp = client_a.get(reverse("orders:order_list"))
        order_pks = [o.pk for o in resp.context["orders"]]
        assert order_a.pk in order_pks

    def test_list_has_status_choices(self, client_a):
        resp = client_a.get(reverse("orders:order_list"))
        assert "status_choices" in resp.context

    def test_list_has_channel_choices(self, client_a):
        resp = client_a.get(reverse("orders:order_list"))
        assert "channel_choices" in resp.context

    def test_list_has_total(self, client_a):
        resp = client_a.get(reverse("orders:order_list"))
        assert "total" in resp.context

    def test_list_search_by_customer_name(self, client_a, order_a):
        resp = client_a.get(reverse("orders:order_list"), {"q": "Acme"})
        assert resp.status_code == 200
        order_pks = [o.pk for o in resp.context["orders"]]
        assert order_a.pk in order_pks

    def test_list_filter_by_status(self, client_a, order_a):
        resp = client_a.get(reverse("orders:order_list"), {"status": "draft"})
        assert resp.status_code == 200
        order_pks = [o.pk for o in resp.context["orders"]]
        assert order_a.pk in order_pks

    def test_list_filter_by_channel(self, client_a, order_a):
        resp = client_a.get(reverse("orders:order_list"), {"channel": "direct"})
        assert resp.status_code == 200


@pytest.mark.django_db
class TestOrderDetailView:
    def test_detail_200(self, client_a, order_a):
        resp = client_a.get(reverse("orders:order_detail", args=[order_a.pk]))
        assert resp.status_code == 200

    def test_detail_context_has_obj(self, client_a, order_a):
        resp = client_a.get(reverse("orders:order_detail", args=[order_a.pk]))
        assert "obj" in resp.context
        assert resp.context["obj"].pk == order_a.pk

    def test_detail_context_has_lines(self, client_a, order_a):
        resp = client_a.get(reverse("orders:order_detail", args=[order_a.pk]))
        assert "lines" in resp.context

    def test_detail_context_has_fulfillments(self, client_a, order_a):
        resp = client_a.get(reverse("orders:order_detail", args=[order_a.pk]))
        assert "fulfillments" in resp.context

    def test_detail_context_has_amendments(self, client_a, order_a):
        resp = client_a.get(reverse("orders:order_detail", args=[order_a.pk]))
        assert "amendments" in resp.context

    def test_detail_context_has_schedules(self, client_a, order_a):
        resp = client_a.get(reverse("orders:order_detail", args=[order_a.pk]))
        assert "schedules" in resp.context


@pytest.mark.django_db
class TestOrderCreateView:
    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("orders:order_create"))
        assert resp.status_code == 200

    def test_create_post_creates_order(self, client_a, tenant_a):
        before = Order.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("orders:order_create"), {
            "customer_name": "New Customer",
            "customer_email": "new@example.com",
            "channel": "direct",
            "status": "draft",
            "currency": "USD",
            "total_amount": "100.00",
            "is_validated": False,
            "order_date": timezone.localdate().isoformat(),
            "requested_ship_date": "",
            "billing_address": "",
            "shipping_address": "",
            "notes": "",
        })
        assert Order.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a):
        client_a.post(reverse("orders:order_create"), {
            "customer_name": "Tenant Check",
            "customer_email": "",
            "channel": "direct",
            "status": "draft",
            "currency": "USD",
            "total_amount": "0",
            "is_validated": False,
            "order_date": timezone.localdate().isoformat(),
            "requested_ship_date": "",
            "billing_address": "",
            "shipping_address": "",
            "notes": "tenant test",
        })
        obj = Order.objects.filter(tenant=tenant_a, notes="tenant test").first()
        assert obj is not None
        assert obj.tenant == tenant_a

    def test_create_auto_numbers_order(self, client_a, tenant_a):
        Order.objects.filter(tenant=tenant_a).delete()
        client_a.post(reverse("orders:order_create"), {
            "customer_name": "Auto Numbered",
            "channel": "direct",
            "status": "draft",
            "currency": "USD",
            "total_amount": "0",
            "order_date": timezone.localdate().isoformat(),
        })
        obj = Order.objects.filter(tenant=tenant_a).latest("created_at")
        assert obj.number.startswith("ORD-")

    def test_create_post_redirects_on_success(self, client_a, tenant_a):
        resp = client_a.post(reverse("orders:order_create"), {
            "customer_name": "Redirect Test",
            "channel": "direct",
            "status": "draft",
            "currency": "USD",
            "total_amount": "0",
            "order_date": timezone.localdate().isoformat(),
        })
        assert resp.status_code == 302


@pytest.mark.django_db
class TestOrderEditView:
    def test_edit_get_200(self, client_a, order_a):
        resp = client_a.get(reverse("orders:order_edit", args=[order_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_order(self, client_a, order_a):
        client_a.post(reverse("orders:order_edit", args=[order_a.pk]), {
            "customer_name": "Updated Corp",
            "customer_email": "updated@example.com",
            "channel": "partner",
            "status": "validated",
            "currency": "EUR",
            "total_amount": "999.00",
            "is_validated": True,
            "order_date": timezone.localdate().isoformat(),
            "requested_ship_date": "",
            "billing_address": "",
            "shipping_address": "",
            "notes": "updated",
        })
        order_a.refresh_from_db()
        assert order_a.customer_name == "Updated Corp"
        assert order_a.channel == "partner"

    def test_edit_post_redirects_on_success(self, client_a, order_a):
        resp = client_a.post(reverse("orders:order_edit", args=[order_a.pk]), {
            "customer_name": "Updated",
            "channel": "direct",
            "status": "draft",
            "currency": "USD",
            "total_amount": "0",
            "order_date": timezone.localdate().isoformat(),
        })
        assert resp.status_code == 302


@pytest.mark.django_db
class TestOrderDeleteView:
    def test_delete_post_removes_order(self, client_a, tenant_a):
        obj = Order.objects.create(
            tenant=tenant_a, customer_name="Delete Me", order_date=timezone.localdate()
        )
        client_a.post(reverse("orders:order_delete", args=[obj.pk]))
        assert not Order.objects.filter(pk=obj.pk).exists()

    def test_delete_post_redirects_to_list(self, client_a, tenant_a):
        obj = Order.objects.create(
            tenant=tenant_a, customer_name="Redirect Delete", order_date=timezone.localdate()
        )
        resp = client_a.post(reverse("orders:order_delete", args=[obj.pk]))
        assert resp.status_code == 302


# ══════════════════════════════════════════════════════════════ OrderLine views
@pytest.mark.django_db
class TestOrderLineListView:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("orders:orderline_list"))
        assert resp.status_code == 200

    def test_list_context_has_lines(self, client_a, orderline_a):
        resp = client_a.get(reverse("orders:orderline_list"))
        assert "lines" in resp.context

    def test_list_seeded_line_appears(self, client_a, orderline_a):
        resp = client_a.get(reverse("orders:orderline_list"))
        line_pks = [l.pk for l in resp.context["lines"]]
        assert orderline_a.pk in line_pks

    def test_list_has_orders_context(self, client_a):
        resp = client_a.get(reverse("orders:orderline_list"))
        assert "orders" in resp.context


@pytest.mark.django_db
class TestOrderLineDetailView:
    def test_detail_200(self, client_a, orderline_a):
        resp = client_a.get(reverse("orders:orderline_detail", args=[orderline_a.pk]))
        assert resp.status_code == 200

    def test_detail_context_has_obj(self, client_a, orderline_a):
        resp = client_a.get(reverse("orders:orderline_detail", args=[orderline_a.pk]))
        assert "obj" in resp.context
        assert resp.context["obj"].pk == orderline_a.pk


@pytest.mark.django_db
class TestOrderLineCreateView:
    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("orders:orderline_create"))
        assert resp.status_code == 200

    def test_create_post_creates_line(self, client_a, tenant_a, order_a):
        before = OrderLine.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("orders:orderline_create"), {
            "order": order_a.pk,
            "product_name": "New Widget",
            "sku": "NW-001",
            "quantity": 3,
            "unit_price": "25.00",
            "discount_percent": "0.00",
        })
        assert OrderLine.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a, order_a):
        client_a.post(reverse("orders:orderline_create"), {
            "order": order_a.pk,
            "product_name": "Tenant Check Line",
            "sku": "",
            "quantity": 1,
            "unit_price": "10.00",
            "discount_percent": "0.00",
        })
        obj = OrderLine.objects.filter(tenant=tenant_a, product_name="Tenant Check Line").first()
        assert obj is not None
        assert obj.tenant == tenant_a


@pytest.mark.django_db
class TestOrderLineEditView:
    def test_edit_get_200(self, client_a, orderline_a):
        resp = client_a.get(reverse("orders:orderline_edit", args=[orderline_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_line(self, client_a, orderline_a, order_a):
        client_a.post(reverse("orders:orderline_edit", args=[orderline_a.pk]), {
            "order": order_a.pk,
            "product_name": "Updated Widget",
            "sku": "UPD-001",
            "quantity": 5,
            "unit_price": "50.00",
            "discount_percent": "0.00",
        })
        orderline_a.refresh_from_db()
        assert orderline_a.product_name == "Updated Widget"
        assert orderline_a.quantity == 5


@pytest.mark.django_db
class TestOrderLineDeleteView:
    def test_delete_post_removes_line(self, client_a, tenant_a, order_a):
        obj = OrderLine.objects.create(
            tenant=tenant_a, order=order_a, product_name="Delete Me Line"
        )
        client_a.post(reverse("orders:orderline_delete", args=[obj.pk]))
        assert not OrderLine.objects.filter(pk=obj.pk).exists()

    def test_delete_post_redirects_to_list(self, client_a, tenant_a, order_a):
        obj = OrderLine.objects.create(
            tenant=tenant_a, order=order_a, product_name="Redirect Line"
        )
        resp = client_a.post(reverse("orders:orderline_delete", args=[obj.pk]))
        assert resp.status_code == 302


# ══════════════════════════════════════════════════════════════ Fulfillment views
@pytest.mark.django_db
class TestFulfillmentListView:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("orders:fulfillment_list"))
        assert resp.status_code == 200

    def test_list_context_has_fulfillments(self, client_a, fulfillment_a):
        resp = client_a.get(reverse("orders:fulfillment_list"))
        assert "fulfillments" in resp.context

    def test_list_seeded_fulfillment_appears(self, client_a, fulfillment_a):
        resp = client_a.get(reverse("orders:fulfillment_list"))
        pks = [f.pk for f in resp.context["fulfillments"]]
        assert fulfillment_a.pk in pks

    def test_list_has_status_choices(self, client_a):
        resp = client_a.get(reverse("orders:fulfillment_list"))
        assert "status_choices" in resp.context

    def test_list_has_carrier_choices(self, client_a):
        resp = client_a.get(reverse("orders:fulfillment_list"))
        assert "carrier_choices" in resp.context


@pytest.mark.django_db
class TestFulfillmentDetailView:
    def test_detail_200(self, client_a, fulfillment_a):
        resp = client_a.get(reverse("orders:fulfillment_detail", args=[fulfillment_a.pk]))
        assert resp.status_code == 200

    def test_detail_context_has_obj(self, client_a, fulfillment_a):
        resp = client_a.get(reverse("orders:fulfillment_detail", args=[fulfillment_a.pk]))
        assert "obj" in resp.context
        assert resp.context["obj"].pk == fulfillment_a.pk


@pytest.mark.django_db
class TestFulfillmentCreateView:
    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("orders:fulfillment_create"))
        assert resp.status_code == 200

    def test_create_post_creates_fulfillment(self, client_a, tenant_a, order_a):
        before = Fulfillment.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("orders:fulfillment_create"), {
            "order": order_a.pk,
            "warehouse": "Main",
            "carrier": "ups",
            "tracking_number": "UP001",
            "status": "pending",
            "shipped_on": "",
            "expected_delivery": "",
            "notes": "",
        })
        assert Fulfillment.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a, order_a):
        client_a.post(reverse("orders:fulfillment_create"), {
            "order": order_a.pk,
            "warehouse": "Tenant WH",
            "carrier": "dhl",
            "tracking_number": "",
            "status": "pending",
            "shipped_on": "",
            "expected_delivery": "",
            "notes": "tenant check fulfillment",
        })
        obj = Fulfillment.objects.filter(tenant=tenant_a, notes="tenant check fulfillment").first()
        assert obj is not None
        assert obj.tenant == tenant_a


@pytest.mark.django_db
class TestFulfillmentEditView:
    def test_edit_get_200(self, client_a, fulfillment_a):
        resp = client_a.get(reverse("orders:fulfillment_edit", args=[fulfillment_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_fulfillment(self, client_a, fulfillment_a, order_a):
        client_a.post(reverse("orders:fulfillment_edit", args=[fulfillment_a.pk]), {
            "order": order_a.pk,
            "warehouse": "Updated WH",
            "carrier": "dhl",
            "tracking_number": "DHL999",
            "status": "shipped",
            "shipped_on": "",
            "expected_delivery": "",
            "notes": "",
        })
        fulfillment_a.refresh_from_db()
        assert fulfillment_a.warehouse == "Updated WH"
        assert fulfillment_a.carrier == "dhl"


@pytest.mark.django_db
class TestFulfillmentDeleteView:
    def test_delete_post_removes_fulfillment(self, client_a, tenant_a, order_a):
        obj = Fulfillment.objects.create(
            tenant=tenant_a, order=order_a, carrier=Fulfillment.CARRIER_USPS
        )
        client_a.post(reverse("orders:fulfillment_delete", args=[obj.pk]))
        assert not Fulfillment.objects.filter(pk=obj.pk).exists()

    def test_delete_post_redirects_to_list(self, client_a, tenant_a, order_a):
        obj = Fulfillment.objects.create(
            tenant=tenant_a, order=order_a, carrier=Fulfillment.CARRIER_DIGITAL
        )
        resp = client_a.post(reverse("orders:fulfillment_delete", args=[obj.pk]))
        assert resp.status_code == 302


# ══════════════════════════════════════════════════════════════ OrderAmendment views
@pytest.mark.django_db
class TestOrderAmendmentListView:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("orders:orderamendment_list"))
        assert resp.status_code == 200

    def test_list_context_has_amendments(self, client_a, amendment_a):
        resp = client_a.get(reverse("orders:orderamendment_list"))
        assert "amendments" in resp.context

    def test_list_seeded_amendment_appears(self, client_a, amendment_a):
        resp = client_a.get(reverse("orders:orderamendment_list"))
        pks = [a.pk for a in resp.context["amendments"]]
        assert amendment_a.pk in pks

    def test_list_has_status_choices(self, client_a):
        resp = client_a.get(reverse("orders:orderamendment_list"))
        assert "status_choices" in resp.context

    def test_list_has_type_choices(self, client_a):
        resp = client_a.get(reverse("orders:orderamendment_list"))
        assert "type_choices" in resp.context

    def test_list_has_orders_context(self, client_a):
        resp = client_a.get(reverse("orders:orderamendment_list"))
        assert "orders" in resp.context


@pytest.mark.django_db
class TestOrderAmendmentDetailView:
    def test_detail_200(self, client_a, amendment_a):
        resp = client_a.get(reverse("orders:orderamendment_detail", args=[amendment_a.pk]))
        assert resp.status_code == 200

    def test_detail_context_has_obj(self, client_a, amendment_a):
        resp = client_a.get(reverse("orders:orderamendment_detail", args=[amendment_a.pk]))
        assert "obj" in resp.context
        assert resp.context["obj"].pk == amendment_a.pk


@pytest.mark.django_db
class TestOrderAmendmentCreateView:
    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("orders:orderamendment_create"))
        assert resp.status_code == 200

    def test_create_post_creates_amendment(self, client_a, tenant_a, order_a):
        before = OrderAmendment.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("orders:orderamendment_create"), {
            "order": order_a.pk,
            "amendment_type": "price",
            "status": "requested",
            "reason": "Test reason",
            "requested_by": "tester",
            "amount_delta": "0.00",
            "requested_on": timezone.localdate().isoformat(),
        })
        assert OrderAmendment.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a, order_a):
        client_a.post(reverse("orders:orderamendment_create"), {
            "order": order_a.pk,
            "amendment_type": "address",
            "status": "requested",
            "reason": "tenant check reason",
            "requested_by": "admin",
            "amount_delta": "0.00",
            "requested_on": timezone.localdate().isoformat(),
        })
        obj = OrderAmendment.objects.filter(tenant=tenant_a, reason="tenant check reason").first()
        assert obj is not None
        assert obj.tenant == tenant_a


@pytest.mark.django_db
class TestOrderAmendmentEditView:
    def test_edit_get_200(self, client_a, amendment_a):
        resp = client_a.get(reverse("orders:orderamendment_edit", args=[amendment_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_amendment(self, client_a, amendment_a, order_a):
        client_a.post(reverse("orders:orderamendment_edit", args=[amendment_a.pk]), {
            "order": order_a.pk,
            "amendment_type": "date",
            "status": "approved",
            "reason": "Updated reason",
            "requested_by": "manager",
            "amount_delta": "100.00",
            "requested_on": timezone.localdate().isoformat(),
        })
        amendment_a.refresh_from_db()
        assert amendment_a.amendment_type == "date"
        assert amendment_a.reason == "Updated reason"


@pytest.mark.django_db
class TestOrderAmendmentDeleteView:
    def test_delete_post_removes_amendment(self, client_a, tenant_a, order_a):
        obj = OrderAmendment.objects.create(
            tenant=tenant_a, order=order_a, requested_on=timezone.localdate()
        )
        client_a.post(reverse("orders:orderamendment_delete", args=[obj.pk]))
        assert not OrderAmendment.objects.filter(pk=obj.pk).exists()

    def test_delete_post_redirects_to_list(self, client_a, tenant_a, order_a):
        obj = OrderAmendment.objects.create(
            tenant=tenant_a, order=order_a, requested_on=timezone.localdate()
        )
        resp = client_a.post(reverse("orders:orderamendment_delete", args=[obj.pk]))
        assert resp.status_code == 302


# ══════════════════════════════════════════════════════════════ RevenueSchedule views
@pytest.mark.django_db
class TestRevenueScheduleListView:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("orders:revenueschedule_list"))
        assert resp.status_code == 200

    def test_list_context_has_schedules(self, client_a, revenueschedule_a):
        resp = client_a.get(reverse("orders:revenueschedule_list"))
        assert "schedules" in resp.context

    def test_list_seeded_schedule_appears(self, client_a, revenueschedule_a):
        resp = client_a.get(reverse("orders:revenueschedule_list"))
        pks = [s.pk for s in resp.context["schedules"]]
        assert revenueschedule_a.pk in pks

    def test_list_has_status_choices(self, client_a):
        resp = client_a.get(reverse("orders:revenueschedule_list"))
        assert "status_choices" in resp.context

    def test_list_has_method_choices(self, client_a):
        resp = client_a.get(reverse("orders:revenueschedule_list"))
        assert "method_choices" in resp.context


@pytest.mark.django_db
class TestRevenueScheduleDetailView:
    def test_detail_200(self, client_a, revenueschedule_a):
        resp = client_a.get(reverse("orders:revenueschedule_detail", args=[revenueschedule_a.pk]))
        assert resp.status_code == 200

    def test_detail_context_has_obj(self, client_a, revenueschedule_a):
        resp = client_a.get(reverse("orders:revenueschedule_detail", args=[revenueschedule_a.pk]))
        assert "obj" in resp.context
        assert resp.context["obj"].pk == revenueschedule_a.pk


@pytest.mark.django_db
class TestRevenueScheduleCreateView:
    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("orders:revenueschedule_create"))
        assert resp.status_code == 200

    def test_create_post_creates_schedule(self, client_a, tenant_a, order_a):
        before = RevenueSchedule.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("orders:revenueschedule_create"), {
            "order": order_a.pk,
            "method": "immediate",
            "status": "scheduled",
            "period_label": "Q2 2025",
            "amount": "500.00",
            "recognition_date": timezone.localdate().isoformat(),
            "notes": "",
        })
        assert RevenueSchedule.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a, order_a):
        client_a.post(reverse("orders:revenueschedule_create"), {
            "order": order_a.pk,
            "method": "milestone",
            "status": "scheduled",
            "period_label": "tenant check period",
            "amount": "0.00",
            "recognition_date": timezone.localdate().isoformat(),
            "notes": "",
        })
        obj = RevenueSchedule.objects.filter(tenant=tenant_a, period_label="tenant check period").first()
        assert obj is not None
        assert obj.tenant == tenant_a


@pytest.mark.django_db
class TestRevenueScheduleEditView:
    def test_edit_get_200(self, client_a, revenueschedule_a):
        resp = client_a.get(reverse("orders:revenueschedule_edit", args=[revenueschedule_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_schedule(self, client_a, revenueschedule_a, order_a):
        client_a.post(reverse("orders:revenueschedule_edit", args=[revenueschedule_a.pk]), {
            "order": order_a.pk,
            "method": "usage",
            "status": "deferred",
            "period_label": "Q3 2025",
            "amount": "750.00",
            "recognition_date": timezone.localdate().isoformat(),
            "notes": "updated",
        })
        revenueschedule_a.refresh_from_db()
        assert revenueschedule_a.method == "usage"
        assert revenueschedule_a.period_label == "Q3 2025"


@pytest.mark.django_db
class TestRevenueScheduleDeleteView:
    def test_delete_post_removes_schedule(self, client_a, tenant_a, order_a):
        obj = RevenueSchedule.objects.create(
            tenant=tenant_a, order=order_a, recognition_date=timezone.localdate()
        )
        client_a.post(reverse("orders:revenueschedule_delete", args=[obj.pk]))
        assert not RevenueSchedule.objects.filter(pk=obj.pk).exists()

    def test_delete_post_redirects_to_list(self, client_a, tenant_a, order_a):
        obj = RevenueSchedule.objects.create(
            tenant=tenant_a, order=order_a, recognition_date=timezone.localdate()
        )
        resp = client_a.post(reverse("orders:revenueschedule_delete", args=[obj.pk]))
        assert resp.status_code == 302
