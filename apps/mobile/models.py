from django.db import models, transaction
from django.utils import timezone


class MobileDevice(models.Model):
    """Mobile CRM Access — a registered mobile device a rep uses for CRM."""

    PLATFORM_IOS = "ios"
    PLATFORM_ANDROID = "android"
    PLATFORM_WEB = "web"
    PLATFORM_CHOICES = [
        (PLATFORM_IOS, "iOS"),
        (PLATFORM_ANDROID, "Android"),
        (PLATFORM_WEB, "Web"),
    ]

    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_LOST = "lost"
    STATUS_WIPED = "wiped"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_INACTIVE, "Inactive"),
        (STATUS_LOST, "Lost"),
        (STATUS_WIPED, "Wiped"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="mobile_mobiledevices")
    device_name = models.CharField(max_length=120)
    user_name = models.CharField(max_length=120)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default=PLATFORM_IOS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    app_version = models.CharField(max_length=20, blank=True)
    push_enabled = models.BooleanField(default=True)
    last_sync = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["device_name", "-id"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="mdev_tenant_status_idx"),
            models.Index(fields=["tenant", "platform"], name="mdev_tenant_platform_idx"),
        ]

    def __str__(self):
        return self.device_name


class FieldVisit(models.Model):
    """Field Sales Tools — a scheduled/completed in-person sales visit (auto FV-)."""

    TYPE_SALES_CALL = "sales_call"
    TYPE_DEMO = "demo"
    TYPE_CHECK_IN = "check_in"
    TYPE_SUPPORT = "support"
    TYPE_PROSPECTING = "prospecting"
    TYPE_CHOICES = [
        (TYPE_SALES_CALL, "Sales call"),
        (TYPE_DEMO, "Demo"),
        (TYPE_CHECK_IN, "Check-in"),
        (TYPE_SUPPORT, "Support"),
        (TYPE_PROSPECTING, "Prospecting"),
    ]

    STATUS_PLANNED = "planned"
    STATUS_CHECKED_IN = "checked_in"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELED = "canceled"
    STATUS_NO_SHOW = "no_show"
    STATUS_CHOICES = [
        (STATUS_PLANNED, "Planned"),
        (STATUS_CHECKED_IN, "Checked in"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELED, "Canceled"),
        (STATUS_NO_SHOW, "No show"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="mobile_fieldvisits")
    number = models.CharField(max_length=20, blank=True)
    rep_name = models.CharField(max_length=120)
    account_name = models.CharField(max_length=150)
    visit_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_SALES_CALL)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PLANNED)
    scheduled_on = models.DateField(default=timezone.localdate)
    location = models.CharField(max_length=150, blank=True)
    duration_minutes = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-scheduled_on", "-id"]
        unique_together = ("tenant", "number")
        indexes = [
            models.Index(fields=["tenant", "status"], name="fvisit_tenant_status_idx"),
            models.Index(fields=["tenant", "visit_type"], name="fvisit_tenant_type_idx"),
        ]

    def __str__(self):
        return self.number or f"Field visit #{self.pk}"

    def save(self, *args, **kwargs):
        if not self.number and self.tenant_id:
            # Per-tenant sequence with a row lock to avoid duplicate numbers under
            # concurrent creation (idempotent for seeds).
            with transaction.atomic():
                last = (FieldVisit.objects.select_for_update()
                        .filter(tenant_id=self.tenant_id, number__startswith="FV-")
                        .order_by("-number").first())
                seq = 1
                if last and last.number:
                    try:
                        seq = int(last.number.split("-")[1]) + 1
                    except (IndexError, ValueError):
                        seq = (FieldVisit.objects
                               .filter(tenant_id=self.tenant_id, number__startswith="FV-")
                               .count() + 1)
                self.number = f"FV-{seq:05d}"
                super().save(*args, **kwargs)
                return
        super().save(*args, **kwargs)


class MobileQuote(models.Model):
    """Mobile Quoting & Approvals — a quote built/submitted from mobile (auto MQ-)."""

    STATUS_DRAFT = "draft"
    STATUS_SUBMITTED = "submitted"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_EXPIRED = "expired"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_SUBMITTED, "Submitted"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_EXPIRED, "Expired"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="mobile_mobilequotes")
    number = models.CharField(max_length=20, blank=True)
    rep_name = models.CharField(max_length=120)
    customer_name = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    discount_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    submitted_on = models.DateField(default=timezone.localdate)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-submitted_on", "-id"]
        unique_together = ("tenant", "number")
        indexes = [
            models.Index(fields=["tenant", "status"], name="mquote_tenant_status_idx"),
            models.Index(fields=["tenant", "submitted_on"], name="mquote_tenant_subdate_idx"),
        ]

    def __str__(self):
        return self.number or f"Mobile quote #{self.pk}"

    def save(self, *args, **kwargs):
        if not self.number and self.tenant_id:
            # Per-tenant sequence with a row lock to avoid duplicate numbers under
            # concurrent creation (idempotent for seeds).
            with transaction.atomic():
                last = (MobileQuote.objects.select_for_update()
                        .filter(tenant_id=self.tenant_id, number__startswith="MQ-")
                        .order_by("-number").first())
                seq = 1
                if last and last.number:
                    try:
                        seq = int(last.number.split("-")[1]) + 1
                    except (IndexError, ValueError):
                        seq = (MobileQuote.objects
                               .filter(tenant_id=self.tenant_id, number__startswith="MQ-")
                               .count() + 1)
                self.number = f"MQ-{seq:05d}"
                super().save(*args, **kwargs)
                return
        super().save(*args, **kwargs)


class CallActivity(models.Model):
    """Voice & Call Integration — a logged call from the mobile dialer."""

    DIRECTION_INBOUND = "inbound"
    DIRECTION_OUTBOUND = "outbound"
    DIRECTION_MISSED = "missed"
    DIRECTION_CHOICES = [
        (DIRECTION_INBOUND, "Inbound"),
        (DIRECTION_OUTBOUND, "Outbound"),
        (DIRECTION_MISSED, "Missed"),
    ]

    TYPE_SALES = "sales"
    TYPE_FOLLOW_UP = "follow_up"
    TYPE_SUPPORT = "support"
    TYPE_COLD_CALL = "cold_call"
    TYPE_CHOICES = [
        (TYPE_SALES, "Sales"),
        (TYPE_FOLLOW_UP, "Follow-up"),
        (TYPE_SUPPORT, "Support"),
        (TYPE_COLD_CALL, "Cold call"),
    ]

    OUTCOME_CONNECTED = "connected"
    OUTCOME_VOICEMAIL = "voicemail"
    OUTCOME_NO_ANSWER = "no_answer"
    OUTCOME_BUSY = "busy"
    OUTCOME_SCHEDULED_CALLBACK = "scheduled_callback"
    OUTCOME_CHOICES = [
        (OUTCOME_CONNECTED, "Connected"),
        (OUTCOME_VOICEMAIL, "Voicemail"),
        (OUTCOME_NO_ANSWER, "No answer"),
        (OUTCOME_BUSY, "Busy"),
        (OUTCOME_SCHEDULED_CALLBACK, "Scheduled callback"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="mobile_callactivities")
    rep_name = models.CharField(max_length=120)
    contact_name = models.CharField(max_length=150)
    direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES, default=DIRECTION_OUTBOUND)
    call_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_SALES)
    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES, default=OUTCOME_CONNECTED)
    duration_seconds = models.IntegerField(default=0)
    call_date = models.DateField(default=timezone.localdate)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-call_date", "-id"]
        indexes = [
            models.Index(fields=["tenant", "direction"], name="call_tenant_direction_idx"),
            models.Index(fields=["tenant", "outcome"], name="call_tenant_outcome_idx"),
        ]

    def __str__(self):
        return f"{self.get_direction_display()} — {self.contact_name}"


class MobileAlert(models.Model):
    """Mobile Dashboards & Alerts — a push alert surfaced on the mobile dashboard."""

    TYPE_DEAL_UPDATE = "deal_update"
    TYPE_TASK_DUE = "task_due"
    TYPE_QUOTA_WARNING = "quota_warning"
    TYPE_APPROVAL_REQUEST = "approval_request"
    TYPE_SYSTEM = "system"
    TYPE_CHOICES = [
        (TYPE_DEAL_UPDATE, "Deal update"),
        (TYPE_TASK_DUE, "Task due"),
        (TYPE_QUOTA_WARNING, "Quota warning"),
        (TYPE_APPROVAL_REQUEST, "Approval request"),
        (TYPE_SYSTEM, "System"),
    ]

    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"
    PRIORITY_URGENT = "urgent"
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, "Low"),
        (PRIORITY_MEDIUM, "Medium"),
        (PRIORITY_HIGH, "High"),
        (PRIORITY_URGENT, "Urgent"),
    ]

    STATUS_UNREAD = "unread"
    STATUS_READ = "read"
    STATUS_DISMISSED = "dismissed"
    STATUS_ACTIONED = "actioned"
    STATUS_CHOICES = [
        (STATUS_UNREAD, "Unread"),
        (STATUS_READ, "Read"),
        (STATUS_DISMISSED, "Dismissed"),
        (STATUS_ACTIONED, "Actioned"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="mobile_mobilealerts")
    title = models.CharField(max_length=150)
    alert_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_SYSTEM)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_UNREAD)
    recipient = models.CharField(max_length=120, blank=True)
    body = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="malert_tenant_status_idx"),
            models.Index(fields=["tenant", "priority"], name="malert_tenant_priority_idx"),
            models.Index(fields=["tenant", "alert_type"], name="malert_tenant_type_idx"),
        ]

    def __str__(self):
        return self.title
