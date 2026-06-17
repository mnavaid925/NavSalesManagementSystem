"""Tests for accounts.backends.EmailOrUsernameModelBackend."""
import pytest
from django.test import RequestFactory

from apps.accounts.backends import EmailOrUsernameModelBackend
from apps.accounts.models import User
from apps.core.models import Tenant


@pytest.mark.django_db
class TestEmailOrUsernameModelBackend:
    @pytest.fixture(autouse=True)
    def setup_user(self, tenant_a):
        self.backend = EmailOrUsernameModelBackend()
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="correctpassword",
            tenant=tenant_a,
        )
        self.factory = RequestFactory()
        self.request = self.factory.get("/")

    def test_authenticate_by_username(self):
        user = self.backend.authenticate(
            self.request, username="testuser", password="correctpassword"
        )
        assert user is not None
        assert user.pk == self.user.pk

    def test_authenticate_by_email(self):
        user = self.backend.authenticate(
            self.request, username="testuser@example.com", password="correctpassword"
        )
        assert user is not None
        assert user.pk == self.user.pk

    def test_authenticate_by_email_case_insensitive(self):
        user = self.backend.authenticate(
            self.request, username="TESTUSER@EXAMPLE.COM", password="correctpassword"
        )
        assert user is not None

    def test_authenticate_by_username_case_insensitive(self):
        user = self.backend.authenticate(
            self.request, username="TESTUSER", password="correctpassword"
        )
        assert user is not None

    def test_wrong_password_fails(self):
        user = self.backend.authenticate(
            self.request, username="testuser", password="wrongpassword"
        )
        assert user is None

    def test_nonexistent_user_fails(self):
        user = self.backend.authenticate(
            self.request, username="doesnotexist", password="anything"
        )
        assert user is None

    def test_none_username_fails(self):
        user = self.backend.authenticate(
            self.request, username=None, password="correctpassword"
        )
        assert user is None

    def test_none_password_fails(self):
        user = self.backend.authenticate(
            self.request, username="testuser", password=None
        )
        assert user is None

    def test_inactive_user_fails(self, tenant_a):
        inactive = User.objects.create_user(
            username="inactiveuser", email="inactive@example.com",
            password="correctpassword", tenant=tenant_a, is_active=False,
        )
        user = self.backend.authenticate(
            self.request, username="inactiveuser", password="correctpassword"
        )
        assert user is None
