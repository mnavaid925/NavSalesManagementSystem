"""Shared fixtures for the opportunities app tests."""
import pytest
from django.test import Client

from apps.core.models import Tenant
from apps.accounts.models import Role, User
from apps.opportunities.models import (
    Competitor,
    DealCollaborator,
    Opportunity,
    OpportunityActivity,
    PipelineStage,
)


# ──────────────────────────── tenants ────────────────────────────

@pytest.fixture
def tenant_a():
    return Tenant.objects.create(name="Acme Corp", slug="acme-corp")


@pytest.fixture
def tenant_b():
    return Tenant.objects.create(name="Rival Inc", slug="rival-inc")


# ──────────────────────────── roles ──────────────────────────────

@pytest.fixture
def role_a(tenant_a):
    return Role.objects.create(tenant=tenant_a, name="Administrator", level=Role.LEVEL_ADMIN)


@pytest.fixture
def role_b(tenant_b):
    return Role.objects.create(tenant=tenant_b, name="Administrator", level=Role.LEVEL_ADMIN)


# ──────────────────────────── users ──────────────────────────────

@pytest.fixture
def admin_a(tenant_a, role_a):
    return User.objects.create_user(
        username="admin_opp_a",
        password="testpass123",
        tenant=tenant_a,
        role=role_a,
        is_tenant_admin=True,
        email="admin_opp_a@acme.com",
    )


@pytest.fixture
def admin_b(tenant_b, role_b):
    return User.objects.create_user(
        username="admin_opp_b",
        password="testpass123",
        tenant=tenant_b,
        role=role_b,
        is_tenant_admin=True,
        email="admin_opp_b@rival.com",
    )


@pytest.fixture
def rep_a(tenant_a):
    rep_role = Role.objects.create(tenant=tenant_a, name="Sales Rep", level=Role.LEVEL_REP)
    return User.objects.create_user(
        username="rep_opp_a",
        password="testpass123",
        tenant=tenant_a,
        role=rep_role,
        is_tenant_admin=False,
        email="rep_opp_a@acme.com",
    )


# ──────────────────────────── clients ────────────────────────────

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


# ──────────────────────────── pipeline stages ────────────────────

@pytest.fixture
def stage_a(tenant_a):
    return PipelineStage.objects.create(
        tenant=tenant_a,
        name="Qualification",
        order=1,
        probability=20,
        stage_type=PipelineStage.TYPE_OPEN,
    )


@pytest.fixture
def stage_b(tenant_b):
    return PipelineStage.objects.create(
        tenant=tenant_b,
        name="B Qualification",
        order=1,
        probability=20,
        stage_type=PipelineStage.TYPE_OPEN,
    )


# ──────────────────────────── opportunities ──────────────────────

@pytest.fixture
def opportunity_a(tenant_a, stage_a):
    return Opportunity.objects.create(
        tenant=tenant_a,
        name="Big Deal",
        account_name="ACME Customer",
        stage=stage_a,
        status=Opportunity.STATUS_OPEN,
        priority=Opportunity.PRIORITY_HIGH,
        amount="50000.00",
        probability=60,
        owner_name="Alice",
    )


@pytest.fixture
def opportunity_b(tenant_b, stage_b):
    return Opportunity.objects.create(
        tenant=tenant_b,
        name="Rival Deal",
        account_name="Rival Customer",
        stage=stage_b,
        status=Opportunity.STATUS_OPEN,
        priority=Opportunity.PRIORITY_MEDIUM,
        amount="30000.00",
        probability=40,
        owner_name="Bob",
    )


# ──────────────────────────── activities ─────────────────────────

@pytest.fixture
def activity_a(tenant_a, opportunity_a):
    return OpportunityActivity.objects.create(
        tenant=tenant_a,
        opportunity=opportunity_a,
        subject="Initial call with ACME",
        activity_type=OpportunityActivity.TYPE_CALL,
        outcome=OpportunityActivity.OUTCOME_POSITIVE,
        performed_by="Alice",
    )


@pytest.fixture
def activity_b(tenant_b, opportunity_b):
    return OpportunityActivity.objects.create(
        tenant=tenant_b,
        opportunity=opportunity_b,
        subject="B Initial email",
        activity_type=OpportunityActivity.TYPE_EMAIL,
        outcome=OpportunityActivity.OUTCOME_PENDING,
        performed_by="Bob",
    )


# ──────────────────────────── competitors ────────────────────────

@pytest.fixture
def competitor_a(tenant_a, opportunity_a):
    return Competitor.objects.create(
        tenant=tenant_a,
        opportunity=opportunity_a,
        name="CompetitorX",
        threat_level=Competitor.THREAT_HIGH,
        status=Competitor.STATUS_ACTIVE,
        strengths="Market share",
        weaknesses="High price",
    )


@pytest.fixture
def competitor_b(tenant_b, opportunity_b):
    return Competitor.objects.create(
        tenant=tenant_b,
        opportunity=opportunity_b,
        name="CompetitorY",
        threat_level=Competitor.THREAT_LOW,
        status=Competitor.STATUS_ACTIVE,
    )


# ──────────────────────────── collaborators ──────────────────────

@pytest.fixture
def collaborator_a(tenant_a, opportunity_a):
    return DealCollaborator.objects.create(
        tenant=tenant_a,
        opportunity=opportunity_a,
        member_name="Carol Smith",
        email="carol@acme.com",
        team_role=DealCollaborator.ROLE_SALES_ENG,
        status=DealCollaborator.STATUS_ACTIVE,
    )


@pytest.fixture
def collaborator_b(tenant_b, opportunity_b):
    return DealCollaborator.objects.create(
        tenant=tenant_b,
        opportunity=opportunity_b,
        member_name="Dave Jones",
        email="dave@rival.com",
        team_role=DealCollaborator.ROLE_LEGAL,
        status=DealCollaborator.STATUS_INVITED,
    )
