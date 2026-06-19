import secrets

from django.db import models, transaction
from django.utils import timezone


class Connector(models.Model):
    """ERP / integration connector — the parent integration endpoint."""

    CATEGORY_ERP = "erp"
    CATEGORY_MARKETING = "marketing"
    CATEGORY_COMMUNICATION = "communication"
    CATEGORY_BI = "bi"
    CATEGORY_ESIGNATURE = "esignature"
    CATEGORY_CRM = "crm"
    CATEGORY_STORAGE = "storage"
    CATEGORY_CHOICES = [
        (CATEGORY_ERP, "ERP"),
        (CATEGORY_MARKETING, "Marketing automation"),
        (CATEGORY_COMMUNICATION, "Communication"),
        (CATEGORY_BI, "Business intelligence"),
        (CATEGORY_ESIGNATURE, "E-signature"),
        (CATEGORY_CRM, "CRM"),
        (CATEGORY_STORAGE, "Storage"),
    ]

    STATUS_CONNECTED = "connected"
    STATUS_DISCONNECTED = "disconnected"
    STATUS_ERROR = "error"
    STATUS_CONFIGURING = "configuring"
    STATUS_CHOICES = [
        (STATUS_CONNECTED, "Connected"),
        (STATUS_DISCONNECTED, "Disconnected"),
        (STATUS_ERROR, "Error"),
        (STATUS_CONFIGURING, "Configuring"),
    ]

    AUTH_OAUTH = "oauth"
    AUTH_API_KEY = "api_key"
    AUTH_BASIC = "basic"
    AUTH_TOKEN = "token"
    AUTH_CHOICES = [
        (AUTH_OAUTH, "OAuth 2.0"),
        (AUTH_API_KEY, "API key"),
        (AUTH_BASIC, "Basic auth"),
        (AUTH_TOKEN, "Bearer token"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="integrations_connectors")
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_ERP)
    provider = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DISCONNECTED)
    auth_type = models.CharField(max_length=20, choices=AUTH_CHOICES, default=AUTH_OAUTH)
    last_sync = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="conn_tenant_status_idx"),
            models.Index(fields=["tenant", "category"], name="conn_tenant_category_idx"),
        ]

    def __str__(self):
        return self.name


class SyncJob(models.Model):
    """Marketing/data sync job between the platform and a connector (auto SYNC-)."""

    DIRECTION_INBOUND = "inbound"
    DIRECTION_OUTBOUND = "outbound"
    DIRECTION_BIDIRECTIONAL = "bidirectional"
    DIRECTION_CHOICES = [
        (DIRECTION_INBOUND, "Inbound"),
        (DIRECTION_OUTBOUND, "Outbound"),
        (DIRECTION_BIDIRECTIONAL, "Bidirectional"),
    ]

    STATUS_SCHEDULED = "scheduled"
    STATUS_RUNNING = "running"
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"
    STATUS_PAUSED = "paused"
    STATUS_CHOICES = [
        (STATUS_SCHEDULED, "Scheduled"),
        (STATUS_RUNNING, "Running"),
        (STATUS_SUCCESS, "Success"),
        (STATUS_FAILED, "Failed"),
        (STATUS_PAUSED, "Paused"),
    ]

    SCHEDULE_MANUAL = "manual"
    SCHEDULE_HOURLY = "hourly"
    SCHEDULE_DAILY = "daily"
    SCHEDULE_WEEKLY = "weekly"
    SCHEDULE_REALTIME = "realtime"
    SCHEDULE_CHOICES = [
        (SCHEDULE_MANUAL, "Manual"),
        (SCHEDULE_HOURLY, "Hourly"),
        (SCHEDULE_DAILY, "Daily"),
        (SCHEDULE_WEEKLY, "Weekly"),
        (SCHEDULE_REALTIME, "Real-time"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="integrations_syncjobs")
    connector = models.ForeignKey(
        "integrations.Connector", on_delete=models.SET_NULL,
        related_name="sync_jobs", null=True, blank=True)
    number = models.CharField(max_length=20, blank=True)
    name = models.CharField(max_length=150)
    direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES, default=DIRECTION_INBOUND)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SCHEDULED)
    schedule = models.CharField(max_length=20, choices=SCHEDULE_CHOICES, default=SCHEDULE_DAILY)
    records_synced = models.IntegerField(default=0)
    last_run = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        unique_together = ("tenant", "number")
        indexes = [
            models.Index(fields=["tenant", "status"], name="sjob_tenant_status_idx"),
            models.Index(fields=["tenant", "connector"], name="sjob_tenant_connector_idx"),
        ]

    def __str__(self):
        return self.number or f"SyncJob #{self.pk}"

    def save(self, *args, **kwargs):
        if not self.number and self.tenant_id:
            # Per-tenant sequence with a row lock to avoid duplicate numbers under
            # concurrent creation (idempotent for seeds).
            with transaction.atomic():
                last = (SyncJob.objects.select_for_update()
                        .filter(tenant_id=self.tenant_id, number__startswith="SYNC-")
                        .order_by("-number").first())
                seq = 1
                if last and last.number:
                    try:
                        seq = int(last.number.split("-")[1]) + 1
                    except (IndexError, ValueError):
                        seq = (SyncJob.objects
                               .filter(tenant_id=self.tenant_id, number__startswith="SYNC-")
                               .count() + 1)
                self.number = f"SYNC-{seq:05d}"
                super().save(*args, **kwargs)
                return
        super().save(*args, **kwargs)


class SyncLog(models.Model):
    """A log line emitted by a sync job run."""

    LEVEL_INFO = "info"
    LEVEL_WARNING = "warning"
    LEVEL_ERROR = "error"
    LEVEL_SUCCESS = "success"
    LEVEL_CHOICES = [
        (LEVEL_INFO, "Info"),
        (LEVEL_WARNING, "Warning"),
        (LEVEL_ERROR, "Error"),
        (LEVEL_SUCCESS, "Success"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="integrations_synclogs")
    job = models.ForeignKey(
        "integrations.SyncJob", on_delete=models.SET_NULL,
        related_name="logs", null=True, blank=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default=LEVEL_INFO)
    message = models.TextField(blank=True)
    records_affected = models.IntegerField(default=0)
    duration_ms = models.IntegerField(default=0)
    occurred_at = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-occurred_at", "-id"]
        indexes = [
            models.Index(fields=["tenant", "level"], name="slog_tenant_level_idx"),
            models.Index(fields=["tenant", "job"], name="slog_tenant_job_idx"),
        ]

    def __str__(self):
        return f"{self.level} log #{self.pk}"

    def save(self, *args, **kwargs):
        if self.occurred_at is None:
            self.occurred_at = timezone.now()
        super().save(*args, **kwargs)


class Webhook(models.Model):
    """Outbound webhook subscription with a signing secret."""

    EVENT_RECORD_CREATED = "record.created"
    EVENT_RECORD_UPDATED = "record.updated"
    EVENT_RECORD_DELETED = "record.deleted"
    EVENT_SYNC_COMPLETED = "sync.completed"
    EVENT_ERROR = "error"
    EVENT_CHOICES = [
        (EVENT_RECORD_CREATED, "Record created"),
        (EVENT_RECORD_UPDATED, "Record updated"),
        (EVENT_RECORD_DELETED, "Record deleted"),
        (EVENT_SYNC_COMPLETED, "Sync completed"),
        (EVENT_ERROR, "Error"),
    ]

    METHOD_POST = "post"
    METHOD_PUT = "put"
    METHOD_PATCH = "patch"
    METHOD_CHOICES = [
        (METHOD_POST, "POST"),
        (METHOD_PUT, "PUT"),
        (METHOD_PATCH, "PATCH"),
    ]

    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_INACTIVE, "Inactive"),
        (STATUS_FAILED, "Failed"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="integrations_webhooks")
    name = models.CharField(max_length=150)
    target_url = models.URLField(blank=True)
    event_type = models.CharField(max_length=30, choices=EVENT_CHOICES, default=EVENT_RECORD_CREATED)
    http_method = models.CharField(max_length=10, choices=METHOD_CHOICES, default=METHOD_POST)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    # WARNING: signing secret stored in plaintext for demo purposes only. In
    # production, store a hash (never the raw value), expose it once on creation,
    # and rotate via a dedicated write-only flow. Excluded from the ModelForm.
    secret = models.CharField(max_length=128, blank=True)
    failure_count = models.IntegerField(default=0)
    last_triggered = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="whk_tenant_status_idx"),
            models.Index(fields=["tenant", "event_type"], name="whk_tenant_event_idx"),
        ]

    def __str__(self):
        return self.name

    @property
    def masked(self):
        """Never reveal the full secret in the UI."""
        if not self.secret:
            return ""
        return f"{'•' * 8}{self.secret[-4:]}" if len(self.secret) > 4 else "•" * len(self.secret)


class ApiKey(models.Model):
    """A generated API key for programmatic access."""

    ENVIRONMENT_PRODUCTION = "production"
    ENVIRONMENT_SANDBOX = "sandbox"
    ENVIRONMENT_DEVELOPMENT = "development"
    ENVIRONMENT_CHOICES = [
        (ENVIRONMENT_PRODUCTION, "Production"),
        (ENVIRONMENT_SANDBOX, "Sandbox"),
        (ENVIRONMENT_DEVELOPMENT, "Development"),
    ]

    STATUS_ACTIVE = "active"
    STATUS_REVOKED = "revoked"
    STATUS_EXPIRED = "expired"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_REVOKED, "Revoked"),
        (STATUS_EXPIRED, "Expired"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="integrations_apikeys")
    name = models.CharField(max_length=150)
    # WARNING: generated secret stored in plaintext for demo purposes only. In
    # production, store only a hash of the key, surface the raw value once at
    # creation, and rotate via a dedicated write-only flow. Excluded from the
    # ModelForm — generated in save() and never editable from the UI.
    key = models.CharField(max_length=64, blank=True)
    key_prefix = models.CharField(max_length=12, blank=True)  # system-set in save()
    environment = models.CharField(max_length=20, choices=ENVIRONMENT_CHOICES, default=ENVIRONMENT_SANDBOX)
    scopes = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    last_used = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    expires_on = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="akey_tenant_status_idx"),
            models.Index(fields=["tenant", "environment"], name="akey_tenant_env_idx"),
        ]

    def __str__(self):
        return self.name

    @property
    def masked(self):
        """Never reveal the full key in the UI — only the prefix + a tail mask."""
        if not self.key:
            return ""
        return f"{self.key_prefix}{'•' * 8}"

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_urlsafe(32)
        if not self.key_prefix:
            self.key_prefix = self.key[:8]
        super().save(*args, **kwargs)
