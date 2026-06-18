"""Shared fixtures for enablement app tests."""
import pytest
from django.test import Client
from django.utils import timezone

from apps.core.models import Tenant
from apps.accounts.models import Role, User
from apps.enablement.models import (
    CallRecording, CompetitiveCard, ContentAsset, Playbook, TrainingRecord,
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


# ------------------------------------------------------------------ rep (non-admin)
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


# ------------------------------------------------------------------ ContentAsset fixtures
@pytest.fixture
def asset_a(tenant_a):
    return ContentAsset.objects.create(
        tenant=tenant_a,
        title="Sales Deck Q1",
        asset_type=ContentAsset.TYPE_DECK,
        status=ContentAsset.STATUS_DRAFT,
    )


@pytest.fixture
def asset_b(tenant_b):
    return ContentAsset.objects.create(
        tenant=tenant_b,
        title="B Corp One-Pager",
        asset_type=ContentAsset.TYPE_ONE_PAGER,
        status=ContentAsset.STATUS_PUBLISHED,
    )


# ------------------------------------------------------------------ Playbook fixtures
@pytest.fixture
def playbook_a(tenant_a):
    return Playbook.objects.create(
        tenant=tenant_a,
        title="Discovery Playbook",
        stage=Playbook.STAGE_DISCOVERY,
        status=Playbook.STATUS_ACTIVE,
    )


@pytest.fixture
def playbook_b(tenant_b):
    return Playbook.objects.create(
        tenant=tenant_b,
        title="B Corp Playbook",
        stage=Playbook.STAGE_PROSPECTING,
        status=Playbook.STATUS_DRAFT,
    )


# ------------------------------------------------------------------ TrainingRecord fixtures
@pytest.fixture
def training_a(tenant_a):
    return TrainingRecord.objects.create(
        tenant=tenant_a,
        course_name="Sales Foundations",
        rep_name="Alice",
        kind=TrainingRecord.KIND_COURSE,
        status=TrainingRecord.STATUS_NOT_STARTED,
        enrolled_on=timezone.localdate(),
    )


@pytest.fixture
def training_b(tenant_b):
    return TrainingRecord.objects.create(
        tenant=tenant_b,
        course_name="B Corp Training",
        rep_name="Bob",
        kind=TrainingRecord.KIND_WORKSHOP,
        status=TrainingRecord.STATUS_IN_PROGRESS,
        enrolled_on=timezone.localdate(),
    )


# ------------------------------------------------------------------ CallRecording fixtures
@pytest.fixture
def recording_a(tenant_a):
    return CallRecording.objects.create(
        tenant=tenant_a,
        title="Discovery Call — Alice",
        rep_name="Alice",
        call_type=CallRecording.TYPE_DISCOVERY,
        status=CallRecording.STATUS_PENDING,
        call_date=timezone.localdate(),
    )


@pytest.fixture
def recording_b(tenant_b):
    return CallRecording.objects.create(
        tenant=tenant_b,
        title="B Corp Demo Call",
        rep_name="Bob",
        call_type=CallRecording.TYPE_DEMO,
        status=CallRecording.STATUS_REVIEWED,
        call_date=timezone.localdate(),
    )


# ------------------------------------------------------------------ CompetitiveCard fixtures
@pytest.fixture
def card_a(tenant_a):
    return CompetitiveCard.objects.create(
        tenant=tenant_a,
        competitor_name="Acme Corp",
        threat_level=CompetitiveCard.THREAT_HIGH,
        status=CompetitiveCard.STATUS_PUBLISHED,
        last_updated_on=timezone.localdate(),
    )


@pytest.fixture
def card_b(tenant_b):
    return CompetitiveCard.objects.create(
        tenant=tenant_b,
        competitor_name="B Rival Inc",
        threat_level=CompetitiveCard.THREAT_LOW,
        status=CompetitiveCard.STATUS_DRAFT,
        last_updated_on=timezone.localdate(),
    )
