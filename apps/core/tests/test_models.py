"""Tests for core.models: Tenant and AuditLog."""
import pytest
from django.utils import timezone

from apps.core.models import AuditLog, Tenant


@pytest.mark.django_db
class TestTenant:
    def test_str_returns_name(self):
        t = Tenant.objects.create(name="Globex Corp", slug="globex")
        assert str(t) == "Globex Corp"

    def test_default_status_is_trial(self):
        t = Tenant.objects.create(name="Startup", slug="startup")
        assert t.status == Tenant.STATUS_TRIAL

    def test_default_is_active_true(self):
        t = Tenant.objects.create(name="Active Co", slug="active-co")
        assert t.is_active is True

    def test_status_choices_contain_all_three(self):
        choices = dict(Tenant.STATUS_CHOICES)
        assert Tenant.STATUS_TRIAL in choices
        assert Tenant.STATUS_ACTIVE in choices
        assert Tenant.STATUS_SUSPENDED in choices

    def test_slug_is_unique(self, tenant):
        import django.db.utils as db_utils
        with pytest.raises(db_utils.IntegrityError):
            Tenant.objects.create(name="Another Acme", slug="acme")

    def test_trial_ends_on_nullable(self):
        t = Tenant.objects.create(name="NoTrial", slug="notrial")
        assert t.trial_ends_on is None

    def test_created_at_auto_populated(self):
        before = timezone.now()
        t = Tenant.objects.create(name="TimeTenant", slug="time-tenant")
        assert t.created_at >= before

    def test_ordering_by_name(self):
        Tenant.objects.create(name="Zebra Inc", slug="zebra-inc")
        Tenant.objects.create(name="Apple Inc", slug="apple-inc")
        names = list(Tenant.objects.values_list("name", flat=True))
        assert names == sorted(names)


@pytest.mark.django_db
class TestAuditLog:
    def test_str_create_action(self, tenant):
        log = AuditLog.objects.create(
            tenant=tenant,
            action=AuditLog.ACTION_CREATE,
            model_name="Invoice",
        )
        assert "Created" in str(log)
        assert "Invoice" in str(log)

    def test_str_with_no_model_name(self, tenant):
        log = AuditLog.objects.create(
            tenant=tenant,
            action=AuditLog.ACTION_LOGIN,
        )
        # Should not crash; just returns action display
        assert str(log) is not None

    def test_action_choices_contain_all_five(self):
        choices = dict(AuditLog.ACTION_CHOICES)
        for action in [
            AuditLog.ACTION_CREATE,
            AuditLog.ACTION_UPDATE,
            AuditLog.ACTION_DELETE,
            AuditLog.ACTION_LOGIN,
            AuditLog.ACTION_OTHER,
        ]:
            assert action in choices

    def test_tenant_nullable(self):
        log = AuditLog.objects.create(action=AuditLog.ACTION_OTHER)
        assert log.tenant is None

    def test_user_nullable(self, tenant):
        log = AuditLog.objects.create(tenant=tenant, action=AuditLog.ACTION_CREATE)
        assert log.user is None

    def test_created_at_default_is_now(self):
        before = timezone.now()
        log = AuditLog.objects.create(action=AuditLog.ACTION_OTHER)
        assert log.created_at >= before

    def test_ordering_newest_first(self, tenant):
        from django.utils import timezone
        from datetime import timedelta
        # Use explicit timestamps so ordering is deterministic even on fast in-memory SQLite
        t0 = timezone.now() - timedelta(seconds=10)
        t1 = timezone.now()
        AuditLog.objects.create(tenant=tenant, action=AuditLog.ACTION_CREATE, model_name="A", created_at=t0)
        AuditLog.objects.create(tenant=tenant, action=AuditLog.ACTION_UPDATE, model_name="B", created_at=t1)
        logs = list(AuditLog.objects.filter(tenant=tenant))
        # Newest first: B should be before A
        assert logs[0].model_name == "B"
        assert logs[1].model_name == "A"
