import secrets
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Role(models.Model):
    """A tenant-scoped role (Module 19 — User Roles & Profiles)."""

    LEVEL_REP = "rep"
    LEVEL_MANAGER = "manager"
    LEVEL_DIRECTOR = "director"
    LEVEL_EXECUTIVE = "executive"
    LEVEL_ADMIN = "admin"
    LEVEL_CHOICES = [
        (LEVEL_REP, "Sales Rep"),
        (LEVEL_MANAGER, "Manager"),
        (LEVEL_DIRECTOR, "Director"),
        (LEVEL_EXECUTIVE, "Executive"),
        (LEVEL_ADMIN, "Administrator"),
    ]

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, related_name="roles")
    name = models.CharField(max_length=80)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default=LEVEL_REP)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("tenant", "name")

    def __str__(self):
        return self.name


class User(AbstractUser):
    """Custom user: every non-superuser belongs to exactly one tenant."""

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE,
        related_name="users", null=True, blank=True,
    )
    role = models.ForeignKey(
        "accounts.Role", on_delete=models.SET_NULL,
        related_name="users", null=True, blank=True,
    )
    phone = models.CharField(max_length=40, blank=True)
    job_title = models.CharField(max_length=120, blank=True)
    avatar_url = models.URLField(blank=True)
    is_tenant_admin = models.BooleanField(
        default=False,
        help_text="Can manage users, roles and invites within the tenant.",
    )

    class Meta:
        ordering = ["first_name", "last_name", "username"]

    @property
    def display_name(self):
        full = self.get_full_name().strip()
        return full or self.username

    @property
    def initials(self):
        first = (self.first_name or self.username or "?")[:1]
        last = (self.last_name or "")[:1]
        return (first + last).upper()


class UserInvite(models.Model):
    """A pending invitation to join a tenant (Module 5 — User management / invite)."""

    STATUS_PENDING = "pending"
    STATUS_ACCEPTED = "accepted"
    STATUS_REVOKED = "revoked"
    STATUS_EXPIRED = "expired"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_REVOKED, "Revoked"),
        (STATUS_EXPIRED, "Expired"),
    ]

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, related_name="invites")
    email = models.EmailField()
    role = models.ForeignKey(
        "accounts.Role", on_delete=models.SET_NULL,
        related_name="invites", null=True, blank=True,
    )
    token = models.CharField(max_length=64, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    message = models.TextField(blank=True)
    invited_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL,
        related_name="sent_invites", null=True, blank=True,
    )
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=14)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_actionable(self):
        return self.status == self.STATUS_PENDING and not self.is_expired
