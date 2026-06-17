from django.db import models
from django.utils import timezone


class Activity(models.Model):
    """Activity Logging & Tracking — a logged sales interaction (call, email, note...)."""

    TYPE_CALL = "call"
    TYPE_EMAIL = "email"
    TYPE_MEETING = "meeting"
    TYPE_NOTE = "note"
    TYPE_DEMO = "demo"
    TYPE_VISIT = "visit"
    TYPE_CHOICES = [
        (TYPE_CALL, "Call"),
        (TYPE_EMAIL, "Email"),
        (TYPE_MEETING, "Meeting"),
        (TYPE_NOTE, "Note"),
        (TYPE_DEMO, "Demo"),
        (TYPE_VISIT, "Visit"),
    ]

    DIRECTION_INBOUND = "inbound"
    DIRECTION_OUTBOUND = "outbound"
    DIRECTION_INTERNAL = "internal"
    DIRECTION_CHOICES = [
        (DIRECTION_INBOUND, "Inbound"),
        (DIRECTION_OUTBOUND, "Outbound"),
        (DIRECTION_INTERNAL, "Internal"),
    ]

    OUTCOME_PENDING = "pending"
    OUTCOME_SUCCESSFUL = "successful"
    OUTCOME_NO_ANSWER = "no_answer"
    OUTCOME_FOLLOW_UP = "follow_up"
    OUTCOME_NOT_INTERESTED = "not_interested"
    OUTCOME_CHOICES = [
        (OUTCOME_PENDING, "Pending"),
        (OUTCOME_SUCCESSFUL, "Successful"),
        (OUTCOME_NO_ANSWER, "No answer"),
        (OUTCOME_FOLLOW_UP, "Needs follow-up"),
        (OUTCOME_NOT_INTERESTED, "Not interested"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="activities_activitys"
    )
    subject = models.CharField(max_length=200)
    activity_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_CALL)
    direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES, default=DIRECTION_OUTBOUND)
    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES, default=OUTCOME_PENDING)
    contact_name = models.CharField(max_length=150, blank=True)
    company_name = models.CharField(max_length=150, blank=True)
    owner_name = models.CharField(max_length=150, blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    activity_date = models.DateField(default=timezone.localdate)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-activity_date", "-id"]
        indexes = [
            models.Index(fields=["tenant", "activity_type"], name="act_tenant_type_idx"),
            models.Index(fields=["tenant", "activity_date"], name="act_tenant_date_idx"),
        ]

    def __str__(self):
        return self.subject


class SalesTask(models.Model):
    """Task & Follow-up Management — a to-do / follow-up tied to the pipeline."""

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

    STATUS_OPEN = "open"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_DEFERRED = "deferred"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_IN_PROGRESS, "In progress"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_DEFERRED, "Deferred"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="activities_salestasks"
    )
    # Intra-app FK: a task may follow up on a logged activity (same app).
    activity = models.ForeignKey(
        "activities.Activity", on_delete=models.SET_NULL,
        related_name="follow_up_tasks", null=True, blank=True,
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    assigned_to = models.CharField(max_length=150, blank=True)
    related_to = models.CharField(max_length=200, blank=True)
    due_date = models.DateField(null=True, blank=True)
    reminder_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-due_date", "-id"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="task_tenant_status_idx"),
            models.Index(fields=["tenant", "due_date"], name="task_tenant_due_idx"),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.status == self.STATUS_COMPLETED and self.completed_at is None:
            self.completed_at = timezone.now()
        if self.status != self.STATUS_COMPLETED:
            self.completed_at = None
        super().save(*args, **kwargs)


class Meeting(models.Model):
    """Calendar & Meeting Scheduling — a scheduled meeting/appointment."""

    TYPE_DISCOVERY = "discovery"
    TYPE_DEMO = "demo"
    TYPE_PROPOSAL = "proposal"
    TYPE_NEGOTIATION = "negotiation"
    TYPE_CHECK_IN = "check_in"
    TYPE_INTERNAL = "internal"
    TYPE_CHOICES = [
        (TYPE_DISCOVERY, "Discovery"),
        (TYPE_DEMO, "Demo"),
        (TYPE_PROPOSAL, "Proposal"),
        (TYPE_NEGOTIATION, "Negotiation"),
        (TYPE_CHECK_IN, "Check-in"),
        (TYPE_INTERNAL, "Internal"),
    ]

    LOCATION_ONSITE = "onsite"
    LOCATION_VIDEO = "video"
    LOCATION_PHONE = "phone"
    LOCATION_CHOICES = [
        (LOCATION_ONSITE, "On-site"),
        (LOCATION_VIDEO, "Video call"),
        (LOCATION_PHONE, "Phone"),
    ]

    STATUS_SCHEDULED = "scheduled"
    STATUS_CONFIRMED = "confirmed"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    STATUS_NO_SHOW = "no_show"
    STATUS_CHOICES = [
        (STATUS_SCHEDULED, "Scheduled"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
        (STATUS_NO_SHOW, "No show"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="activities_meetings"
    )
    title = models.CharField(max_length=200)
    meeting_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_DISCOVERY)
    location_type = models.CharField(max_length=20, choices=LOCATION_CHOICES, default=LOCATION_VIDEO)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SCHEDULED)
    attendees = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    organizer_name = models.CharField(max_length=150, blank=True)
    scheduled_date = models.DateField(default=timezone.localdate)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    agenda = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-scheduled_date", "-id"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="meeting_tenant_status_idx"),
            models.Index(fields=["tenant", "scheduled_date"], name="meeting_tenant_date_idx"),
        ]

    def __str__(self):
        return self.title


class EmailLog(models.Model):
    """Email Integration & Tracking — a sent/received email with engagement state."""

    DIRECTION_OUTBOUND = "outbound"
    DIRECTION_INBOUND = "inbound"
    DIRECTION_CHOICES = [
        (DIRECTION_OUTBOUND, "Outbound"),
        (DIRECTION_INBOUND, "Inbound"),
    ]

    STATUS_DRAFT = "draft"
    STATUS_SENT = "sent"
    STATUS_DELIVERED = "delivered"
    STATUS_OPENED = "opened"
    STATUS_CLICKED = "clicked"
    STATUS_REPLIED = "replied"
    STATUS_BOUNCED = "bounced"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_SENT, "Sent"),
        (STATUS_DELIVERED, "Delivered"),
        (STATUS_OPENED, "Opened"),
        (STATUS_CLICKED, "Clicked"),
        (STATUS_REPLIED, "Replied"),
        (STATUS_BOUNCED, "Bounced"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="activities_emaillogs"
    )
    # Intra-app FK: an email may be tied to a logged activity (same app).
    activity = models.ForeignKey(
        "activities.Activity", on_delete=models.SET_NULL,
        related_name="email_logs", null=True, blank=True,
    )
    subject = models.CharField(max_length=255)
    direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES, default=DIRECTION_OUTBOUND)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    from_email = models.EmailField(blank=True)
    to_email = models.EmailField(blank=True)
    open_count = models.PositiveIntegerField(default=0)
    click_count = models.PositiveIntegerField(default=0)
    sent_at = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    opened_at = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    body = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="email_tenant_status_idx"),
            models.Index(fields=["tenant", "direction"], name="email_tenant_dir_idx"),
        ]

    def __str__(self):
        return self.subject

    def save(self, *args, **kwargs):
        # System-set engagement timestamps based on lifecycle state.
        sent_states = {
            self.STATUS_SENT, self.STATUS_DELIVERED, self.STATUS_OPENED,
            self.STATUS_CLICKED, self.STATUS_REPLIED, self.STATUS_BOUNCED,
        }
        if self.status in sent_states and self.sent_at is None:
            self.sent_at = timezone.now()
        opened_states = {self.STATUS_OPENED, self.STATUS_CLICKED, self.STATUS_REPLIED}
        if self.status in opened_states and self.opened_at is None:
            self.opened_at = timezone.now()
        super().save(*args, **kwargs)


class SalesPlan(models.Model):
    """Daily/Weekly Sales Planning — a planning sheet (auto-numbered PLAN-00001)."""

    PERIOD_DAILY = "daily"
    PERIOD_WEEKLY = "weekly"
    PERIOD_MONTHLY = "monthly"
    PERIOD_CHOICES = [
        (PERIOD_DAILY, "Daily"),
        (PERIOD_WEEKLY, "Weekly"),
        (PERIOD_MONTHLY, "Monthly"),
    ]

    STATUS_DRAFT = "draft"
    STATUS_ACTIVE = "active"
    STATUS_COMPLETED = "completed"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_ARCHIVED, "Archived"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="activities_salesplans"
    )
    number = models.CharField(max_length=20, blank=True)
    title = models.CharField(max_length=200)
    owner_name = models.CharField(max_length=150, blank=True)
    period_type = models.CharField(max_length=20, choices=PERIOD_CHOICES, default=PERIOD_WEEKLY)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    start_date = models.DateField(default=timezone.localdate)
    end_date = models.DateField(null=True, blank=True)
    target_calls = models.PositiveIntegerField(default=0)
    target_meetings = models.PositiveIntegerField(default=0)
    revenue_goal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    objectives = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date", "-id"]
        unique_together = ("tenant", "number")
        indexes = [
            models.Index(fields=["tenant", "status"], name="plan_tenant_status_idx"),
            models.Index(fields=["tenant", "start_date"], name="plan_tenant_start_idx"),
        ]

    def __str__(self):
        return self.number or self.title

    def save(self, *args, **kwargs):
        if not self.number and self.tenant_id:
            # Per-tenant sequence with an existence guard (idempotent for seeds).
            last = (SalesPlan.objects.filter(tenant_id=self.tenant_id, number__startswith="PLAN-")
                    .order_by("-number").first())
            seq = 1
            if last and last.number:
                try:
                    seq = int(last.number.split("-")[1]) + 1
                except (IndexError, ValueError):
                    seq = SalesPlan.objects.filter(tenant_id=self.tenant_id).count() + 1
            self.number = f"PLAN-{seq:05d}"
        super().save(*args, **kwargs)
