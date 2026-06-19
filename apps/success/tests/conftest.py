"""Shared fixtures for success app tests."""
import pytest
from django.test import Client
from django.utils import timezone

from apps.core.models import Tenant
from apps.accounts.models import Role, User
from apps.success.models import (
    HealthScore, Renewal, OnboardingPlan, Advocacy, QBR,
)


# ------------------------------------------------------------------ tenants
@pytest.fixture
def tenant_a():
    return Tenant.objects.create(name="Success Tenant A", slug="success-tenant-a")


@pytest.fixture
def tenant_b():
    return Tenant.objects.create(name="Success Tenant B", slug="success-tenant-b")


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
        username="success_admin_a",
        password="testpass123",
        tenant=tenant_a,
        role=role_a,
        is_tenant_admin=True,
        email="success_admin_a@testa.com",
    )


@pytest.fixture
def admin_b(tenant_b, role_b):
    return User.objects.create_user(
        username="success_admin_b",
        password="testpass123",
        tenant=tenant_b,
        role=role_b,
        is_tenant_admin=True,
        email="success_admin_b@testb.com",
    )


# ------------------------------------------------------------------ rep (non-admin)
@pytest.fixture
def rep_a(tenant_a):
    rep_role = Role.objects.create(tenant=tenant_a, name="Sales Rep", level=Role.LEVEL_REP)
    return User.objects.create_user(
        username="success_rep_a",
        password="testpass123",
        tenant=tenant_a,
        role=rep_role,
        is_tenant_admin=False,
        email="success_rep_a@testa.com",
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


# ------------------------------------------------------------------ health scores
@pytest.fixture
def healthscore_a(tenant_a):
    return HealthScore.objects.create(
        tenant=tenant_a,
        account_name="Acme Corp",
        owner="Alice Smith",
        score=75,
        risk_level=HealthScore.RISK_LOW,
        trend=HealthScore.TREND_IMPROVING,
        arr="120000.00",
        last_reviewed=timezone.localdate(),
    )


@pytest.fixture
def healthscore_b(tenant_b):
    return HealthScore.objects.create(
        tenant=tenant_b,
        account_name="Globex Corp",
        owner="Bob Jones",
        score=30,
        risk_level=HealthScore.RISK_HIGH,
        trend=HealthScore.TREND_DECLINING,
        arr="50000.00",
        last_reviewed=timezone.localdate(),
    )


# ------------------------------------------------------------------ renewals
@pytest.fixture
def renewal_a(tenant_a):
    return Renewal.objects.create(
        tenant=tenant_a,
        account_name="Acme Corp",
        owner="Alice Smith",
        renewal_type=Renewal.TYPE_RENEWAL,
        status=Renewal.STATUS_OPEN,
        arr_current="100000.00",
        arr_proposed="110000.00",
        probability=70,
        renewal_date=timezone.localdate(),
    )


@pytest.fixture
def renewal_b(tenant_b):
    return Renewal.objects.create(
        tenant=tenant_b,
        account_name="Globex Corp",
        owner="Bob Jones",
        renewal_type=Renewal.TYPE_UPSELL,
        status=Renewal.STATUS_AT_RISK,
        arr_current="50000.00",
        arr_proposed="60000.00",
        probability=40,
        renewal_date=timezone.localdate(),
    )


# ------------------------------------------------------------------ onboarding plans
@pytest.fixture
def onboardingplan_a(tenant_a):
    return OnboardingPlan.objects.create(
        tenant=tenant_a,
        account_name="Acme Corp",
        plan_name="Acme Onboarding Q1",
        owner="Alice Smith",
        status=OnboardingPlan.STATUS_IN_PROGRESS,
        progress_pct=50,
        start_date=timezone.localdate(),
    )


@pytest.fixture
def onboardingplan_b(tenant_b):
    return OnboardingPlan.objects.create(
        tenant=tenant_b,
        account_name="Globex Corp",
        plan_name="Globex Onboarding Q2",
        owner="Bob Jones",
        status=OnboardingPlan.STATUS_NOT_STARTED,
        progress_pct=0,
        start_date=timezone.localdate(),
    )


# ------------------------------------------------------------------ advocacy
@pytest.fixture
def advocacy_a(tenant_a):
    return Advocacy.objects.create(
        tenant=tenant_a,
        account_name="Acme Corp",
        contact_name="Alice Smith",
        advocacy_type=Advocacy.TYPE_REFERENCE,
        status=Advocacy.STATUS_ACTIVE,
    )


@pytest.fixture
def advocacy_b(tenant_b):
    return Advocacy.objects.create(
        tenant=tenant_b,
        account_name="Globex Corp",
        contact_name="Bob Jones",
        advocacy_type=Advocacy.TYPE_CASE_STUDY,
        status=Advocacy.STATUS_NOMINATED,
    )


# ------------------------------------------------------------------ QBRs
@pytest.fixture
def qbr_a(tenant_a):
    return QBR.objects.create(
        tenant=tenant_a,
        account_name="Acme Corp",
        period_label="2026-Q1",
        owner="Alice Smith",
        status=QBR.STATUS_SCHEDULED,
        sentiment=QBR.SENTIMENT_POSITIVE,
        scheduled_on=timezone.localdate(),
    )


@pytest.fixture
def qbr_b(tenant_b):
    return QBR.objects.create(
        tenant=tenant_b,
        account_name="Globex Corp",
        period_label="2026-Q2",
        owner="Bob Jones",
        status=QBR.STATUS_COMPLETED,
        sentiment=QBR.SENTIMENT_NEUTRAL,
        scheduled_on=timezone.localdate(),
    )
