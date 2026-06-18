"""Tests for orders.forms: required fields, exclusions, and tenant-scoped FK querysets."""
import pytest
from django.utils import timezone
from decimal import Decimal

from apps.orders.forms import (
    FulfillmentForm, OrderAmendmentForm, OrderForm, OrderLineForm, RevenueScheduleForm,
)
from apps.orders.models import Order


# ══════════════════════════════════════════════════════════════ OrderForm
@pytest.mark.django_db
class TestOrderForm:
    def test_valid_form(self):
        form = OrderForm(data={
            "customer_name": "Acme Corp",
            "customer_email": "acme@example.com",
            "channel": "direct",
            "status": "draft",
            "currency": "USD",
            "total_amount": "500.00",
            "is_validated": False,
            "order_date": timezone.localdate().isoformat(),
            "requested_ship_date": "",
            "billing_address": "",
            "shipping_address": "",
            "notes": "",
        })
        assert form.is_valid(), form.errors

    def test_missing_customer_name_invalid(self):
        form = OrderForm(data={
            "channel": "direct",
            "status": "draft",
            "currency": "USD",
            "total_amount": "0",
            "order_date": timezone.localdate().isoformat(),
        })
        assert not form.is_valid()
        assert "customer_name" in form.errors

    def test_invalid_status_choice_invalid(self):
        form = OrderForm(data={
            "customer_name": "Test",
            "channel": "direct",
            "status": "not_a_status",
            "currency": "USD",
            "total_amount": "0",
            "order_date": timezone.localdate().isoformat(),
        })
        assert not form.is_valid()

    def test_invalid_channel_choice_invalid(self):
        form = OrderForm(data={
            "customer_name": "Test",
            "channel": "invalid_channel",
            "status": "draft",
            "currency": "USD",
            "total_amount": "0",
            "order_date": timezone.localdate().isoformat(),
        })
        assert not form.is_valid()

    def test_number_not_in_form_fields(self):
        """number is auto-generated, must not be a form field."""
        form = OrderForm()
        assert "number" not in form.fields

    def test_tenant_not_in_form_fields(self):
        form = OrderForm()
        assert "tenant" not in form.fields

    def test_confirmed_at_not_in_form_fields(self):
        """confirmed_at is system-set, must not be a form field."""
        form = OrderForm()
        assert "confirmed_at" not in form.fields

    def test_created_at_not_in_form_fields(self):
        form = OrderForm()
        assert "created_at" not in form.fields

    def test_updated_at_not_in_form_fields(self):
        form = OrderForm()
        assert "updated_at" not in form.fields


# ══════════════════════════════════════════════════════════════ OrderLineForm
@pytest.mark.django_db
class TestOrderLineForm:
    def test_valid_form(self, tenant_a, order_a):
        form = OrderLineForm(
            data={
                "order": order_a.pk,
                "product_name": "Widget",
                "sku": "WGT-001",
                "quantity": 2,
                "unit_price": "50.00",
                "discount_percent": "0.00",
            },
            tenant=tenant_a,
        )
        assert form.is_valid(), form.errors

    def test_missing_product_name_invalid(self, tenant_a, order_a):
        form = OrderLineForm(
            data={
                "order": order_a.pk,
                "quantity": 1,
                "unit_price": "10.00",
                "discount_percent": "0.00",
            },
            tenant=tenant_a,
        )
        assert not form.is_valid()
        assert "product_name" in form.errors

    def test_line_total_not_in_form_fields(self, tenant_a):
        """line_total is system-computed, must not be a form field."""
        form = OrderLineForm(tenant=tenant_a)
        assert "line_total" not in form.fields

    def test_tenant_not_in_form_fields(self, tenant_a):
        form = OrderLineForm(tenant=tenant_a)
        assert "tenant" not in form.fields

    def test_order_queryset_scoped_to_tenant(self, tenant_a, tenant_b, order_a, order_b):
        """order FK queryset must only include tenant_a orders, not tenant_b orders."""
        form = OrderLineForm(tenant=tenant_a)
        order_pks = list(form.fields["order"].queryset.values_list("pk", flat=True))
        assert order_a.pk in order_pks
        assert order_b.pk not in order_pks

    def test_order_queryset_empty_when_no_tenant(self):
        """When tenant=None the queryset must be .none(), not .all()."""
        form = OrderLineForm(tenant=None)
        assert form.fields["order"].queryset.count() == 0

    def test_order_from_other_tenant_rejected(self, tenant_a, order_b):
        """Submitting an order belonging to a different tenant must fail validation."""
        form = OrderLineForm(
            data={
                "order": order_b.pk,
                "product_name": "Test",
                "quantity": 1,
                "unit_price": "10.00",
                "discount_percent": "0.00",
            },
            tenant=tenant_a,
        )
        assert not form.is_valid()


# ══════════════════════════════════════════════════════════════ FulfillmentForm
@pytest.mark.django_db
class TestFulfillmentForm:
    def test_valid_form(self, tenant_a, order_a):
        form = FulfillmentForm(
            data={
                "order": order_a.pk,
                "warehouse": "Main WH",
                "carrier": "fedex",
                "tracking_number": "FX123",
                "status": "pending",
                "shipped_on": "",
                "expected_delivery": "",
                "notes": "",
            },
            tenant=tenant_a,
        )
        assert form.is_valid(), form.errors

    def test_missing_order_invalid(self, tenant_a):
        form = FulfillmentForm(
            data={
                "warehouse": "WH",
                "carrier": "ups",
                "status": "pending",
            },
            tenant=tenant_a,
        )
        assert not form.is_valid()
        assert "order" in form.errors

    def test_delivered_at_not_in_form_fields(self, tenant_a):
        """delivered_at is system-set, must not be a form field."""
        form = FulfillmentForm(tenant=tenant_a)
        assert "delivered_at" not in form.fields

    def test_tenant_not_in_form_fields(self, tenant_a):
        form = FulfillmentForm(tenant=tenant_a)
        assert "tenant" not in form.fields

    def test_order_queryset_scoped_to_tenant(self, tenant_a, tenant_b, order_a, order_b):
        form = FulfillmentForm(tenant=tenant_a)
        order_pks = list(form.fields["order"].queryset.values_list("pk", flat=True))
        assert order_a.pk in order_pks
        assert order_b.pk not in order_pks

    def test_order_queryset_empty_when_no_tenant(self):
        form = FulfillmentForm(tenant=None)
        assert form.fields["order"].queryset.count() == 0


# ══════════════════════════════════════════════════════════════ OrderAmendmentForm
@pytest.mark.django_db
class TestOrderAmendmentForm:
    def test_valid_form(self, tenant_a, order_a):
        form = OrderAmendmentForm(
            data={
                "order": order_a.pk,
                "amendment_type": "quantity",
                "status": "requested",
                "reason": "Changed my mind",
                "requested_by": "Alice",
                "amount_delta": "0.00",
                "requested_on": timezone.localdate().isoformat(),
            },
            tenant=tenant_a,
        )
        assert form.is_valid(), form.errors

    def test_missing_order_invalid(self, tenant_a):
        form = OrderAmendmentForm(
            data={
                "amendment_type": "price",
                "status": "requested",
                "amount_delta": "0",
                "requested_on": timezone.localdate().isoformat(),
            },
            tenant=tenant_a,
        )
        assert not form.is_valid()
        assert "order" in form.errors

    def test_resolved_at_not_in_form_fields(self, tenant_a):
        """resolved_at is system-set, must not be a form field."""
        form = OrderAmendmentForm(tenant=tenant_a)
        assert "resolved_at" not in form.fields

    def test_tenant_not_in_form_fields(self, tenant_a):
        form = OrderAmendmentForm(tenant=tenant_a)
        assert "tenant" not in form.fields

    def test_order_queryset_scoped_to_tenant(self, tenant_a, tenant_b, order_a, order_b):
        form = OrderAmendmentForm(tenant=tenant_a)
        order_pks = list(form.fields["order"].queryset.values_list("pk", flat=True))
        assert order_a.pk in order_pks
        assert order_b.pk not in order_pks

    def test_order_queryset_empty_when_no_tenant(self):
        form = OrderAmendmentForm(tenant=None)
        assert form.fields["order"].queryset.count() == 0

    def test_order_from_other_tenant_rejected(self, tenant_a, order_b):
        form = OrderAmendmentForm(
            data={
                "order": order_b.pk,
                "amendment_type": "quantity",
                "status": "requested",
                "amount_delta": "0",
                "requested_on": timezone.localdate().isoformat(),
            },
            tenant=tenant_a,
        )
        assert not form.is_valid()


# ══════════════════════════════════════════════════════════════ RevenueScheduleForm
@pytest.mark.django_db
class TestRevenueScheduleForm:
    def test_valid_form(self, tenant_a, order_a):
        form = RevenueScheduleForm(
            data={
                "order": order_a.pk,
                "method": "ratable",
                "status": "scheduled",
                "period_label": "Q1 2025",
                "amount": "250.00",
                "recognition_date": timezone.localdate().isoformat(),
                "notes": "",
            },
            tenant=tenant_a,
        )
        assert form.is_valid(), form.errors

    def test_missing_order_invalid(self, tenant_a):
        form = RevenueScheduleForm(
            data={
                "method": "immediate",
                "status": "scheduled",
                "amount": "100",
                "recognition_date": timezone.localdate().isoformat(),
            },
            tenant=tenant_a,
        )
        assert not form.is_valid()
        assert "order" in form.errors

    def test_recognized_at_not_in_form_fields(self, tenant_a):
        """recognized_at is system-set, must not be a form field."""
        form = RevenueScheduleForm(tenant=tenant_a)
        assert "recognized_at" not in form.fields

    def test_tenant_not_in_form_fields(self, tenant_a):
        form = RevenueScheduleForm(tenant=tenant_a)
        assert "tenant" not in form.fields

    def test_order_queryset_scoped_to_tenant(self, tenant_a, tenant_b, order_a, order_b):
        form = RevenueScheduleForm(tenant=tenant_a)
        order_pks = list(form.fields["order"].queryset.values_list("pk", flat=True))
        assert order_a.pk in order_pks
        assert order_b.pk not in order_pks

    def test_order_queryset_empty_when_no_tenant(self):
        form = RevenueScheduleForm(tenant=None)
        assert form.fields["order"].queryset.count() == 0

    def test_invalid_method_choice(self, tenant_a, order_a):
        form = RevenueScheduleForm(
            data={
                "order": order_a.pk,
                "method": "not_a_method",
                "status": "scheduled",
                "amount": "100",
                "recognition_date": timezone.localdate().isoformat(),
            },
            tenant=tenant_a,
        )
        assert not form.is_valid()
