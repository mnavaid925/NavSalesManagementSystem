"""Tests for accounts views: login, user/role/invite CRUD, profile."""
import pytest
from django.urls import reverse
from django.test import Client

from apps.accounts.models import Role, User, UserInvite
from apps.core.models import Tenant


# ============================================================ login / auth
@pytest.mark.django_db
class TestLoginView:
    def test_get_login_page_200(self):
        c = Client()
        resp = c.get(reverse("accounts:login"))
        assert resp.status_code == 200

    def test_post_valid_credentials_redirects(self, admin_a):
        c = Client()
        resp = c.post(reverse("accounts:login"), {
            "username": "admin_a", "password": "testpass123"
        })
        assert resp.status_code in (301, 302)

    def test_post_invalid_credentials_stays_on_page(self, admin_a):
        c = Client()
        resp = c.post(reverse("accounts:login"), {
            "username": "admin_a", "password": "wrongpass"
        })
        assert resp.status_code == 200

    def test_authenticated_user_redirected_away_from_login(self, client_a):
        resp = client_a.get(reverse("accounts:login"))
        assert resp.status_code in (301, 302)

    def test_login_by_email(self, admin_a):
        c = Client()
        resp = c.post(reverse("accounts:login"), {
            "username": "admin_a@testa.com", "password": "testpass123"
        })
        assert resp.status_code in (301, 302)


# ============================================================ anonymous redirect
@pytest.mark.django_db
class TestAnonymousRedirects:
    def _get(self, url):
        return Client().get(url)

    def test_user_list_redirects_anonymous(self):
        resp = self._get(reverse("accounts:user_list"))
        assert resp.status_code in (301, 302)
        assert "login" in resp.url.lower() or "auth" in resp.url.lower()

    def test_role_list_redirects_anonymous(self):
        resp = self._get(reverse("accounts:role_list"))
        assert resp.status_code in (301, 302)

    def test_invite_list_redirects_anonymous(self):
        resp = self._get(reverse("accounts:invite_list"))
        assert resp.status_code in (301, 302)

    def test_profile_redirects_anonymous(self):
        resp = self._get(reverse("accounts:profile"))
        assert resp.status_code in (301, 302)


# ============================================================ tenant admin required
@pytest.mark.django_db
class TestTenantAdminRequired:
    def test_rep_cannot_access_user_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("accounts:user_list"))
        # Should redirect (to dashboard) not 200
        assert resp.status_code in (301, 302)

    def test_rep_cannot_access_role_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("accounts:role_list"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_access_invite_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("accounts:invite_list"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_user(self, rep_client_a):
        resp = rep_client_a.get(reverse("accounts:user_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_role(self, rep_client_a):
        resp = rep_client_a.get(reverse("accounts:role_create"))
        assert resp.status_code in (301, 302)

    def test_admin_can_access_user_list(self, client_a):
        resp = client_a.get(reverse("accounts:user_list"))
        assert resp.status_code == 200

    def test_admin_can_access_role_list(self, client_a):
        resp = client_a.get(reverse("accounts:role_list"))
        assert resp.status_code == 200


# ============================================================ user CRUD
@pytest.mark.django_db
class TestUserCRUD:
    def test_user_list_200(self, client_a, admin_a):
        resp = client_a.get(reverse("accounts:user_list"))
        assert resp.status_code == 200

    def test_user_list_context_has_users(self, client_a, admin_a):
        resp = client_a.get(reverse("accounts:user_list"))
        assert "users" in resp.context

    def test_user_create_get_200(self, client_a):
        resp = client_a.get(reverse("accounts:user_create"))
        assert resp.status_code == 200

    def test_user_create_post_creates_user(self, client_a, tenant_a, role_a):
        before = User.objects.filter(tenant=tenant_a).count()
        resp = client_a.post(reverse("accounts:user_create"), {
            "username": "brandnew",
            "email": "brandnew@test.com",
            "first_name": "Brand",
            "last_name": "New",
            "phone": "",
            "job_title": "",
            "role": role_a.pk,
            "is_tenant_admin": False,
            "is_active": True,
            "password1": "Str0ng!Pass#99",
            "password2": "Str0ng!Pass#99",
        })
        assert User.objects.filter(tenant=tenant_a).count() == before + 1

    def test_user_create_assigns_correct_tenant(self, client_a, tenant_a, role_a):
        client_a.post(reverse("accounts:user_create"), {
            "username": "tenantcheck",
            "email": "tenantcheck@test.com",
            "first_name": "TC",
            "last_name": "",
            "phone": "",
            "job_title": "",
            "role": role_a.pk,
            "is_tenant_admin": False,
            "is_active": True,
            "password1": "Str0ng!Pass#99",
            "password2": "Str0ng!Pass#99",
        })
        u = User.objects.filter(username="tenantcheck").first()
        assert u is not None
        assert u.tenant == tenant_a

    def test_user_detail_200(self, client_a, admin_a):
        resp = client_a.get(reverse("accounts:user_detail", args=[admin_a.pk]))
        assert resp.status_code == 200

    def test_user_detail_uses_obj_context(self, client_a, admin_a):
        resp = client_a.get(reverse("accounts:user_detail", args=[admin_a.pk]))
        assert "obj" in resp.context

    def test_user_edit_get_200(self, client_a, admin_a):
        resp = client_a.get(reverse("accounts:user_edit", args=[admin_a.pk]))
        assert resp.status_code == 200

    def test_user_delete_post_deletes(self, client_a, tenant_a, role_a):
        # Create a separate user to delete (can't delete yourself)
        victim = User.objects.create_user(
            username="todelete", password="p", tenant=tenant_a, role=role_a
        )
        resp = client_a.post(reverse("accounts:user_delete", args=[victim.pk]))
        assert not User.objects.filter(pk=victim.pk).exists()

    def test_user_delete_self_rejected(self, client_a, admin_a):
        """Admin cannot delete themselves."""
        client_a.post(reverse("accounts:user_delete", args=[admin_a.pk]))
        assert User.objects.filter(pk=admin_a.pk).exists()


# ============================================================ multi-tenant isolation for users
@pytest.mark.django_db
class TestUserTenantIsolation:
    def test_tenant_a_cannot_view_tenant_b_user(self, client_a, admin_b):
        resp = client_a.get(reverse("accounts:user_detail", args=[admin_b.pk]))
        assert resp.status_code == 404

    def test_tenant_a_cannot_edit_tenant_b_user(self, client_a, admin_b):
        resp = client_a.get(reverse("accounts:user_edit", args=[admin_b.pk]))
        assert resp.status_code == 404

    def test_tenant_a_cannot_delete_tenant_b_user(self, client_a, admin_b):
        resp = client_a.post(reverse("accounts:user_delete", args=[admin_b.pk]))
        # 404 since the user doesn't belong to tenant A
        assert resp.status_code == 404

    def test_tenant_a_user_list_excludes_tenant_b_users(self, client_a, admin_b):
        resp = client_a.get(reverse("accounts:user_list"))
        user_pks = [u.pk for u in resp.context["users"]]
        assert admin_b.pk not in user_pks


# ============================================================ role CRUD
@pytest.mark.django_db
class TestRoleCRUD:
    def test_role_list_200(self, client_a):
        resp = client_a.get(reverse("accounts:role_list"))
        assert resp.status_code == 200

    def test_role_list_context_has_roles(self, client_a):
        resp = client_a.get(reverse("accounts:role_list"))
        assert "roles" in resp.context

    def test_role_create_get_200(self, client_a):
        resp = client_a.get(reverse("accounts:role_create"))
        assert resp.status_code == 200

    def test_role_create_post_creates_role(self, client_a, tenant_a):
        before = Role.objects.filter(tenant=tenant_a).count()
        resp = client_a.post(reverse("accounts:role_create"), {
            "name": "New Role",
            "level": "rep",
            "description": "Test role",
            "is_active": True,
        })
        assert Role.objects.filter(tenant=tenant_a).count() == before + 1

    def test_role_create_assigns_correct_tenant(self, client_a, tenant_a):
        client_a.post(reverse("accounts:role_create"), {
            "name": "TenantRole",
            "level": "manager",
            "description": "",
            "is_active": True,
        })
        role = Role.objects.filter(name="TenantRole").first()
        assert role is not None
        assert role.tenant == tenant_a

    def test_role_detail_200(self, client_a, role_a):
        resp = client_a.get(reverse("accounts:role_detail", args=[role_a.pk]))
        assert resp.status_code == 200

    def test_role_edit_get_200(self, client_a, role_a):
        resp = client_a.get(reverse("accounts:role_edit", args=[role_a.pk]))
        assert resp.status_code == 200

    def test_role_delete_post_deletes(self, client_a, tenant_a):
        role = Role.objects.create(tenant=tenant_a, name="ToDeleteRole")
        resp = client_a.post(reverse("accounts:role_delete", args=[role.pk]))
        assert not Role.objects.filter(pk=role.pk).exists()

    def test_role_isolation_tenant_a_cannot_view_tenant_b_role(self, client_a, role_b):
        resp = client_a.get(reverse("accounts:role_detail", args=[role_b.pk]))
        assert resp.status_code == 404

    def test_role_isolation_tenant_a_cannot_edit_tenant_b_role(self, client_a, role_b):
        resp = client_a.get(reverse("accounts:role_edit", args=[role_b.pk]))
        assert resp.status_code == 404


# ============================================================ invite CRUD
@pytest.mark.django_db
class TestInviteCRUD:
    def test_invite_list_200(self, client_a):
        resp = client_a.get(reverse("accounts:invite_list"))
        assert resp.status_code == 200

    def test_invite_create_get_200(self, client_a):
        resp = client_a.get(reverse("accounts:invite_create"))
        assert resp.status_code == 200

    def test_invite_create_post_creates_invite(self, client_a, tenant_a, role_a):
        before = UserInvite.objects.filter(tenant=tenant_a).count()
        resp = client_a.post(reverse("accounts:invite_create"), {
            "email": "newinvitee@example.com",
            "role": role_a.pk,
            "message": "",
        })
        assert UserInvite.objects.filter(tenant=tenant_a).count() == before + 1

    def test_invite_create_assigns_correct_tenant(self, client_a, tenant_a, role_a):
        client_a.post(reverse("accounts:invite_create"), {
            "email": "tenantinvite@example.com",
            "role": role_a.pk,
            "message": "",
        })
        invite = UserInvite.objects.filter(email="tenantinvite@example.com").first()
        assert invite is not None
        assert invite.tenant == tenant_a

    def test_invite_revoke(self, client_a, tenant_a, admin_a):
        invite = UserInvite(tenant=tenant_a, email="revoke_me@example.com", invited_by=admin_a)
        invite.save()
        resp = client_a.post(reverse("accounts:invite_revoke", args=[invite.pk]))
        invite.refresh_from_db()
        assert invite.status == UserInvite.STATUS_REVOKED

    def test_invite_isolation_tenant_a_cannot_revoke_tenant_b_invite(
        self, client_a, tenant_b, admin_b
    ):
        invite = UserInvite(tenant=tenant_b, email="b_invite@example.com", invited_by=admin_b)
        invite.save()
        resp = client_a.post(reverse("accounts:invite_revoke", args=[invite.pk]))
        assert resp.status_code == 404


# ============================================================ profile
@pytest.mark.django_db
class TestProfileViews:
    def test_profile_view_200(self, client_a):
        resp = client_a.get(reverse("accounts:profile"))
        assert resp.status_code == 200

    def test_profile_edit_get_200(self, client_a):
        resp = client_a.get(reverse("accounts:profile_edit"))
        assert resp.status_code == 200

    def test_profile_edit_post_updates(self, client_a, admin_a):
        resp = client_a.post(reverse("accounts:profile_edit"), {
            "first_name": "Updated",
            "last_name": "Name",
            "email": "updated@testa.com",
            "phone": "555-1234",
            "job_title": "CEO",
            "avatar_url": "",
        })
        admin_a.refresh_from_db()
        assert admin_a.first_name == "Updated"
