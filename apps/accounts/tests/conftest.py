"""Shared fixtures for accounts app tests."""
import pytest
from django.test import Client

from apps.core.models import Tenant
from apps.accounts.models import Role, User


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
        first_name="Alice",
        last_name="Admin",
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
