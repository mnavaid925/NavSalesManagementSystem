"""Tests for core.utils.log_action."""
import pytest
from unittest.mock import MagicMock, patch

from apps.core.models import AuditLog, Tenant
from apps.core.utils import log_action


def _make_anon_request(tenant=None):
    """Make a mock request with an anonymous (unauthenticated) user."""
    req = MagicMock()
    req.tenant = tenant
    # AnonymousUser.is_authenticated returns False
    req.user = MagicMock()
    req.user.is_authenticated = False
    return req


@pytest.mark.django_db
class TestLogAction:
    def test_creates_audit_log_row(self, tenant):
        from apps.accounts.models import User
        user = User.objects.create_user(
            username="logger", password="pass", tenant=tenant, is_tenant_admin=True
        )
        # Build a request object with a real authenticated user
        req = MagicMock()
        req.tenant = tenant
        req.user = user  # real User, is_authenticated returns True

        before_count = AuditLog.objects.count()
        log_action(req, AuditLog.ACTION_CREATE, model_name="TestModel", detail="some detail")
        assert AuditLog.objects.count() == before_count + 1

    def test_log_scoped_to_tenant(self, tenant):
        from apps.accounts.models import User
        user = User.objects.create_user(
            username="logger2", password="pass", tenant=tenant, is_tenant_admin=True
        )
        req = MagicMock()
        req.tenant = tenant
        req.user = user

        log_action(req, AuditLog.ACTION_UPDATE, model_name="Invoice", detail="updated")
        log = AuditLog.objects.filter(model_name="Invoice").latest("created_at")
        assert log.tenant == tenant

    def test_log_records_user(self, tenant):
        from apps.accounts.models import User
        user = User.objects.create_user(
            username="logger3", password="pass", tenant=tenant, is_tenant_admin=True
        )
        req = MagicMock()
        req.tenant = tenant
        req.user = user

        log_action(req, AuditLog.ACTION_CREATE, model_name="Role")
        log = AuditLog.objects.filter(model_name="Role").latest("created_at")
        assert log.user == user

    def test_log_with_instance_gets_model_name_and_repr(self, tenant):
        from apps.accounts.models import User
        user = User.objects.create_user(
            username="logger4", password="pass", tenant=tenant, is_tenant_admin=True
        )
        req = MagicMock()
        req.tenant = tenant
        req.user = user

        log_action(req, AuditLog.ACTION_DELETE, instance=tenant)
        log = AuditLog.objects.filter(action=AuditLog.ACTION_DELETE).latest("created_at")
        assert log.model_name == "Tenant"
        assert log.object_repr == str(tenant)

    def test_log_with_no_tenant_stores_null(self):
        """When request.tenant is None (superuser), tenant is stored as NULL."""
        req = _make_anon_request(tenant=None)

        before_count = AuditLog.objects.count()
        log_action(req, AuditLog.ACTION_OTHER)
        assert AuditLog.objects.count() == before_count + 1
        log = AuditLog.objects.latest("created_at")
        assert log.tenant is None

    def test_log_with_unauthenticated_user_stores_null_user(self):
        req = _make_anon_request(tenant=None)

        log_action(req, AuditLog.ACTION_LOGIN)
        log = AuditLog.objects.latest("created_at")
        assert log.user is None

    def test_detail_truncated_to_255(self, tenant):
        from apps.accounts.models import User
        user = User.objects.create_user(
            username="logger5", password="pass", tenant=tenant, is_tenant_admin=True
        )
        req = MagicMock()
        req.tenant = tenant
        req.user = user
        long_detail = "x" * 500

        log_action(req, AuditLog.ACTION_OTHER, detail=long_detail)
        log = AuditLog.objects.latest("created_at")
        assert len(log.detail) <= 255

    def test_log_action_with_none_user_attribute(self):
        """getattr(request, 'user', None) is None — should not crash."""
        req = MagicMock(spec=[])  # no attributes at all, getattr returns None
        req.tenant = None

        before_count = AuditLog.objects.count()
        log_action(req, AuditLog.ACTION_OTHER)
        assert AuditLog.objects.count() == before_count + 1
