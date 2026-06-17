"""Shared fixtures for tenants app tests."""
import pytest
from django.test import Client

from apps.core.models import Tenant
from apps.accounts.models import Role, User
from apps.tenants.models import (
    OnboardingStep, Subscription, Invoice, EncryptionKey, BrandingSetting, HealthMetric
)


@pytest.fixture
def tenant_a():
    return Tenant.objects.create(name="Tenant A", slug="tenant-a")


@pytest.fixture
def tenant_b():
    return Tenant.objects.create(name="Tenant B", slug="tenant-b")


@pytest.fixture
def role_a(tenant_a):
    return Role.objects.create(tenant=tenant_a, name="Administrator", level=Role.LEVEL_ADMIN)


@pytest.fixture
def role_b(tenant_b):
    return Role.objects.create(tenant=tenant_b, name="Administrator", level=Role.LEVEL_ADMIN)


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


@pytest.fixture
def subscription_a(tenant_a):
    return Subscription.objects.create(
        tenant=tenant_a,
        plan=Subscription.PLAN_STARTER,
        status=Subscription.STATUS_TRIALING,
    )


@pytest.fixture
def invoice_a(tenant_a, subscription_a):
    return Invoice.objects.create(tenant=tenant_a, subscription=subscription_a, amount="99.00")


@pytest.fixture
def invoice_b(tenant_b):
    return Invoice.objects.create(tenant=tenant_b, amount="50.00")


@pytest.fixture
def encryption_key_a(tenant_a):
    _, prefix, hashed = EncryptionKey.generate_secret()
    return EncryptionKey.objects.create(
        tenant=tenant_a, label="Test Key", key_prefix=prefix, hashed_key=hashed
    )


@pytest.fixture
def encryption_key_b(tenant_b):
    _, prefix, hashed = EncryptionKey.generate_secret()
    return EncryptionKey.objects.create(
        tenant=tenant_b, label="B Key", key_prefix=prefix, hashed_key=hashed
    )


@pytest.fixture
def branding_a(tenant_a):
    return BrandingSetting.objects.create(tenant=tenant_a, name="Default Brand")


@pytest.fixture
def branding_b(tenant_b):
    return BrandingSetting.objects.create(tenant=tenant_b, name="B Brand")


@pytest.fixture
def healthmetric_a(tenant_a):
    return HealthMetric.objects.create(
        tenant=tenant_a, metric_name="CPU Usage", value="42.5", unit="%"
    )


@pytest.fixture
def healthmetric_b(tenant_b):
    return HealthMetric.objects.create(
        tenant=tenant_b, metric_name="Memory Usage", value="70.0", unit="%"
    )


@pytest.fixture
def onboarding_step_a(tenant_a):
    return OnboardingStep.objects.create(
        tenant=tenant_a, title="Setup Profile", order=1
    )


@pytest.fixture
def onboarding_step_b(tenant_b):
    return OnboardingStep.objects.create(
        tenant=tenant_b, title="B Setup", order=1
    )


@pytest.fixture
def subscription_b(tenant_b):
    return Subscription.objects.create(
        tenant=tenant_b, plan=Subscription.PLAN_PRO, status=Subscription.STATUS_ACTIVE
    )
