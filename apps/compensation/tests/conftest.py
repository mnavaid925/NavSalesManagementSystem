"""Shared fixtures for compensation app tests."""
import pytest
from django.test import Client
from django.utils import timezone

from apps.core.models import Tenant
from apps.accounts.models import Role, User
from apps.compensation.models import (
    CommissionPlan, Earning, Clawback, GlobalPlanVariation, Payout,
)


# ------------------------------------------------------------------ tenants
@pytest.fixture
def tenant_a():
    return Tenant.objects.create(name="Comp Tenant A", slug="comp-tenant-a")


@pytest.fixture
def tenant_b():
    return Tenant.objects.create(name="Comp Tenant B", slug="comp-tenant-b")


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
        username="comp_admin_a",
        password="testpass123",
        tenant=tenant_a,
        role=role_a,
        is_tenant_admin=True,
        email="comp_admin_a@testa.com",
    )


@pytest.fixture
def admin_b(tenant_b, role_b):
    return User.objects.create_user(
        username="comp_admin_b",
        password="testpass123",
        tenant=tenant_b,
        role=role_b,
        is_tenant_admin=True,
        email="comp_admin_b@testb.com",
    )


# ------------------------------------------------------------------ rep (non-admin)
@pytest.fixture
def rep_a(tenant_a):
    rep_role = Role.objects.create(tenant=tenant_a, name="Sales Rep", level=Role.LEVEL_REP)
    return User.objects.create_user(
        username="comp_rep_a",
        password="testpass123",
        tenant=tenant_a,
        role=rep_role,
        is_tenant_admin=False,
        email="comp_rep_a@testa.com",
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


# ------------------------------------------------------------------ commission plans
@pytest.fixture
def plan_a(tenant_a):
    return CommissionPlan.objects.create(
        tenant=tenant_a,
        name="Plan Alpha",
        code="ALPHA",
        plan_type=CommissionPlan.TYPE_FLAT,
        status=CommissionPlan.STATUS_ACTIVE,
        base_rate="5.00",
        target_quota="100000.00",
        effective_from=timezone.localdate(),
    )


@pytest.fixture
def plan_b(tenant_b):
    return CommissionPlan.objects.create(
        tenant=tenant_b,
        name="Plan Beta",
        code="BETA",
        plan_type=CommissionPlan.TYPE_TIERED,
        status=CommissionPlan.STATUS_DRAFT,
        base_rate="8.00",
        target_quota="200000.00",
        effective_from=timezone.localdate(),
    )


# ------------------------------------------------------------------ earnings
@pytest.fixture
def earning_a(tenant_a, plan_a):
    return Earning.objects.create(
        tenant=tenant_a,
        plan=plan_a,
        rep_name="Alice Smith",
        deal_reference="DEAL-001",
        deal_amount="50000.00",
        commission_amount="2500.00",
        status=Earning.STATUS_PENDING,
        earned_on=timezone.localdate(),
    )


@pytest.fixture
def earning_b(tenant_b, plan_b):
    return Earning.objects.create(
        tenant=tenant_b,
        plan=plan_b,
        rep_name="Bob Jones",
        deal_reference="DEAL-B01",
        deal_amount="30000.00",
        commission_amount="1500.00",
        status=Earning.STATUS_PENDING,
        earned_on=timezone.localdate(),
    )


# ------------------------------------------------------------------ clawbacks
@pytest.fixture
def clawback_a(tenant_a, earning_a):
    return Clawback.objects.create(
        tenant=tenant_a,
        earning=earning_a,
        rep_name="Alice Smith",
        reason=Clawback.REASON_CANCELLATION,
        status=Clawback.STATUS_OPEN,
        amount="500.00",
        effective_on=timezone.localdate(),
    )


@pytest.fixture
def clawback_b(tenant_b, earning_b):
    return Clawback.objects.create(
        tenant=tenant_b,
        earning=earning_b,
        rep_name="Bob Jones",
        reason=Clawback.REASON_REFUND,
        status=Clawback.STATUS_OPEN,
        amount="300.00",
        effective_on=timezone.localdate(),
    )


# ------------------------------------------------------------------ global plan variations
@pytest.fixture
def variation_a(tenant_a, plan_a):
    return GlobalPlanVariation.objects.create(
        tenant=tenant_a,
        plan=plan_a,
        region="North America",
        currency=GlobalPlanVariation.CURRENCY_USD,
        status=GlobalPlanVariation.STATUS_ACTIVE,
        fx_rate="1.000000",
        local_quota="100000.00",
        rate_adjustment="0.00",
        effective_from=timezone.localdate(),
    )


@pytest.fixture
def variation_b(tenant_b, plan_b):
    return GlobalPlanVariation.objects.create(
        tenant=tenant_b,
        plan=plan_b,
        region="Europe",
        currency=GlobalPlanVariation.CURRENCY_EUR,
        status=GlobalPlanVariation.STATUS_ACTIVE,
        fx_rate="0.920000",
        local_quota="80000.00",
        rate_adjustment="1.00",
        effective_from=timezone.localdate(),
    )


# ------------------------------------------------------------------ payouts
@pytest.fixture
def payout_a(tenant_a):
    return Payout.objects.create(
        tenant=tenant_a,
        rep_name="Alice Smith",
        method=Payout.METHOD_PAYROLL,
        status=Payout.STATUS_SCHEDULED,
        gross_amount="5000.00",
        deductions="500.00",
        net_amount="4500.00",
        period_label="2026-Q1",
        scheduled_on=timezone.localdate(),
    )


@pytest.fixture
def payout_b(tenant_b):
    return Payout.objects.create(
        tenant=tenant_b,
        rep_name="Bob Jones",
        method=Payout.METHOD_BANK,
        status=Payout.STATUS_SCHEDULED,
        gross_amount="3000.00",
        deductions="300.00",
        net_amount="2700.00",
        period_label="2026-Q1",
        scheduled_on=timezone.localdate(),
    )
