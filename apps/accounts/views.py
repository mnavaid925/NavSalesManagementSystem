from datetime import timedelta
from functools import wraps

from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from apps.core.utils import log_action

from .forms import (
    InviteAcceptForm, InviteForm, LoginForm, ProfileForm, RegisterForm,
    RoleForm, UserCreateForm, UserEditForm,
)
from .models import Role, User, UserInvite

BACKEND = "apps.accounts.backends.EmailOrUsernameModelBackend"


def tenant_admin_required(view):
    """Allow only tenant admins (or superusers) to manage users/roles/invites."""

    @wraps(view)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not (request.user.is_superuser or getattr(request.user, "is_tenant_admin", False)):
            messages.error(request, "You don't have permission to manage your workspace.")
            return redirect("dashboard:index")
        return view(request, *args, **kwargs)

    return _wrapped


# --------------------------------------------------------------------------- auth
def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:index")
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        request.tenant = getattr(user, "tenant", None)
        log_action(request, "login", detail=f"{user.username} signed in")
        nxt = request.POST.get("next") or request.GET.get("next")
        if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
            return redirect(nxt)
        return redirect("dashboard:index")
    return render(request, "auth/login.html", {"form": form, "next": request.GET.get("next", "")})


@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "You have been signed out.")
    return redirect("accounts:login")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:index")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        from apps.tenants.models import OnboardingStep  # lazy: avoid app-load cycle
        OnboardingStep.seed_defaults(user.tenant)
        login(request, user, backend=BACKEND)
        request.tenant = user.tenant
        log_action(request, "create", instance=user.tenant,
                   detail="Workspace created via self-service registration")
        messages.success(request, f"Welcome aboard, {user.display_name}! Your workspace is ready.")
        return redirect("dashboard:index")
    return render(request, "auth/register.html", {"form": form})


def invite_accept_view(request, token):
    invite = get_object_or_404(UserInvite, token=token)
    if not invite.is_actionable:
        return render(request, "auth/invite_invalid.html", {"invite": invite})
    form = InviteAcceptForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        user = User(
            username=data["username"],
            email=invite.email,
            first_name=data["first_name"],
            last_name=data.get("last_name", ""),
            tenant=invite.tenant,
            role=invite.role,
        )
        user.set_password(data["password1"])
        user.save()
        invite.status = UserInvite.STATUS_ACCEPTED
        invite.accepted_at = timezone.now()
        invite.save(update_fields=["status", "accepted_at", "updated_at"])
        login(request, user, backend=BACKEND)
        request.tenant = user.tenant
        log_action(request, "create", instance=user, detail="Joined via invitation")
        messages.success(request, f"Welcome to {invite.tenant.name}!")
        return redirect("dashboard:index")
    return render(request, "auth/invite_accept.html", {"form": form, "invite": invite})


# ----------------------------------------------------------------------- users
@tenant_admin_required
def user_list(request):
    qs = User.objects.filter(tenant=request.tenant).select_related("role")

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(username__icontains=q) | Q(email__icontains=q)
            | Q(first_name__icontains=q) | Q(last_name__icontains=q)
        )

    role = request.GET.get("role", "")
    if role.isdigit():
        qs = qs.filter(role_id=int(role))

    status = request.GET.get("status", "")
    if status == "active":
        qs = qs.filter(is_active=True)
    elif status == "inactive":
        qs = qs.filter(is_active=False)

    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        "page_title": "Users",
        "page_obj": page_obj,
        "users": page_obj.object_list,
        "roles": Role.objects.filter(tenant=request.tenant),
        "total": paginator.count,
    }
    return render(request, "accounts/user_list.html", context)


@tenant_admin_required
def user_create(request):
    form = UserCreateForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        log_action(request, "create", instance=user)
        messages.success(request, f"User “{user.display_name}” created.")
        return redirect("accounts:user_list")
    return render(request, "accounts/user_form.html",
                  {"form": form, "page_title": "Add User", "mode": "create"})


@tenant_admin_required
def user_detail(request, pk):
    user = get_object_or_404(User.objects.select_related("role", "tenant"),
                             pk=pk, tenant=request.tenant)
    return render(request, "accounts/user_detail.html",
                  {"obj": user, "page_title": user.display_name})


@tenant_admin_required
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk, tenant=request.tenant)
    form = UserEditForm(request.POST or None, instance=user, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=user)
        messages.success(request, "User updated.")
        return redirect("accounts:user_detail", pk=user.pk)
    return render(request, "accounts/user_form.html",
                  {"form": form, "obj": user, "page_title": f"Edit {user.display_name}", "mode": "edit"})


@tenant_admin_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        if user.pk == request.user.pk:
            messages.error(request, "You cannot delete your own account.")
            return redirect("accounts:user_detail", pk=user.pk)
        label = user.display_name
        log_action(request, "delete", instance=user)
        user.delete()
        messages.success(request, f"User “{label}” deleted.")
    return redirect("accounts:user_list")


# ----------------------------------------------------------------------- invites
@tenant_admin_required
def invite_list(request):
    qs = UserInvite.objects.filter(tenant=request.tenant).select_related("role", "invited_by")
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(email__icontains=q)
    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "accounts/invite_list.html", {
        "page_title": "Invitations",
        "page_obj": page_obj,
        "invites": page_obj.object_list,
        "status_choices": UserInvite.STATUS_CHOICES,
        "total": paginator.count,
    })


def _send_invite_email(request, invite):
    accept_url = request.build_absolute_uri(reverse("accounts:invite_accept", args=[invite.token]))
    try:
        send_mail(
            subject=f"You're invited to join {invite.tenant.name}",
            message=(f"{request.user.display_name} invited you to join {invite.tenant.name}.\n\n"
                     f"Accept your invitation:\n{accept_url}\n\n{invite.message}"),
            from_email=None,
            recipient_list=[invite.email],
            fail_silently=True,
        )
    except Exception:
        pass
    return accept_url


@tenant_admin_required
def invite_create(request):
    form = InviteForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        invite = form.save(commit=False)
        invite.tenant = request.tenant
        invite.invited_by = request.user
        invite.save()
        _send_invite_email(request, invite)
        log_action(request, "create", instance=invite, detail=f"Invited {invite.email}")
        messages.success(request, f"Invitation sent to {invite.email}.")
        return redirect("accounts:invite_list")
    return render(request, "accounts/invite_form.html",
                  {"form": form, "page_title": "Invite User"})


@tenant_admin_required
def invite_resend(request, pk):
    invite = get_object_or_404(UserInvite, pk=pk, tenant=request.tenant)
    if request.method == "POST" and invite.status == UserInvite.STATUS_PENDING:
        invite.expires_at = timezone.now() + timedelta(days=14)
        invite.save(update_fields=["expires_at", "updated_at"])
        _send_invite_email(request, invite)
        messages.success(request, f"Invitation re-sent to {invite.email}.")
    return redirect("accounts:invite_list")


@tenant_admin_required
def invite_revoke(request, pk):
    invite = get_object_or_404(UserInvite, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        invite.status = UserInvite.STATUS_REVOKED
        invite.save(update_fields=["status", "updated_at"])
        log_action(request, "update", instance=invite, detail="Invitation revoked")
        messages.success(request, "Invitation revoked.")
    return redirect("accounts:invite_list")


# ------------------------------------------------------------------------- roles
@tenant_admin_required
def role_list(request):
    qs = Role.objects.filter(tenant=request.tenant).annotate(user_count=Count("users"))
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(name__icontains=q)
    level = request.GET.get("level", "")
    if level:
        qs = qs.filter(level=level)
    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "accounts/role_list.html", {
        "page_title": "Roles",
        "page_obj": page_obj,
        "roles": page_obj.object_list,
        "level_choices": Role.LEVEL_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def role_create(request):
    form = RoleForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        role = form.save(commit=False)
        role.tenant = request.tenant
        role.save()
        log_action(request, "create", instance=role)
        messages.success(request, f"Role “{role.name}” created.")
        return redirect("accounts:role_list")
    return render(request, "accounts/role_form.html",
                  {"form": form, "page_title": "Add Role", "mode": "create"})


@tenant_admin_required
def role_detail(request, pk):
    role = get_object_or_404(Role, pk=pk, tenant=request.tenant)
    members = role.users.all()[:50]
    member_count = role.users.count()
    return render(request, "accounts/role_detail.html",
                  {"obj": role, "members": members, "member_count": member_count,
                   "page_title": role.name})


@tenant_admin_required
def role_edit(request, pk):
    role = get_object_or_404(Role, pk=pk, tenant=request.tenant)
    form = RoleForm(request.POST or None, instance=role)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=role)
        messages.success(request, "Role updated.")
        return redirect("accounts:role_detail", pk=role.pk)
    return render(request, "accounts/role_form.html",
                  {"form": form, "obj": role, "page_title": f"Edit {role.name}", "mode": "edit"})


@tenant_admin_required
def role_delete(request, pk):
    role = get_object_or_404(Role, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = role.name
        log_action(request, "delete", instance=role)
        role.delete()
        messages.success(request, f"Role “{label}” deleted.")
    return redirect("accounts:role_list")


# ----------------------------------------------------------------------- profile
@login_required
def profile_view(request):
    return render(request, "accounts/profile.html",
                  {"obj": request.user, "page_title": "My Profile"})


@login_required
def profile_edit(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated.")
        return redirect("accounts:profile")
    return render(request, "accounts/profile_form.html",
                  {"form": form, "page_title": "Edit Profile"})


@login_required
def change_password(request):
    form = PasswordChangeForm(user=request.user, data=request.POST or None)
    for field in form.fields.values():
        existing = field.widget.attrs.get("class", "")
        field.widget.attrs["class"] = f"{existing} form-input".strip()
    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, "Password changed.")
        return redirect("accounts:profile")
    return render(request, "accounts/change_password.html",
                  {"form": form, "page_title": "Change Password"})
