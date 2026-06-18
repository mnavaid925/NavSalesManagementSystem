"""Shared fixtures for orders app tests."""
import pytest
from decimal import Decimal
from django.test import Client
from django.utils import timezone

from apps.core.models import Tenant
from apps.accounts.models import Role, User
from apps.orders.models import (
    Fulfillment, Order, OrderAmendment, OrderLine, RevenueSchedule,
)


# ──────────────────────────────────────────────────────────── tenants
@pytest.fixture
def tenant_a():
    return Tenant.objects.create(name="Tenant A", slug="tenant-a")


@pytest.fixture
def tenant_b():
    return Tenant.objects.create(name="Tenant B", slug="tenant-b")


# ──────────────────────────────────────────────────────────── roles
@pytest.fixture
def role_a(tenant_a):
    return Role.objects.create(tenant=tenant_a, name="Administrator", level=Role.LEVEL_ADMIN)


@pytest.fixture
def role_b(tenant_b):
    return Role.objects.create(tenant=tenant_b, name="Administrator", level=Role.LEVEL_ADMIN)


# ──────────────────────────────────────────────────────────── users
@pytest.fixture
def admin_a(tenant_a, role_a):
    return User.objects.create_user(
        username="admin_a",
        password="testpass123",
        tenant=tenant_a,
        role=role_a,
        is_tenant_admin=True,
        email="admin_a@testa.com",
    )


@pytest.fixture
def admin_b(tenant_b, role_b):
    return User.objects.create_user(
        username="admin_b",
        password="testpass123",
        tenant=tenant_b,
        role=role_b,
        is_tenant_admin=True,
        email="admin_b@testb.com",
    )


@pytest.fixture
def rep_a(tenant_a):
    rep_role = Role.objects.create(tenant=tenant_a, name="Sales Rep", level=Role.LEVEL_REP)
    return User.objects.create_user(
        username="rep_a",
        password="testpass123",
        tenant=tenant_a,
        role=rep_role,
        is_tenant_admin=False,
        email="rep_a@testa.com",
    )


# ──────────────────────────────────────────────────────────── clients
@pytest.fixture
def client_a(admin_a):
    c = Client()
    c.force_login(admin_a)
    return c


@pytest.fixture
def client_b(admin_b):
    c = Client()
    c.force_login(admin_b)
    return c


@pytest.fixture
def rep_client_a(rep_a):
    c = Client()
    c.force_login(rep_a)
    return c


# ──────────────────────────────────────────────────────────── orders
@pytest.fixture
def order_a(tenant_a):
    return Order.objects.create(
        tenant=tenant_a,
        customer_name="Acme Corp",
        customer_email="acme@example.com",
        channel=Order.CHANNEL_DIRECT,
        status=Order.STATUS_DRAFT,
        currency="USD",
        total_amount=Decimal("500.00"),
        order_date=timezone.localdate(),
    )


@pytest.fixture
def order_b(tenant_b):
    return Order.objects.create(
        tenant=tenant_b,
        customer_name="Beta Corp",
        customer_email="beta@example.com",
        channel=Order.CHANNEL_ONLINE,
        status=Order.STATUS_DRAFT,
        currency="EUR",
        total_amount=Decimal("200.00"),
        order_date=timezone.localdate(),
    )


# ──────────────────────────────────────────────────────────── order lines
@pytest.fixture
def orderline_a(tenant_a, order_a):
    return OrderLine.objects.create(
        tenant=tenant_a,
        order=order_a,
        product_name="Widget Pro",
        sku="WGT-001",
        quantity=2,
        unit_price=Decimal("100.00"),
        discount_percent=Decimal("0.00"),
    )


@pytest.fixture
def orderline_b(tenant_b, order_b):
    return OrderLine.objects.create(
        tenant=tenant_b,
        order=order_b,
        product_name="Gadget Basic",
        sku="GDG-001",
        quantity=1,
        unit_price=Decimal("200.00"),
        discount_percent=Decimal("0.00"),
    )


# ──────────────────────────────────────────────────────────── fulfillments
@pytest.fixture
def fulfillment_a(tenant_a, order_a):
    return Fulfillment.objects.create(
        tenant=tenant_a,
        order=order_a,
        warehouse="Warehouse A",
        carrier=Fulfillment.CARRIER_FEDEX,
        tracking_number="FX123456",
        status=Fulfillment.STATUS_PENDING,
    )


@pytest.fixture
def fulfillment_b(tenant_b, order_b):
    return Fulfillment.objects.create(
        tenant=tenant_b,
        order=order_b,
        warehouse="Warehouse B",
        carrier=Fulfillment.CARRIER_UPS,
        tracking_number="UP789012",
        status=Fulfillment.STATUS_PENDING,
    )


# ──────────────────────────────────────────────────────────── amendments
@pytest.fixture
def amendment_a(tenant_a, order_a):
    return OrderAmendment.objects.create(
        tenant=tenant_a,
        order=order_a,
        amendment_type=OrderAmendment.TYPE_QUANTITY,
        status=OrderAmendment.STATUS_REQUESTED,
        reason="Customer changed order qty",
        requested_by="admin_a",
        amount_delta=Decimal("50.00"),
        requested_on=timezone.localdate(),
    )


@pytest.fixture
def amendment_b(tenant_b, order_b):
    return OrderAmendment.objects.create(
        tenant=tenant_b,
        order=order_b,
        amendment_type=OrderAmendment.TYPE_PRICE,
        status=OrderAmendment.STATUS_REQUESTED,
        reason="Price negotiation",
        requested_by="admin_b",
        amount_delta=Decimal("20.00"),
        requested_on=timezone.localdate(),
    )


# ──────────────────────────────────────────────────────────── revenue schedules
@pytest.fixture
def revenueschedule_a(tenant_a, order_a):
    return RevenueSchedule.objects.create(
        tenant=tenant_a,
        order=order_a,
        method=RevenueSchedule.METHOD_RATABLE,
        status=RevenueSchedule.STATUS_SCHEDULED,
        period_label="Q1 2025",
        amount=Decimal("250.00"),
        recognition_date=timezone.localdate(),
    )


@pytest.fixture
def revenueschedule_b(tenant_b, order_b):
    return RevenueSchedule.objects.create(
        tenant=tenant_b,
        order=order_b,
        method=RevenueSchedule.METHOD_IMMEDIATE,
        status=RevenueSchedule.STATUS_SCHEDULED,
        period_label="Q1 2025",
        amount=Decimal("100.00"),
        recognition_date=timezone.localdate(),
    )
