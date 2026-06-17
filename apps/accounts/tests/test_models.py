"""Tests for accounts.models: User, Role, UserInvite."""
import pytest
from django.utils import timezone

from apps.accounts.models import Role, User, UserInvite
from apps.core.models import Tenant


@pytest.mark.django_db
class TestUser:
    def test_display_name_full_name(self, admin_a):
        admin_a.first_name = "Alice"
        admin_a.last_name = "Smith"
        admin_a.save()
        assert admin_a.display_name == "Alice Smith"

    def test_display_name_fallback_to_username(self, tenant_a):
        user = User.objects.create_user(
            username="noname_user", password="p", tenant=tenant_a,
            first_name="", last_name="",
        )
        assert user.display_name == "noname_user"

    def test_initials_with_both_names(self, admin_a):
        admin_a.first_name = "Alice"
        admin_a.last_name = "Admin"
        admin_a.save()
        assert admin_a.initials == "AA"

    def test_initials_first_name_only(self, tenant_a):
        user = User.objects.create_user(
            username="firstonly", password="p", tenant=tenant_a,
            first_name="Bob", last_name="",
        )
        assert user.initials == "B"

    def test_initials_username_fallback(self, tenant_a):
        user = User.objects.create_user(
            username="xuser", password="p", tenant=tenant_a,
            first_name="", last_name="",
        )
        assert user.initials == "X"

    def test_initials_uppercase(self, tenant_a):
        user = User.objects.create_user(
            username="user_lower", password="p", tenant=tenant_a,
            first_name="alice", last_name="smith",
        )
        assert user.initials == user.initials.upper()

    def test_is_tenant_admin_default_false(self, tenant_a):
        user = User.objects.create_user(
            username="notadmin", password="p", tenant=tenant_a
        )
        assert user.is_tenant_admin is False

    def test_user_belongs_to_tenant(self, admin_a, tenant_a):
        assert admin_a.tenant == tenant_a

    def test_user_str_is_username(self, admin_a):
        # AbstractUser __str__ returns username
        assert str(admin_a) == "admin_a"


@pytest.mark.django_db
class TestRole:
    def test_str_returns_name(self, role_a):
        assert str(role_a) == role_a.name

    def test_unique_together_tenant_name(self, tenant_a):
        Role.objects.create(tenant=tenant_a, name="Manager")
        import django.db.utils as db_utils
        with pytest.raises(db_utils.IntegrityError):
            Role.objects.create(tenant=tenant_a, name="Manager")

    def test_same_name_allowed_in_different_tenants(self, tenant_a, tenant_b):
        Role.objects.create(tenant=tenant_a, name="Unique Role")
        # Should NOT raise
        Role.objects.create(tenant=tenant_b, name="Unique Role")

    def test_default_level_is_rep(self, tenant_a):
        role = Role.objects.create(tenant=tenant_a, name="Default Role")
        assert role.level == Role.LEVEL_REP

    def test_level_choices_contain_all_five(self):
        choices = dict(Role.LEVEL_CHOICES)
        for level in [
            Role.LEVEL_REP, Role.LEVEL_MANAGER, Role.LEVEL_DIRECTOR,
            Role.LEVEL_EXECUTIVE, Role.LEVEL_ADMIN,
        ]:
            assert level in choices

    def test_is_active_default_true(self, tenant_a):
        role = Role.objects.create(tenant=tenant_a, name="NewRole")
        assert role.is_active is True

    def test_ordering_by_name(self, tenant_a):
        Role.objects.create(tenant=tenant_a, name="Zebra Role")
        Role.objects.create(tenant=tenant_a, name="Ant Role")
        names = list(Role.objects.filter(tenant=tenant_a).values_list("name", flat=True))
        assert names == sorted(names)


@pytest.mark.django_db
class TestUserInvite:
    def test_save_generates_token(self, tenant_a, admin_a):
        invite = UserInvite(tenant=tenant_a, email="new@example.com", invited_by=admin_a)
        invite.save()
        assert invite.token
        assert len(invite.token) > 10

    def test_save_sets_expires_at(self, tenant_a, admin_a):
        before = timezone.now()
        invite = UserInvite(tenant=tenant_a, email="exp@example.com", invited_by=admin_a)
        invite.save()
        assert invite.expires_at > before

    def test_expires_at_14_days_in_future(self, tenant_a, admin_a):
        from datetime import timedelta
        invite = UserInvite(tenant=tenant_a, email="exp14@example.com", invited_by=admin_a)
        invite.save()
        delta = invite.expires_at - timezone.now()
        # Should be approximately 14 days (within 1 minute tolerance)
        assert timedelta(days=13, hours=23) < delta <= timedelta(days=14, minutes=1)

    def test_token_unique(self, tenant_a, admin_a):
        i1 = UserInvite(tenant=tenant_a, email="one@x.com", invited_by=admin_a)
        i1.save()
        i2 = UserInvite(tenant=tenant_a, email="two@x.com", invited_by=admin_a)
        i2.save()
        assert i1.token != i2.token

    def test_is_actionable_pending_not_expired(self, tenant_a, admin_a):
        invite = UserInvite(tenant=tenant_a, email="act@example.com", invited_by=admin_a)
        invite.save()
        assert invite.is_actionable is True

    def test_is_actionable_false_when_accepted(self, tenant_a, admin_a):
        invite = UserInvite(tenant=tenant_a, email="acc@example.com", invited_by=admin_a)
        invite.save()
        invite.status = UserInvite.STATUS_ACCEPTED
        invite.save()
        assert invite.is_actionable is False

    def test_is_actionable_false_when_revoked(self, tenant_a, admin_a):
        invite = UserInvite(tenant=tenant_a, email="rev@example.com", invited_by=admin_a)
        invite.save()
        invite.status = UserInvite.STATUS_REVOKED
        invite.save()
        assert invite.is_actionable is False

    def test_is_actionable_false_when_expired(self, tenant_a, admin_a):
        from datetime import timedelta
        invite = UserInvite(
            tenant=tenant_a, email="past@example.com", invited_by=admin_a,
            expires_at=timezone.now() - timedelta(hours=1),
        )
        invite.token = "manual-token-12345678"
        invite.save()
        assert invite.is_actionable is False

    def test_str_shows_email_and_status(self, tenant_a, admin_a):
        invite = UserInvite(tenant=tenant_a, email="info@example.com", invited_by=admin_a)
        invite.save()
        result = str(invite)
        assert "info@example.com" in result
        assert "Pending" in result

    def test_status_choices_contain_all_four(self):
        choices = dict(UserInvite.STATUS_CHOICES)
        for status in [
            UserInvite.STATUS_PENDING,
            UserInvite.STATUS_ACCEPTED,
            UserInvite.STATUS_REVOKED,
            UserInvite.STATUS_EXPIRED,
        ]:
            assert status in choices
