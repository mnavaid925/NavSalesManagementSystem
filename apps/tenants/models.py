import hashlib
import secrets

from django.db import models
from django.utils import timezone


class OnboardingStep(models.Model):
    """Tenant Onboarding — a self-service setup checklist item."""

    STATUS_PENDING = "pending"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_DONE = "done"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_IN_PROGRESS, "In progress"),
        (STATUS_DONE, "Done"),
    ]

    DEFAULT_STEPS = [
        ("Complete company profile", "Add your company name, industry and contact details."),
        ("Configure branding", "Upload your logo and set your brand colours."),
        ("Invite your team", "Send invitations to your sales reps and managers."),
        ("Choose a subscription plan", "Pick the plan that fits your team size."),
        ("Set up security keys", "Generate API/encryption keys for integrations."),
        ("Review tenant health", "Confirm resource usage and alert thresholds."),
    ]

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, related_name="onboarding_steps")
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    completed_at = models.DateTimeField(null=True, blank=True)  # system-set (off forms, L22)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.status == self.STATUS_DONE and self.completed_at is None:
            self.completed_at = timezone.now()
        if self.status != self.STATUS_DONE:
            self.completed_at = None
        super().save(*args, **kwargs)

    @classmethod
    def seed_defaults(cls, tenant):
        """Idempotently create the standard onboarding checklist for a tenant."""
        for i, (title, desc) in enumerate(cls.DEFAULT_STEPS, start=1):
            cls.objects.get_or_create(
                tenant=tenant, title=title,
                defaults={"description": desc, "order": i},
            )


class Subscription(models.Model):
    """Subscription & Billing — a tenant's plan and lifecycle state."""

    PLAN_STARTER = "starter"
    PLAN_PRO = "pro"
    PLAN_ENTERPRISE = "enterprise"
    PLAN_CHOICES = [
        (PLAN_STARTER, "Starter"),
        (PLAN_PRO, "Professional"),
        (PLAN_ENTERPRISE, "Enterprise"),
    ]

    STATUS_TRIALING = "trialing"
    STATUS_ACTIVE = "active"
    STATUS_PAST_DUE = "past_due"
    STATUS_CANCELED = "canceled"
    STATUS_CHOICES = [
        (STATUS_TRIALING, "Trialing"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_PAST_DUE, "Past due"),
        (STATUS_CANCELED, "Canceled"),
    ]

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default=PLAN_STARTER)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_TRIALING)
    seats = models.PositiveIntegerField(default=5)
    monthly_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    started_on = models.DateField(default=timezone.localdate)
    renews_on = models.DateField(null=True, blank=True)
    is_auto_renew = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-started_on", "-id"]

    def __str__(self):
        return f"{self.get_plan_display()} — {self.get_status_display()}"


class Invoice(models.Model):
    """Subscription & Billing — a billing document (auto-numbered INV-00001)."""

    STATUS_DRAFT = "draft"
    STATUS_SENT = "sent"
    STATUS_PAID = "paid"
    STATUS_OVERDUE = "overdue"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_SENT, "Sent"),
        (STATUS_PAID, "Paid"),
        (STATUS_OVERDUE, "Overdue"),
    ]

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, related_name="invoices")
    subscription = models.ForeignKey(
        "tenants.Subscription", on_delete=models.SET_NULL,
        related_name="invoices", null=True, blank=True,
    )
    number = models.CharField(max_length=20, blank=True)
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    issued_on = models.DateField(default=timezone.localdate)
    due_on = models.DateField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)  # system-set (off forms, L22)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-issued_on", "-id"]
        unique_together = ("tenant", "number")

    def __str__(self):
        return self.number or f"Invoice #{self.pk}"

    def save(self, *args, **kwargs):
        if not self.number and self.tenant_id:
            # Per-tenant sequence with an existence guard (idempotent for seeds).
            last = (Invoice.objects.filter(tenant_id=self.tenant_id, number__startswith="INV-")
                    .order_by("-number").first())
            seq = 1
            if last and last.number:
                try:
                    seq = int(last.number.split("-")[1]) + 1
                except (IndexError, ValueError):
                    seq = Invoice.objects.filter(tenant_id=self.tenant_id).count() + 1
            self.number = f"INV-{seq:05d}"
        if self.status == self.STATUS_PAID and self.paid_at is None:
            self.paid_at = timezone.now()
        super().save(*args, **kwargs)


class EncryptionKey(models.Model):
    """Tenant Isolation & Security — an API/encryption key.

    # WARNING: the plaintext secret is NEVER stored. We keep only a short visible
    # prefix and a SHA-256 hash, and the form excludes both (set in the view). The
    # plaintext is shown once at creation time and cannot be retrieved later (L20).
    """

    ALGO_AES256 = "aes-256"
    ALGO_RSA2048 = "rsa-2048"
    ALGO_HMAC = "hmac-sha256"
    ALGO_CHOICES = [
        (ALGO_AES256, "AES-256"),
        (ALGO_RSA2048, "RSA-2048"),
        (ALGO_HMAC, "HMAC-SHA256"),
    ]

    STATUS_ACTIVE = "active"
    STATUS_ROTATED = "rotated"
    STATUS_REVOKED = "revoked"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_ROTATED, "Rotated"),
        (STATUS_REVOKED, "Revoked"),
    ]

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, related_name="encryption_keys")
    label = models.CharField(max_length=120)
    key_prefix = models.CharField(max_length=16, blank=True, editable=False)
    hashed_key = models.CharField(max_length=128, blank=True, editable=False)
    algorithm = models.CharField(max_length=20, choices=ALGO_CHOICES, default=ALGO_AES256)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    last_rotated_at = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.label} ({self.masked})"

    @property
    def masked(self):
        return f"{self.key_prefix}{'•' * 8}" if self.key_prefix else "••••••••"

    @staticmethod
    def generate_secret():
        """Return (plaintext, prefix, sha256_hash). Store only prefix + hash."""
        plaintext = "sk_" + secrets.token_urlsafe(32)
        prefix = plaintext[:10]
        hashed = hashlib.sha256(plaintext.encode()).hexdigest()
        return plaintext, prefix, hashed


class BrandingSetting(models.Model):
    """Custom Branding — white-label profile (logo, colours, email templates)."""

    THEME_LIGHT = "light"
    THEME_DARK = "dark"
    THEME_AUTO = "auto"
    THEME_CHOICES = [
        (THEME_LIGHT, "Light"),
        (THEME_DARK, "Dark"),
        (THEME_AUTO, "Auto"),
    ]

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, related_name="branding_profiles")
    name = models.CharField(max_length=120, default="Default")
    is_default = models.BooleanField(default=False)
    logo_url = models.URLField(blank=True)
    primary_color = models.CharField(max_length=9, default="#2563eb")
    accent_color = models.CharField(max_length=9, default="#0ea5e9")
    login_message = models.CharField(max_length=255, blank=True)
    email_from_name = models.CharField(max_length=120, blank=True)
    email_signature = models.TextField(blank=True)
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default=THEME_LIGHT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_default", "name"]

    def __str__(self):
        return self.name


class HealthMetric(models.Model):
    """Tenant Health Monitoring — a resource/usage/uptime measurement."""

    CATEGORY_RESOURCE = "resource"
    CATEGORY_USAGE = "usage"
    CATEGORY_UPTIME = "uptime"
    CATEGORY_PERFORMANCE = "performance"
    CATEGORY_CHOICES = [
        (CATEGORY_RESOURCE, "Resource"),
        (CATEGORY_USAGE, "Usage"),
        (CATEGORY_UPTIME, "Uptime"),
        (CATEGORY_PERFORMANCE, "Performance"),
    ]

    STATUS_OK = "ok"
    STATUS_WARNING = "warning"
    STATUS_CRITICAL = "critical"
    STATUS_CHOICES = [
        (STATUS_OK, "OK"),
        (STATUS_WARNING, "Warning"),
        (STATUS_CRITICAL, "Critical"),
    ]

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, related_name="health_metrics")
    metric_name = models.CharField(max_length=120)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_RESOURCE)
    value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit = models.CharField(max_length=20, blank=True)
    threshold = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OK)
    recorded_at = models.DateTimeField(default=timezone.now)  # system observation time (off forms)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-recorded_at", "-id"]

    def __str__(self):
        return f"{self.metric_name}: {self.value}{self.unit}"
