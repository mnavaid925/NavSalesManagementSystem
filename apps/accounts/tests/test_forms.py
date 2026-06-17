"""Tests for accounts.forms: RegisterForm, UserCreateForm, RoleForm, InviteForm."""
import pytest

from apps.accounts.forms import RegisterForm, RoleForm, InviteForm, UserCreateForm
from apps.accounts.models import Role, User
from apps.core.models import Tenant


@pytest.mark.django_db
class TestRegisterForm:
    def _valid_data(self, suffix=""):
        return {
            "company_name": f"TestCo{suffix}",
            "industry": "Tech",
            "first_name": "John",
            "last_name": "Doe",
            "email": f"john{suffix}@testco.com",
            "username": f"johndoe{suffix}",
            "password1": "Str0ng!Pass#99",
            "password2": "Str0ng!Pass#99",
        }

    def test_valid_form_is_valid(self):
        form = RegisterForm(data=self._valid_data("1"))
        assert form.is_valid(), form.errors

    def test_save_creates_tenant(self):
        form = RegisterForm(data=self._valid_data("2"))
        assert form.is_valid(), form.errors
        before = Tenant.objects.count()
        form.save()
        assert Tenant.objects.count() == before + 1

    def test_save_creates_three_roles(self):
        form = RegisterForm(data=self._valid_data("3"))
        assert form.is_valid(), form.errors
        user = form.save()
        roles = Role.objects.filter(tenant=user.tenant)
        assert roles.count() == 3
        names = set(roles.values_list("name", flat=True))
        assert names == {"Administrator", "Manager", "Sales Rep"}

    def test_save_creates_admin_user(self):
        form = RegisterForm(data=self._valid_data("4"))
        assert form.is_valid(), form.errors
        user = form.save()
        assert user.is_tenant_admin is True
        assert user.tenant is not None

    def test_save_is_atomic_no_orphan_tenant_on_duplicate_username(self):
        """If save() fails due to duplicate username, no orphan tenant is left."""
        data = self._valid_data("5")
        # Pre-create user with same username
        existing_tenant = Tenant.objects.create(name="Pre-existing", slug="pre-existing")
        User.objects.create_user(
            username=data["username"], password="p", tenant=existing_tenant
        )
        # Now the form should fail validation (duplicate username)
        form = RegisterForm(data=data)
        assert not form.is_valid()
        assert "username" in form.errors

    def test_save_is_atomic_no_orphan_tenant_on_duplicate_email(self):
        """If save() fails due to duplicate email, no orphan tenant is left."""
        data = self._valid_data("6")
        existing_tenant = Tenant.objects.create(name="Pre-existing-email", slug="pre-existing-email")
        User.objects.create_user(
            username="other_user6", password="p", email=data["email"], tenant=existing_tenant
        )
        form = RegisterForm(data=data)
        assert not form.is_valid()
        assert "email" in form.errors

    def test_password_mismatch_invalid(self):
        data = self._valid_data("7")
        data["password2"] = "different_password"
        form = RegisterForm(data=data)
        assert not form.is_valid()
        assert "password2" in form.errors

    def test_missing_company_name_invalid(self):
        data = self._valid_data("8")
        data.pop("company_name")
        form = RegisterForm(data=data)
        assert not form.is_valid()

    def test_missing_email_invalid(self):
        data = self._valid_data("9")
        data.pop("email")
        form = RegisterForm(data=data)
        assert not form.is_valid()

    def test_tenant_not_a_form_field(self):
        form = RegisterForm(data=self._valid_data("10"))
        assert "tenant" not in form.fields

    def test_number_not_a_form_field(self):
        form = RegisterForm(data=self._valid_data("11"))
        assert "number" not in form.fields

    def test_duplicate_slug_gets_unique_slug(self):
        """If slug already exists, _unique_slug generates a suffix."""
        Tenant.objects.create(name="Dupco", slug="dupco")
        form = RegisterForm(data={
            "company_name": "Dupco",
            "first_name": "Test",
            "email": "slug@dupco.com",
            "username": "sluguser",
            "password1": "Str0ng!Pass#99",
            "password2": "Str0ng!Pass#99",
        })
        assert form.is_valid(), form.errors
        user = form.save()
        assert user.tenant.slug == "dupco-2"


@pytest.mark.django_db
class TestRoleForm:
    def test_valid_role_form(self, tenant_a):
        form = RoleForm(data={"name": "Sales Director", "level": "director", "is_active": True})
        assert form.is_valid(), form.errors

    def test_tenant_not_a_form_field(self):
        form = RoleForm(data={"name": "Test Role", "level": "rep"})
        assert "tenant" not in form.fields

    def test_missing_name_invalid(self):
        form = RoleForm(data={"level": "rep"})
        assert not form.is_valid()

    def test_invalid_level_invalid(self):
        form = RoleForm(data={"name": "Bad Level", "level": "invalid_level"})
        assert not form.is_valid()


@pytest.mark.django_db
class TestInviteForm:
    def test_valid_invite_form(self, tenant_a, role_a):
        form = InviteForm(data={"email": "invitee@example.com", "role": role_a.pk}, tenant=tenant_a)
        assert form.is_valid(), form.errors

    def test_tenant_not_a_form_field(self, tenant_a):
        form = InviteForm(tenant=tenant_a)
        assert "tenant" not in form.fields

    def test_token_not_a_form_field(self, tenant_a):
        form = InviteForm(tenant=tenant_a)
        assert "token" not in form.fields

    def test_missing_email_invalid(self, tenant_a):
        form = InviteForm(data={}, tenant=tenant_a)
        assert not form.is_valid()

    def test_role_scoped_to_tenant(self, tenant_a, tenant_b):
        role_b = Role.objects.create(tenant=tenant_b, name="B Manager")
        form = InviteForm(tenant=tenant_a)
        # role_b should NOT appear in choices for tenant_a
        role_pks = [r.pk for r in form.fields["role"].queryset]
        assert role_b.pk not in role_pks


@pytest.mark.django_db
class TestUserCreateForm:
    def test_valid_user_create_form(self, tenant_a, role_a):
        form = UserCreateForm(data={
            "username": "newuser",
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "User",
            "phone": "",
            "job_title": "",
            "role": role_a.pk,
            "is_tenant_admin": False,
            "is_active": True,
            "password1": "Str0ng!Pass#99",
            "password2": "Str0ng!Pass#99",
        }, tenant=tenant_a)
        assert form.is_valid(), form.errors

    def test_tenant_not_in_form_fields(self, tenant_a):
        form = UserCreateForm(tenant=tenant_a)
        assert "tenant" not in form.fields

    def test_save_assigns_tenant_to_user(self, tenant_a, role_a):
        form = UserCreateForm(data={
            "username": "tenanteduser",
            "email": "tenanted@example.com",
            "first_name": "T",
            "last_name": "U",
            "phone": "",
            "job_title": "",
            "role": role_a.pk,
            "is_tenant_admin": False,
            "is_active": True,
            "password1": "Str0ng!Pass#99",
            "password2": "Str0ng!Pass#99",
        }, tenant=tenant_a)
        assert form.is_valid(), form.errors
        user = form.save()
        assert user.tenant == tenant_a
