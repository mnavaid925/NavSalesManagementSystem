from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordResetForm, SetPasswordForm,
)
from django.db import transaction
from django.utils.text import slugify

from apps.core.forms import StyledFormMixin
from apps.core.models import Tenant

from .models import Role, User, UserInvite


class LoginForm(StyledFormMixin, AuthenticationForm):
    """Username-or-email login (see EmailOrUsernameModelBackend)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Email or username"
        self.fields["username"].widget.attrs.update({"autofocus": True, "placeholder": "you@company.com"})
        self.fields["password"].widget.attrs.update({"placeholder": "••••••••"})


class RegisterForm(StyledFormMixin, forms.Form):
    """Self-service tenant onboarding: creates a Tenant + its first admin user."""

    company_name = forms.CharField(max_length=150, label="Company / Workspace name")
    industry = forms.CharField(max_length=120, required=False)
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField()
    username = forms.CharField(max_length=150)
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("That username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with that email already exists.")
        return email

    def _unique_slug(self, name):
        base = slugify(name) or "workspace"
        slug = base
        i = 2
        while Tenant.objects.filter(slug=slug).exists():
            slug = f"{base}-{i}"
            i += 1
        return slug

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get("password1"), cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Passwords do not match.")
        if p1:
            password_validation.validate_password(p1)
        return cleaned

    @transaction.atomic
    def save(self):
        """Create the tenant, its default roles and the first admin user.

        Atomic so a failure (e.g. a slug/username race) never leaves an orphaned
        tenant with no admin behind.
        """
        data = self.cleaned_data
        tenant = Tenant.objects.create(
            name=data["company_name"],
            slug=self._unique_slug(data["company_name"]),
            industry=data.get("industry", ""),
            status=Tenant.STATUS_TRIAL,
        )
        admin_role = Role.objects.create(
            tenant=tenant, name="Administrator", level=Role.LEVEL_ADMIN,
            description="Full access to this workspace.",
        )
        Role.objects.create(tenant=tenant, name="Manager", level=Role.LEVEL_MANAGER)
        Role.objects.create(tenant=tenant, name="Sales Rep", level=Role.LEVEL_REP)
        user = User(
            username=data["username"],
            email=data["email"],
            first_name=data["first_name"],
            last_name=data.get("last_name", ""),
            tenant=tenant,
            role=admin_role,
            is_tenant_admin=True,
        )
        user.set_password(data["password1"])
        user.save()
        return user


class _TenantRoleMixin:
    """Limit any `role` field to the active tenant's roles."""

    def _scope_role(self, tenant):
        if "role" in self.fields:
            self.fields["role"].queryset = Role.objects.filter(tenant=tenant, is_active=True)


class UserCreateForm(StyledFormMixin, _TenantRoleMixin, forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            "username", "email", "first_name", "last_name",
            "phone", "job_title", "role", "is_tenant_admin", "is_active",
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        self.tenant = tenant
        super().__init__(*args, **kwargs)
        self._scope_role(tenant)

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get("password1"), cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Passwords do not match.")
        if p1:
            password_validation.validate_password(p1)
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.tenant = self.tenant
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserEditForm(StyledFormMixin, _TenantRoleMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "username", "email", "first_name", "last_name",
            "phone", "job_title", "role", "is_tenant_admin", "is_active",
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._scope_role(tenant)


class ProfileForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "job_title", "avatar_url"]


class RoleForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Role
        fields = ["name", "level", "description", "is_active"]


class InviteForm(StyledFormMixin, _TenantRoleMixin, forms.ModelForm):
    class Meta:
        model = UserInvite
        fields = ["email", "role", "message"]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._scope_role(tenant)


class StyledPasswordResetForm(StyledFormMixin, PasswordResetForm):
    """Django's reset-request form with theme.css styling."""


class StyledSetPasswordForm(StyledFormMixin, SetPasswordForm):
    """Django's set-new-password form (reset confirm) with theme.css styling."""


class InviteAcceptForm(StyledFormMixin, forms.Form):
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150, required=False)
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("That username is already taken.")
        return username

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get("password1"), cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Passwords do not match.")
        if p1:
            password_validation.validate_password(p1)
        return cleaned
