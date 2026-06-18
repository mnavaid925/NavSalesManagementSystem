"""Shared fixtures for crm app tests."""
import pytest
from django.test import Client

from apps.core.models import Tenant
from apps.accounts.models import Role, User
from apps.crm.models import Account, AccountPlan, AccountTier, Contact, RelationshipMap


# ============================================================ tenants
@pytest.fixture
def tenant_a():
    return Tenant.objects.create(name="CRM Tenant A", slug="crm-tenant-a")


@pytest.fixture
def tenant_b():
    return Tenant.objects.create(name="CRM Tenant B", slug="crm-tenant-b")


# ============================================================ roles
@pytest.fixture
def role_a(tenant_a):
    return Role.objects.create(tenant=tenant_a, name="Administrator", level=Role.LEVEL_ADMIN)


@pytest.fixture
def role_b(tenant_b):
    return Role.objects.create(tenant=tenant_b, name="Administrator", level=Role.LEVEL_ADMIN)


# ============================================================ admin users
@pytest.fixture
def admin_a(tenant_a, role_a):
    return User.objects.create_user(
        username="crm_admin_a",
        password="testpass123",
        tenant=tenant_a,
        role=role_a,
        is_tenant_admin=True,
        email="crm_admin_a@testa.com",
    )


@pytest.fixture
def admin_b(tenant_b, role_b):
    return User.objects.create_user(
        username="crm_admin_b",
        password="testpass123",
        tenant=tenant_b,
        role=role_b,
        is_tenant_admin=True,
        email="crm_admin_b@testb.com",
    )


# ============================================================ rep user (non-admin)
@pytest.fixture
def rep_a(tenant_a):
    rep_role = Role.objects.create(tenant=tenant_a, name="Sales Rep", level=Role.LEVEL_REP)
    return User.objects.create_user(
        username="crm_rep_a",
        password="testpass123",
        tenant=tenant_a,
        role=rep_role,
        is_tenant_admin=False,
        email="crm_rep_a@testa.com",
    )


# ============================================================ logged-in clients
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


# ============================================================ AccountTier fixtures
@pytest.fixture
def tier_a(tenant_a):
    return AccountTier.objects.create(
        tenant=tenant_a,
        name="Strategic",
        segment=AccountTier.SEGMENT_STRATEGIC,
        rank=1,
    )


@pytest.fixture
def tier_b(tenant_b):
    return AccountTier.objects.create(
        tenant=tenant_b,
        name="SMB Tier",
        segment=AccountTier.SEGMENT_SMB,
        rank=2,
    )


# ============================================================ Account fixtures
@pytest.fixture
def account_a(tenant_a, tier_a):
    return Account.objects.create(
        tenant=tenant_a,
        name="Acme Corp",
        account_type=Account.TYPE_CUSTOMER,
        tier=tier_a,
    )


@pytest.fixture
def account_b(tenant_b):
    return Account.objects.create(
        tenant=tenant_b,
        name="Rival Corp",
        account_type=Account.TYPE_PROSPECT,
    )


# ============================================================ Contact fixtures
@pytest.fixture
def contact_a(tenant_a, account_a):
    return Contact.objects.create(
        tenant=tenant_a,
        first_name="Alice",
        last_name="Smith",
        account=account_a,
        email="alice@acme.com",
    )


@pytest.fixture
def contact_b(tenant_b, account_b):
    return Contact.objects.create(
        tenant=tenant_b,
        first_name="Bob",
        last_name="Jones",
        account=account_b,
        email="bob@rival.com",
    )


# ============================================================ secondary contact for RelationshipMap
@pytest.fixture
def contact_a2(tenant_a, account_a):
    return Contact.objects.create(
        tenant=tenant_a,
        first_name="Carol",
        last_name="White",
        account=account_a,
        email="carol@acme.com",
    )


# ============================================================ RelationshipMap fixtures
@pytest.fixture
def relmap_a(tenant_a, account_a, contact_a, contact_a2):
    return RelationshipMap.objects.create(
        tenant=tenant_a,
        account=account_a,
        from_contact=contact_a,
        to_contact=contact_a2,
        relationship_type=RelationshipMap.TYPE_REPORTS_TO,
        strength=RelationshipMap.STRENGTH_STRONG,
    )


@pytest.fixture
def relmap_b(tenant_b, account_b, contact_b):
    # Need a second contact for tenant_b
    contact_b2 = Contact.objects.create(
        tenant=tenant_b,
        first_name="Dave",
        last_name="Brown",
        account=account_b,
        email="dave@rival.com",
    )
    return RelationshipMap.objects.create(
        tenant=tenant_b,
        account=account_b,
        from_contact=contact_b,
        to_contact=contact_b2,
        relationship_type=RelationshipMap.TYPE_PEER,
    )


# ============================================================ AccountPlan fixtures
@pytest.fixture
def plan_a(tenant_a, account_a):
    return AccountPlan.objects.create(
        tenant=tenant_a,
        account=account_a,
        title="Acme Growth Plan 2026",
        status=AccountPlan.STATUS_DRAFT,
    )


@pytest.fixture
def plan_b(tenant_b, account_b):
    return AccountPlan.objects.create(
        tenant=tenant_b,
        account=account_b,
        title="Rival Growth Plan 2026",
        status=AccountPlan.STATUS_DRAFT,
    )
