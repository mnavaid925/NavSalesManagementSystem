"""Shared fixtures for activities app tests."""
import pytest
from django.test import Client
from django.utils import timezone

from apps.core.models import Tenant
from apps.accounts.models import Role, User
from apps.activities.models import Activity, SalesTask, Meeting, EmailLog, SalesPlan


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


# ------------------------------------------------------------------ Activity fixtures
@pytest.fixture
def activity_a(tenant_a):
    return Activity.objects.create(
        tenant=tenant_a,
        subject="Call with Acme",
        activity_type=Activity.TYPE_CALL,
        direction=Activity.DIRECTION_OUTBOUND,
        outcome=Activity.OUTCOME_PENDING,
        contact_name="John Doe",
        company_name="Acme Corp",
        activity_date=timezone.localdate(),
    )


@pytest.fixture
def activity_b(tenant_b):
    return Activity.objects.create(
        tenant=tenant_b,
        subject="B Corp Email",
        activity_type=Activity.TYPE_EMAIL,
        direction=Activity.DIRECTION_INBOUND,
        outcome=Activity.OUTCOME_SUCCESSFUL,
        contact_name="Jane Smith",
        company_name="B Corp",
        activity_date=timezone.localdate(),
    )


# ------------------------------------------------------------------ SalesTask fixtures
@pytest.fixture
def salestask_a(tenant_a, activity_a):
    return SalesTask.objects.create(
        tenant=tenant_a,
        title="Follow up with Acme",
        activity=activity_a,
        priority=SalesTask.PRIORITY_HIGH,
        status=SalesTask.STATUS_OPEN,
        assigned_to="rep_a",
        due_date=timezone.localdate(),
    )


@pytest.fixture
def salestask_b(tenant_b):
    return SalesTask.objects.create(
        tenant=tenant_b,
        title="B Corp Task",
        priority=SalesTask.PRIORITY_LOW,
        status=SalesTask.STATUS_OPEN,
    )


# ------------------------------------------------------------------ Meeting fixtures
@pytest.fixture
def meeting_a(tenant_a):
    return Meeting.objects.create(
        tenant=tenant_a,
        title="Discovery Call with Acme",
        meeting_type=Meeting.TYPE_DISCOVERY,
        location_type=Meeting.LOCATION_VIDEO,
        status=Meeting.STATUS_SCHEDULED,
        scheduled_date=timezone.localdate(),
        organizer_name="admin_a",
    )


@pytest.fixture
def meeting_b(tenant_b):
    return Meeting.objects.create(
        tenant=tenant_b,
        title="B Corp Demo",
        meeting_type=Meeting.TYPE_DEMO,
        location_type=Meeting.LOCATION_ONSITE,
        status=Meeting.STATUS_SCHEDULED,
        scheduled_date=timezone.localdate(),
    )


# ------------------------------------------------------------------ EmailLog fixtures
@pytest.fixture
def emaillog_a(tenant_a, activity_a):
    return EmailLog.objects.create(
        tenant=tenant_a,
        subject="Acme Proposal Email",
        direction=EmailLog.DIRECTION_OUTBOUND,
        status=EmailLog.STATUS_DRAFT,
        from_email="rep@testa.com",
        to_email="john@acme.com",
        activity=activity_a,
    )


@pytest.fixture
def emaillog_b(tenant_b):
    return EmailLog.objects.create(
        tenant=tenant_b,
        subject="B Corp Intro",
        direction=EmailLog.DIRECTION_OUTBOUND,
        status=EmailLog.STATUS_DRAFT,
        from_email="rep@testb.com",
        to_email="jane@bcorp.com",
    )


# ------------------------------------------------------------------ SalesPlan fixtures
@pytest.fixture
def salesplan_a(tenant_a):
    return SalesPlan.objects.create(
        tenant=tenant_a,
        title="Q1 Weekly Plan",
        period_type=SalesPlan.PERIOD_WEEKLY,
        status=SalesPlan.STATUS_DRAFT,
        start_date=timezone.localdate(),
        target_calls=20,
        target_meetings=5,
        revenue_goal="10000.00",
    )


@pytest.fixture
def salesplan_b(tenant_b):
    return SalesPlan.objects.create(
        tenant=tenant_b,
        title="B Corp Plan",
        period_type=SalesPlan.PERIOD_MONTHLY,
        status=SalesPlan.STATUS_ACTIVE,
        start_date=timezone.localdate(),
    )
