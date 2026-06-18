"""Tests for orders.models: Order, OrderLine, Fulfillment, OrderAmendment, RevenueSchedule."""
import pytest
from decimal import Decimal
from django.utils import timezone

from apps.orders.models import (
    Fulfillment, Order, OrderAmendment, OrderLine, RevenueSchedule,
)


# ══════════════════════════════════════════════════════════════ Order
@pytest.mark.django_db
class TestOrder:
    def test_str_returns_number(self, order_a):
        assert str(order_a) == order_a.number

    def test_str_fallback_when_no_number(self, tenant_a):
        obj = Order(tenant=tenant_a, customer_name="Test")
        # unsaved — pk may be None
        result = str(obj)
        assert result is not None

    def test_auto_number_generated_on_save(self, order_a):
        assert order_a.number.startswith("ORD-")

    def test_auto_number_format_five_digits(self, order_a):
        parts = order_a.number.split("-")
        assert len(parts) == 2
        assert len(parts[1]) == 5
        assert parts[1].isdigit()

    def test_first_order_is_ORD_00001(self, tenant_a):
        o = Order.objects.create(
            tenant=tenant_a, customer_name="First", order_date=timezone.localdate()
        )
        assert o.number == "ORD-00001"

    def test_auto_number_increments_per_tenant(self, tenant_a):
        o1 = Order.objects.create(tenant=tenant_a, customer_name="A", order_date=timezone.localdate())
        o2 = Order.objects.create(tenant=tenant_a, customer_name="B", order_date=timezone.localdate())
        assert o1.number == "ORD-00001"
        assert o2.number == "ORD-00002"

    def test_auto_number_isolated_per_tenant(self, tenant_a, tenant_b):
        oa = Order.objects.create(tenant=tenant_a, customer_name="A", order_date=timezone.localdate())
        ob = Order.objects.create(tenant=tenant_b, customer_name="B", order_date=timezone.localdate())
        assert oa.number == "ORD-00001"
        assert ob.number == "ORD-00001"

    def test_unique_together_tenant_number(self, tenant_a):
        import django.db.utils as db_utils
        Order.objects.create(tenant=tenant_a, customer_name="X", order_date=timezone.localdate())
        with pytest.raises(db_utils.IntegrityError):
            Order.objects.create(
                tenant=tenant_a, number="ORD-00001",
                customer_name="Y", order_date=timezone.localdate()
            )

    def test_default_status_is_draft(self, tenant_a):
        o = Order.objects.create(
            tenant=tenant_a, customer_name="C", order_date=timezone.localdate()
        )
        assert o.status == Order.STATUS_DRAFT

    def test_default_channel_is_direct(self, tenant_a):
        o = Order.objects.create(
            tenant=tenant_a, customer_name="D", order_date=timezone.localdate()
        )
        assert o.channel == Order.CHANNEL_DIRECT

    def test_default_currency_is_usd(self, tenant_a):
        o = Order.objects.create(
            tenant=tenant_a, customer_name="E", order_date=timezone.localdate()
        )
        assert o.currency == "USD"

    def test_default_total_amount_is_zero(self, tenant_a):
        o = Order.objects.create(
            tenant=tenant_a, customer_name="F", order_date=timezone.localdate()
        )
        assert o.total_amount == Decimal("0")

    def test_default_is_validated_false(self, tenant_a):
        o = Order.objects.create(
            tenant=tenant_a, customer_name="G", order_date=timezone.localdate()
        )
        assert o.is_validated is False

    def test_confirmed_at_set_when_status_confirmed(self, tenant_a):
        o = Order.objects.create(
            tenant=tenant_a,
            customer_name="Confirm Me",
            status=Order.STATUS_CONFIRMED,
            order_date=timezone.localdate(),
        )
        assert o.confirmed_at is not None

    def test_confirmed_at_not_set_for_draft(self, tenant_a):
        o = Order.objects.create(
            tenant=tenant_a,
            customer_name="Draft",
            status=Order.STATUS_DRAFT,
            order_date=timezone.localdate(),
        )
        assert o.confirmed_at is None

    def test_confirmed_at_set_on_status_change_to_confirmed(self, order_a):
        assert order_a.confirmed_at is None
        order_a.status = Order.STATUS_CONFIRMED
        order_a.save()
        order_a.refresh_from_db()
        assert order_a.confirmed_at is not None

    def test_status_choices_contain_all_five(self):
        choices = dict(Order.STATUS_CHOICES)
        assert Order.STATUS_DRAFT in choices
        assert Order.STATUS_VALIDATED in choices
        assert Order.STATUS_CONFIRMED in choices
        assert Order.STATUS_FULFILLED in choices
        assert Order.STATUS_CANCELLED in choices

    def test_channel_choices_contain_all_four(self):
        choices = dict(Order.CHANNEL_CHOICES)
        assert Order.CHANNEL_DIRECT in choices
        assert Order.CHANNEL_PARTNER in choices
        assert Order.CHANNEL_ONLINE in choices
        assert Order.CHANNEL_RENEWAL in choices


# ══════════════════════════════════════════════════════════════ OrderLine
@pytest.mark.django_db
class TestOrderLine:
    def test_str_shows_product_and_quantity(self, orderline_a):
        result = str(orderline_a)
        assert "Widget Pro" in result
        assert "2" in result

    def test_line_total_computed_on_save(self, tenant_a, order_a):
        line = OrderLine.objects.create(
            tenant=tenant_a,
            order=order_a,
            product_name="Test Product",
            quantity=3,
            unit_price=Decimal("100.00"),
            discount_percent=Decimal("10.00"),
        )
        # gross = 300, discount = 30, total = 270
        assert line.line_total == Decimal("270.00")

    def test_line_total_no_discount(self, tenant_a, order_a):
        line = OrderLine.objects.create(
            tenant=tenant_a,
            order=order_a,
            product_name="No Discount",
            quantity=5,
            unit_price=Decimal("20.00"),
            discount_percent=Decimal("0.00"),
        )
        assert line.line_total == Decimal("100.00")

    def test_line_total_full_discount(self, tenant_a, order_a):
        line = OrderLine.objects.create(
            tenant=tenant_a,
            order=order_a,
            product_name="Free",
            quantity=1,
            unit_price=Decimal("50.00"),
            discount_percent=Decimal("100.00"),
        )
        assert line.line_total == Decimal("0.00")

    def test_line_total_is_recomputed_on_update(self, orderline_a):
        orderline_a.quantity = 4
        orderline_a.unit_price = Decimal("50.00")
        orderline_a.discount_percent = Decimal("0.00")
        orderline_a.save()
        orderline_a.refresh_from_db()
        assert orderline_a.line_total == Decimal("200.00")

    def test_default_quantity_is_one(self, tenant_a, order_a):
        line = OrderLine.objects.create(
            tenant=tenant_a, order=order_a, product_name="Default Qty",
        )
        assert line.quantity == 1

    def test_default_unit_price_is_zero(self, tenant_a, order_a):
        line = OrderLine.objects.create(
            tenant=tenant_a, order=order_a, product_name="Default Price",
        )
        assert line.unit_price == Decimal("0")

    def test_default_discount_percent_is_zero(self, tenant_a, order_a):
        line = OrderLine.objects.create(
            tenant=tenant_a, order=order_a, product_name="Default Discount",
        )
        assert line.discount_percent == Decimal("0")


# ══════════════════════════════════════════════════════════════ Fulfillment
@pytest.mark.django_db
class TestFulfillment:
    def test_str_includes_carrier_display(self, fulfillment_a):
        result = str(fulfillment_a)
        assert "FedEx" in result

    def test_str_includes_tracking_number(self, fulfillment_a):
        result = str(fulfillment_a)
        assert "FX123456" in result

    def test_str_uses_status_display_when_no_tracking(self, tenant_a, order_a):
        f = Fulfillment.objects.create(
            tenant=tenant_a,
            order=order_a,
            carrier=Fulfillment.CARRIER_UPS,
            tracking_number="",
            status=Fulfillment.STATUS_PENDING,
        )
        result = str(f)
        assert "UPS" in result
        assert "Pending" in result

    def test_default_status_is_pending(self, tenant_a, order_a):
        f = Fulfillment.objects.create(tenant=tenant_a, order=order_a)
        assert f.status == Fulfillment.STATUS_PENDING

    def test_default_carrier_is_fedex(self, tenant_a, order_a):
        f = Fulfillment.objects.create(tenant=tenant_a, order=order_a)
        assert f.carrier == Fulfillment.CARRIER_FEDEX

    def test_delivered_at_set_when_status_delivered(self, tenant_a, order_a):
        f = Fulfillment.objects.create(
            tenant=tenant_a, order=order_a, status=Fulfillment.STATUS_DELIVERED
        )
        assert f.delivered_at is not None

    def test_delivered_at_not_set_for_pending(self, tenant_a, order_a):
        f = Fulfillment.objects.create(
            tenant=tenant_a, order=order_a, status=Fulfillment.STATUS_PENDING
        )
        assert f.delivered_at is None

    def test_delivered_at_set_on_status_change_to_delivered(self, fulfillment_a):
        assert fulfillment_a.delivered_at is None
        fulfillment_a.status = Fulfillment.STATUS_DELIVERED
        fulfillment_a.save()
        fulfillment_a.refresh_from_db()
        assert fulfillment_a.delivered_at is not None

    def test_status_choices_contain_all_six(self):
        choices = dict(Fulfillment.STATUS_CHOICES)
        assert Fulfillment.STATUS_PENDING in choices
        assert Fulfillment.STATUS_PICKING in choices
        assert Fulfillment.STATUS_PACKED in choices
        assert Fulfillment.STATUS_SHIPPED in choices
        assert Fulfillment.STATUS_DELIVERED in choices
        assert Fulfillment.STATUS_RETURNED in choices

    def test_carrier_choices_contain_all_five(self):
        choices = dict(Fulfillment.CARRIER_CHOICES)
        assert Fulfillment.CARRIER_FEDEX in choices
        assert Fulfillment.CARRIER_UPS in choices
        assert Fulfillment.CARRIER_DHL in choices
        assert Fulfillment.CARRIER_USPS in choices
        assert Fulfillment.CARRIER_DIGITAL in choices


# ══════════════════════════════════════════════════════════════ OrderAmendment
@pytest.mark.django_db
class TestOrderAmendment:
    def test_str_shows_type_and_status(self, amendment_a):
        result = str(amendment_a)
        assert "Quantity Change" in result
        assert "Requested" in result

    def test_default_amendment_type_is_quantity(self, tenant_a, order_a):
        a = OrderAmendment.objects.create(tenant=tenant_a, order=order_a)
        assert a.amendment_type == OrderAmendment.TYPE_QUANTITY

    def test_default_status_is_requested(self, tenant_a, order_a):
        a = OrderAmendment.objects.create(tenant=tenant_a, order=order_a)
        assert a.status == OrderAmendment.STATUS_REQUESTED

    def test_resolved_at_set_when_approved(self, tenant_a, order_a):
        a = OrderAmendment.objects.create(
            tenant=tenant_a, order=order_a, status=OrderAmendment.STATUS_APPROVED
        )
        assert a.resolved_at is not None

    def test_resolved_at_set_when_rejected(self, tenant_a, order_a):
        a = OrderAmendment.objects.create(
            tenant=tenant_a, order=order_a, status=OrderAmendment.STATUS_REJECTED
        )
        assert a.resolved_at is not None

    def test_resolved_at_set_when_applied(self, tenant_a, order_a):
        a = OrderAmendment.objects.create(
            tenant=tenant_a, order=order_a, status=OrderAmendment.STATUS_APPLIED
        )
        assert a.resolved_at is not None

    def test_resolved_at_is_none_for_requested(self, tenant_a, order_a):
        a = OrderAmendment.objects.create(
            tenant=tenant_a, order=order_a, status=OrderAmendment.STATUS_REQUESTED
        )
        assert a.resolved_at is None

    def test_resolved_at_cleared_on_revert_to_requested(self, amendment_a):
        amendment_a.status = OrderAmendment.STATUS_APPROVED
        amendment_a.save()
        assert amendment_a.resolved_at is not None
        amendment_a.status = OrderAmendment.STATUS_REQUESTED
        amendment_a.save()
        amendment_a.refresh_from_db()
        assert amendment_a.resolved_at is None

    def test_type_choices_contain_all_five(self):
        choices = dict(OrderAmendment.TYPE_CHOICES)
        assert OrderAmendment.TYPE_QUANTITY in choices
        assert OrderAmendment.TYPE_PRICE in choices
        assert OrderAmendment.TYPE_ADDRESS in choices
        assert OrderAmendment.TYPE_DATE in choices
        assert OrderAmendment.TYPE_CANCELLATION in choices

    def test_status_choices_contain_all_four(self):
        choices = dict(OrderAmendment.STATUS_CHOICES)
        assert OrderAmendment.STATUS_REQUESTED in choices
        assert OrderAmendment.STATUS_APPROVED in choices
        assert OrderAmendment.STATUS_REJECTED in choices
        assert OrderAmendment.STATUS_APPLIED in choices


# ══════════════════════════════════════════════════════════════ RevenueSchedule
@pytest.mark.django_db
class TestRevenueSchedule:
    def test_str_shows_period_label_and_amount(self, revenueschedule_a):
        result = str(revenueschedule_a)
        assert "Q1 2025" in result
        assert "250" in result

    def test_str_uses_recognition_date_when_no_period_label(self, tenant_a, order_a):
        rs = RevenueSchedule.objects.create(
            tenant=tenant_a,
            order=order_a,
            period_label="",
            amount=Decimal("100.00"),
            recognition_date=timezone.localdate(),
        )
        result = str(rs)
        assert "100" in result

    def test_default_method_is_ratable(self, tenant_a, order_a):
        rs = RevenueSchedule.objects.create(tenant=tenant_a, order=order_a)
        assert rs.method == RevenueSchedule.METHOD_RATABLE

    def test_default_status_is_scheduled(self, tenant_a, order_a):
        rs = RevenueSchedule.objects.create(tenant=tenant_a, order=order_a)
        assert rs.status == RevenueSchedule.STATUS_SCHEDULED

    def test_recognized_at_set_when_recognized(self, tenant_a, order_a):
        rs = RevenueSchedule.objects.create(
            tenant=tenant_a, order=order_a, status=RevenueSchedule.STATUS_RECOGNIZED
        )
        assert rs.recognized_at is not None

    def test_recognized_at_none_for_scheduled(self, tenant_a, order_a):
        rs = RevenueSchedule.objects.create(
            tenant=tenant_a, order=order_a, status=RevenueSchedule.STATUS_SCHEDULED
        )
        assert rs.recognized_at is None

    def test_recognized_at_cleared_when_status_changes_from_recognized(self, tenant_a, order_a):
        rs = RevenueSchedule.objects.create(
            tenant=tenant_a, order=order_a, status=RevenueSchedule.STATUS_RECOGNIZED
        )
        assert rs.recognized_at is not None
        rs.status = RevenueSchedule.STATUS_DEFERRED
        rs.save()
        rs.refresh_from_db()
        assert rs.recognized_at is None

    def test_method_choices_contain_all_four(self):
        choices = dict(RevenueSchedule.METHOD_CHOICES)
        assert RevenueSchedule.METHOD_IMMEDIATE in choices
        assert RevenueSchedule.METHOD_RATABLE in choices
        assert RevenueSchedule.METHOD_MILESTONE in choices
        assert RevenueSchedule.METHOD_USAGE in choices

    def test_status_choices_contain_all_four(self):
        choices = dict(RevenueSchedule.STATUS_CHOICES)
        assert RevenueSchedule.STATUS_SCHEDULED in choices
        assert RevenueSchedule.STATUS_RECOGNIZED in choices
        assert RevenueSchedule.STATUS_DEFERRED in choices
        assert RevenueSchedule.STATUS_CANCELLED in choices
