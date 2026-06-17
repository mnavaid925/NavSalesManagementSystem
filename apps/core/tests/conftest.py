"""Shared fixtures for core app tests."""
import pytest
from django.test import Client

from apps.core.models import Tenant
from apps.core.navigation import reset_sidebar_cache


@pytest.fixture(autouse=True)
def clear_sidebar_cache():
    """Ensure sidebar cache doesn't bleed between tests."""
    reset_sidebar_cache()
    yield
    reset_sidebar_cache()


@pytest.fixture
def tenant():
    return Tenant.objects.create(name="Acme Corp", slug="acme")


@pytest.fixture
def client():
    return Client()
