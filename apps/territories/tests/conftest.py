"""Shared fixtures for territories app tests."""
import pytest
from decimal import Decimal
from django.test import Client
from django.utils import timezone

from apps.core.models import Tenant
from apps.accounts.models import Role, User
from apps.territories.models import (
    Territory, TerritoryAssignment, QuotaPlan, CoverageModel, TerritoryPerformance,
)


@pytest.fixture
def tenant_a():
    return Tenant.objects.create(name="Territories A", slug="territories-a")


@pytest.fixture
def tenant_b():
    return Tenant.objects.create(name="Territories B", slug="territories-b")


@pytest.fixture
def role_a(tenant_a):
    return Role.objects.create(tenant=tenant_a, name="Administrator", level=Role.LEVEL_ADMIN)


@pytest.fixture
def role_b(tenant_b):
    return Role.objects.create(tenant=tenant_b, name="Administrator", level=Role.LEVEL_ADMIN)


@pytest.fixture
def admin_a(tenant_a, role_a):
    return User.objects.create_user(
        username="terr_admin_a",
        password="testpass123",
        tenant=tenant_a,
        role=role_a,
        is_tenant_admin=True,
        email="terr_admin_a@testa.com",
    )


@pytest.fixture
def admin_b(tenant_b, role_b):
    return User.objects.create_user(
        username="terr_admin_b",
        password="testpass123",
        tenant=tenant_b,
        role=role_b,
        is_tenant_admin=True,
        email="terr_admin_b@testb.com",
    )


@pytest.fixture
def rep_a(tenant_a):
    rep_role = Role.objects.create(tenant=tenant_a, name="Sales Rep", level=Role.LEVEL_REP)
    return User.objects.create_user(
        username="terr_rep_a",
        password="testpass123",
        tenant=tenant_a,
        role=rep_role,
        is_tenant_admin=False,
        email="terr_rep_a@testa.com",
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


# ── model fixtures for tenant_a ──────────────────────────────────────────────

@pytest.fixture
def territory_a(tenant_a):
    return Territory.objects.create(
        tenant=tenant_a,
        name="North Region",
        code="NR-001",
        territory_type=Territory.TYPE_GEOGRAPHIC,
        status=Territory.STATUS_ACTIVE,
        region="North",
        country="US",
    )


@pytest.fixture
def territory_b(tenant_b):
    return Territory.objects.create(
        tenant=tenant_b,
        name="South Region",
        code="SR-001",
        territory_type=Territory.TYPE_GEOGRAPHIC,
        status=Territory.STATUS_ACTIVE,
        region="South",
        country="US",
    )


@pytest.fixture
def assignment_a(tenant_a, territory_a):
    return TerritoryAssignment.objects.create(
        tenant=tenant_a,
        territory=territory_a,
        rep_name="Alice Smith",
        rep_email="alice@example.com",
        assignment_role=TerritoryAssignment.ROLE_OWNER,
        status=TerritoryAssignment.STATUS_ACTIVE,
        effective_date=timezone.localdate(),
    )


@pytest.fixture
def assignment_b(tenant_b, territory_b):
    return TerritoryAssignment.objects.create(
        tenant=tenant_b,
        territory=territory_b,
        rep_name="Bob Jones",
        rep_email="bob@example.com",
        assignment_role=TerritoryAssignment.ROLE_OWNER,
        status=TerritoryAssignment.STATUS_ACTIVE,
        effective_date=timezone.localdate(),
    )


@pytest.fixture
def quota_plan_a(tenant_a, territory_a):
    return QuotaPlan.objects.create(
        tenant=tenant_a,
        territory=territory_a,
        name="Q1 Plan",
        period_type=QuotaPlan.PERIOD_QUARTERLY,
        fiscal_year=2026,
        status=QuotaPlan.STATUS_DRAFT,
        target_amount="50000.00",
    )


@pytest.fixture
def quota_plan_b(tenant_b, territory_b):
    return QuotaPlan.objects.create(
        tenant=tenant_b,
        territory=territory_b,
        name="Q1 Plan B",
        period_type=QuotaPlan.PERIOD_QUARTERLY,
        fiscal_year=2026,
        status=QuotaPlan.STATUS_DRAFT,
        target_amount="30000.00",
    )


@pytest.fixture
def coverage_model_a(tenant_a):
    return CoverageModel.objects.create(
        tenant=tenant_a,
        name="Direct Field Model",
        model_type=CoverageModel.MODEL_DIRECT,
        status=CoverageModel.STATUS_PROPOSED,
        target_ratio="50.00",
        rep_capacity=5,
    )


@pytest.fixture
def coverage_model_b(tenant_b):
    return CoverageModel.objects.create(
        tenant=tenant_b,
        name="Inside Sales Model",
        model_type=CoverageModel.MODEL_INSIDE,
        status=CoverageModel.STATUS_PROPOSED,
        target_ratio="30.00",
        rep_capacity=3,
    )


@pytest.fixture
def performance_a(tenant_a, territory_a):
    return TerritoryPerformance.objects.create(
        tenant=tenant_a,
        territory=territory_a,
        period_type=TerritoryPerformance.PERIOD_QUARTERLY,
        period_label="Q1 2026",
        rating=TerritoryPerformance.RATING_ON_TRACK,
        quota_amount=Decimal("50000.00"),
        actual_amount=Decimal("45000.00"),
        pipeline_amount=Decimal("60000.00"),
        deals_won=5,
    )


@pytest.fixture
def performance_b(tenant_b, territory_b):
    return TerritoryPerformance.objects.create(
        tenant=tenant_b,
        territory=territory_b,
        period_type=TerritoryPerformance.PERIOD_QUARTERLY,
        period_label="Q1 2026",
        rating=TerritoryPerformance.RATING_AT_RISK,
        quota_amount=Decimal("30000.00"),
        actual_amount=Decimal("10000.00"),
        pipeline_amount=Decimal("20000.00"),
        deals_won=2,
    )
