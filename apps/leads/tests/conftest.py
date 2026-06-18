"""Shared fixtures for the leads app tests."""
import pytest
from django.test import Client
from django.utils import timezone

from apps.core.models import Tenant
from apps.accounts.models import Role, User
from apps.leads.models import (
    Lead, LeadConversion, LeadScore, LeadSource, NurtureCampaign,
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


# ------------------------------------------------------------------ non-admin rep
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


# ------------------------------------------------------------------ LeadSource fixtures
@pytest.fixture
def leadsource_a(tenant_a):
    return LeadSource.objects.create(
        tenant=tenant_a,
        name="Web Form A",
        source_type=LeadSource.TYPE_WEB_FORM,
        status=LeadSource.STATUS_ACTIVE,
    )


@pytest.fixture
def leadsource_b(tenant_b):
    return LeadSource.objects.create(
        tenant=tenant_b,
        name="Web Form B",
        source_type=LeadSource.TYPE_WEB_FORM,
        status=LeadSource.STATUS_ACTIVE,
    )


# ------------------------------------------------------------------ NurtureCampaign fixtures
@pytest.fixture
def campaign_a(tenant_a):
    return NurtureCampaign.objects.create(
        tenant=tenant_a,
        name="Campaign A",
        channel=NurtureCampaign.CHANNEL_EMAIL,
        status=NurtureCampaign.STATUS_DRAFT,
    )


@pytest.fixture
def campaign_b(tenant_b):
    return NurtureCampaign.objects.create(
        tenant=tenant_b,
        name="Campaign B",
        channel=NurtureCampaign.CHANNEL_EMAIL,
        status=NurtureCampaign.STATUS_DRAFT,
    )


# ------------------------------------------------------------------ Lead fixtures
@pytest.fixture
def lead_a(tenant_a, leadsource_a):
    return Lead.objects.create(
        tenant=tenant_a,
        source=leadsource_a,
        first_name="Alice",
        last_name="Smith",
        email="alice@example.com",
        status=Lead.STATUS_NEW,
        rating=Lead.RATING_WARM,
    )


@pytest.fixture
def lead_b(tenant_b, leadsource_b):
    return Lead.objects.create(
        tenant=tenant_b,
        source=leadsource_b,
        first_name="Bob",
        last_name="Jones",
        email="bob@example.com",
        status=Lead.STATUS_NEW,
        rating=Lead.RATING_COLD,
    )


# ------------------------------------------------------------------ LeadScore fixtures
@pytest.fixture
def leadscore_a(tenant_a, lead_a):
    return LeadScore.objects.create(
        tenant=tenant_a,
        lead=lead_a,
        score=75,
        grade=LeadScore.GRADE_B,
        scoring_model=LeadScore.MODEL_RULES,
    )


@pytest.fixture
def leadscore_b(tenant_b, lead_b):
    return LeadScore.objects.create(
        tenant=tenant_b,
        lead=lead_b,
        score=30,
        grade=LeadScore.GRADE_D,
        scoring_model=LeadScore.MODEL_MANUAL,
    )


# ------------------------------------------------------------------ LeadConversion fixtures
@pytest.fixture
def leadconversion_a(tenant_a, lead_a):
    return LeadConversion.objects.create(
        tenant=tenant_a,
        lead=lead_a,
        status=LeadConversion.STATUS_PENDING,
        outcome=LeadConversion.OUTCOME_OPPORTUNITY,
    )


@pytest.fixture
def leadconversion_b(tenant_b, lead_b):
    return LeadConversion.objects.create(
        tenant=tenant_b,
        lead=lead_b,
        status=LeadConversion.STATUS_PENDING,
        outcome=LeadConversion.OUTCOME_OPPORTUNITY,
    )
