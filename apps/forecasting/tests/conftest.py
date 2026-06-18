"""Shared fixtures for forecasting app tests."""
from decimal import Decimal

import pytest
from django.test import Client

from apps.core.models import Tenant
from apps.accounts.models import Role, User
from apps.forecasting.models import (
    Forecast, ForecastAccuracy, ForecastAdjustment, ForecastCategory, Quota,
)


# ------------------------------------------------------------------ tenants
@pytest.fixture
def tenant_a():
    return Tenant.objects.create(name="Tenant A", slug="tenant-a")


@pytest.fixture
def tenant_b():
    return Tenant.objects.create(name="Tenant B", slug="tenant-b")


# ------------------------------------------------------------------ roles
@pytest.fixture
def role_a(tenant_a):
    return Role.objects.create(tenant=tenant_a, name="Administrator", level=Role.LEVEL_ADMIN)


@pytest.fixture
def role_b(tenant_b):
    return Role.objects.create(tenant=tenant_b, name="Administrator", level=Role.LEVEL_ADMIN)


# ------------------------------------------------------------------ admin users
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


# ------------------------------------------------------------------ rep (non-admin) user
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


# ------------------------------------------------------------------ logged-in clients
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


# ------------------------------------------------------------------ ForecastCategory fixtures
@pytest.fixture
def category_a(tenant_a):
    return ForecastCategory.objects.create(
        tenant=tenant_a,
        name="Pipeline A",
        commitment=ForecastCategory.COMMIT_PIPELINE,
        probability=40,
    )


@pytest.fixture
def category_b(tenant_b):
    return ForecastCategory.objects.create(
        tenant=tenant_b,
        name="Pipeline B",
        commitment=ForecastCategory.COMMIT_PIPELINE,
        probability=40,
    )


# ------------------------------------------------------------------ Forecast fixtures
@pytest.fixture
def forecast_a(tenant_a, category_a):
    return Forecast.objects.create(
        tenant=tenant_a,
        name="Q3 Forecast",
        category=category_a,
        period_type=Forecast.PERIOD_QUARTER,
        period_label="Q3 2026",
        pipeline_amount="100000.00",
        commit_amount="60000.00",
        status=Forecast.STATUS_DRAFT,
    )


@pytest.fixture
def forecast_b(tenant_b, category_b):
    return Forecast.objects.create(
        tenant=tenant_b,
        name="Q3 B Forecast",
        category=category_b,
        period_type=Forecast.PERIOD_QUARTER,
        period_label="Q3 2026",
        status=Forecast.STATUS_DRAFT,
    )


# ------------------------------------------------------------------ Quota fixtures
@pytest.fixture
def quota_a(tenant_a):
    q = Quota.objects.create(
        tenant=tenant_a,
        owner_name="Alice",
        period_type=Quota.PERIOD_QUARTER,
        period_label="Q3 2026",
        target_amount=Decimal("150000.00"),
        attained_amount=Decimal("75000.00"),
        status=Quota.STATUS_ACTIVE,
    )
    q.refresh_from_db()
    return q


@pytest.fixture
def quota_b(tenant_b):
    q = Quota.objects.create(
        tenant=tenant_b,
        owner_name="Bob B",
        period_type=Quota.PERIOD_QUARTER,
        period_label="Q3 2026",
        target_amount=Decimal("100000.00"),
        status=Quota.STATUS_ACTIVE,
    )
    q.refresh_from_db()
    return q


# ------------------------------------------------------------------ ForecastAdjustment fixtures
@pytest.fixture
def adjustment_a(tenant_a, forecast_a):
    return ForecastAdjustment.objects.create(
        tenant=tenant_a,
        forecast=forecast_a,
        adjustment_type=ForecastAdjustment.TYPE_UPLIFT,
        amount="5000.00",
        adjusted_by="Manager Alice",
        status=ForecastAdjustment.STATUS_PENDING,
    )


@pytest.fixture
def adjustment_b(tenant_b, forecast_b):
    return ForecastAdjustment.objects.create(
        tenant=tenant_b,
        forecast=forecast_b,
        adjustment_type=ForecastAdjustment.TYPE_HAIRCUT,
        amount="-2000.00",
        adjusted_by="Manager Bob",
        status=ForecastAdjustment.STATUS_PENDING,
    )


# ------------------------------------------------------------------ ForecastAccuracy fixtures
@pytest.fixture
def accuracy_a(tenant_a, forecast_a):
    acc = ForecastAccuracy.objects.create(
        tenant=tenant_a,
        forecast=forecast_a,
        period_label="Q2 2026",
        forecasted_amount=Decimal("100000.00"),
        actual_amount=Decimal("95000.00"),
        accuracy_pct=Decimal("95.00"),
        grade=ForecastAccuracy.GRADE_EXCELLENT,
    )
    acc.refresh_from_db()
    return acc


@pytest.fixture
def accuracy_b(tenant_b, forecast_b):
    acc = ForecastAccuracy.objects.create(
        tenant=tenant_b,
        forecast=forecast_b,
        period_label="Q2 2026",
        forecasted_amount=Decimal("80000.00"),
        actual_amount=Decimal("60000.00"),
        accuracy_pct=Decimal("75.00"),
        grade=ForecastAccuracy.GRADE_FAIR,
    )
    acc.refresh_from_db()
    return acc
