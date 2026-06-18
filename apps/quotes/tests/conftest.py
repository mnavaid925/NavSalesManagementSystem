"""Shared fixtures for quotes app tests."""
from decimal import Decimal

import pytest
from django.test import Client

from apps.core.models import Tenant
from apps.accounts.models import Role, User
from apps.quotes.models import (
    PricingRule, Proposal, Quote, QuoteLineItem, QuoteVersion,
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


# ------------------------------------------------------------------ Quote fixtures
@pytest.fixture
def quote_a(tenant_a):
    return Quote.objects.create(
        tenant=tenant_a,
        title="Quote Alpha",
        account_name="Acme Corp",
        contact_name="Alice",
        contact_email="alice@acme.com",
        status=Quote.STATUS_DRAFT,
        currency=Quote.CURRENCY_USD,
    )


@pytest.fixture
def quote_b(tenant_b):
    return Quote.objects.create(
        tenant=tenant_b,
        title="Quote Beta",
        account_name="Rival Ltd",
        status=Quote.STATUS_DRAFT,
    )


# ------------------------------------------------------------------ QuoteLineItem fixtures
@pytest.fixture
def line_item_a(tenant_a, quote_a):
    return QuoteLineItem.objects.create(
        tenant=tenant_a,
        quote=quote_a,
        product_name="Widget Pro",
        sku="WP-001",
        unit=QuoteLineItem.UNIT_EACH,
        quantity=Decimal("2"),
        unit_price=Decimal("50.00"),
        discount_percent=Decimal("10.00"),
    )


@pytest.fixture
def line_item_b(tenant_b, quote_b):
    return QuoteLineItem.objects.create(
        tenant=tenant_b,
        quote=quote_b,
        product_name="Gadget Basic",
        unit=QuoteLineItem.UNIT_EACH,
        quantity=Decimal("1"),
        unit_price=Decimal("100.00"),
        discount_percent=Decimal("0"),
    )


# ------------------------------------------------------------------ PricingRule fixtures
@pytest.fixture
def pricing_rule_a(tenant_a):
    return PricingRule.objects.create(
        tenant=tenant_a,
        name="Volume 10%",
        rule_type=PricingRule.RULE_VOLUME,
        min_discount_percent="5.00",
        max_discount_percent="10.00",
        approval_level=PricingRule.APPROVAL_AUTO,
        status=PricingRule.STATUS_ACTIVE,
    )


@pytest.fixture
def pricing_rule_b(tenant_b):
    return PricingRule.objects.create(
        tenant=tenant_b,
        name="Promo 15%",
        rule_type=PricingRule.RULE_PROMO,
        min_discount_percent="10.00",
        max_discount_percent="15.00",
        approval_level=PricingRule.APPROVAL_MANAGER,
        status=PricingRule.STATUS_ACTIVE,
    )


# ------------------------------------------------------------------ Proposal fixtures
@pytest.fixture
def proposal_a(tenant_a, quote_a):
    return Proposal.objects.create(
        tenant=tenant_a,
        quote=quote_a,
        title="Alpha Proposal",
        template=Proposal.TEMPLATE_STANDARD,
        status=Proposal.STATUS_DRAFT,
        prepared_by="Alice",
    )


@pytest.fixture
def proposal_b(tenant_b, quote_b):
    return Proposal.objects.create(
        tenant=tenant_b,
        quote=quote_b,
        title="Beta Proposal",
        template=Proposal.TEMPLATE_MINIMAL,
        status=Proposal.STATUS_DRAFT,
    )


# ------------------------------------------------------------------ QuoteVersion fixtures
@pytest.fixture
def quote_version_a(tenant_a, quote_a):
    return QuoteVersion.objects.create(
        tenant=tenant_a,
        quote=quote_a,
        version_number=1,
        change_type=QuoteVersion.CHANGE_INITIAL,
        total_amount="100.00",
        is_current=True,
    )


@pytest.fixture
def quote_version_b(tenant_b, quote_b):
    return QuoteVersion.objects.create(
        tenant=tenant_b,
        quote=quote_b,
        version_number=1,
        change_type=QuoteVersion.CHANGE_INITIAL,
        total_amount="200.00",
        is_current=True,
    )
