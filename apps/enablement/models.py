from django.db import models
from django.utils import timezone


class ContentAsset(models.Model):
    """Content Repository & Search — a reusable sales collateral item."""

    TYPE_DECK = "deck"
    TYPE_ONE_PAGER = "one_pager"
    TYPE_CASE_STUDY = "case_study"
    TYPE_WHITEPAPER = "whitepaper"
    TYPE_VIDEO = "video"
    TYPE_TEMPLATE = "template"
    TYPE_OTHER = "other"
    TYPE_CHOICES = [
        (TYPE_DECK, "Pitch Deck"),
        (TYPE_ONE_PAGER, "One-Pager"),
        (TYPE_CASE_STUDY, "Case Study"),
        (TYPE_WHITEPAPER, "Whitepaper"),
        (TYPE_VIDEO, "Video"),
        (TYPE_TEMPLATE, "Template"),
        (TYPE_OTHER, "Other"),
    ]

    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_PUBLISHED, "Published"),
        (STATUS_ARCHIVED, "Archived"),
    ]

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, related_name="enablement_contentassets")
    title = models.CharField(max_length=180)
    asset_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_DECK)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    description = models.TextField(blank=True)
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated keywords for search.")
    file_url = models.URLField(blank=True)
    owner = models.CharField(max_length=120, blank=True)
    view_count = models.PositiveIntegerField(default=0)
    published_at = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-id"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.status == self.STATUS_PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()
        if self.status != self.STATUS_PUBLISHED:
            self.published_at = None
        super().save(*args, **kwargs)


class Playbook(models.Model):
    """Sales Playbooks & Guidance — stage/persona guidance for reps."""

    STAGE_PROSPECTING = "prospecting"
    STAGE_DISCOVERY = "discovery"
    STAGE_DEMO = "demo"
    STAGE_NEGOTIATION = "negotiation"
    STAGE_CLOSING = "closing"
    STAGE_ONBOARDING = "onboarding"
    STAGE_CHOICES = [
        (STAGE_PROSPECTING, "Prospecting"),
        (STAGE_DISCOVERY, "Discovery"),
        (STAGE_DEMO, "Demo"),
        (STAGE_NEGOTIATION, "Negotiation"),
        (STAGE_CLOSING, "Closing"),
        (STAGE_ONBOARDING, "Onboarding"),
    ]

    STATUS_DRAFT = "draft"
    STATUS_ACTIVE = "active"
    STATUS_RETIRED = "retired"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_RETIRED, "Retired"),
    ]

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, related_name="enablement_playbooks")
    title = models.CharField(max_length=180)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default=STAGE_PROSPECTING)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    persona = models.CharField(max_length=120, blank=True, help_text="Target buyer persona.")
    summary = models.TextField(blank=True)
    guidance = models.TextField(blank=True, help_text="The plays, talk tracks and next steps.")
    owner = models.CharField(max_length=120, blank=True)
    version = models.CharField(max_length=20, default="1.0")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["stage", "title"]

    def __str__(self):
        return self.title


class TrainingRecord(models.Model):
    """Training & Certification Tracking — a rep's enrollment in a course/cert."""

    KIND_COURSE = "course"
    KIND_CERTIFICATION = "certification"
    KIND_WORKSHOP = "workshop"
    KIND_ONBOARDING = "onboarding"
    KIND_CHOICES = [
        (KIND_COURSE, "Course"),
        (KIND_CERTIFICATION, "Certification"),
        (KIND_WORKSHOP, "Workshop"),
        (KIND_ONBOARDING, "Onboarding"),
    ]

    STATUS_NOT_STARTED = "not_started"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_EXPIRED = "expired"
    STATUS_CHOICES = [
        (STATUS_NOT_STARTED, "Not started"),
        (STATUS_IN_PROGRESS, "In progress"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_EXPIRED, "Expired"),
    ]

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, related_name="enablement_trainingrecords")
    course_name = models.CharField(max_length=180)
    rep_name = models.CharField(max_length=120)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default=KIND_COURSE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NOT_STARTED)
    provider = models.CharField(max_length=120, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    enrolled_on = models.DateField(default=timezone.localdate)
    due_on = models.DateField(null=True, blank=True)
    expires_on = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-enrolled_on", "-id"]

    def __str__(self):
        return f"{self.rep_name} — {self.course_name}"

    def save(self, *args, **kwargs):
        if self.status == self.STATUS_COMPLETED and self.completed_at is None:
            self.completed_at = timezone.now()
        if self.status != self.STATUS_COMPLETED:
            self.completed_at = None
        super().save(*args, **kwargs)


class CallRecording(models.Model):
    """Coaching & Call Recording — a recorded call reviewed for coaching."""

    TYPE_DISCOVERY = "discovery"
    TYPE_DEMO = "demo"
    TYPE_NEGOTIATION = "negotiation"
    TYPE_CHECK_IN = "check_in"
    TYPE_CLOSING = "closing"
    TYPE_CHOICES = [
        (TYPE_DISCOVERY, "Discovery"),
        (TYPE_DEMO, "Demo"),
        (TYPE_NEGOTIATION, "Negotiation"),
        (TYPE_CHECK_IN, "Check-in"),
        (TYPE_CLOSING, "Closing"),
    ]

    STATUS_PENDING = "pending"
    STATUS_REVIEWED = "reviewed"
    STATUS_COACHED = "coached"
    STATUS_FLAGGED = "flagged"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending review"),
        (STATUS_REVIEWED, "Reviewed"),
        (STATUS_COACHED, "Coached"),
        (STATUS_FLAGGED, "Flagged"),
    ]

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, related_name="enablement_callrecordings")
    title = models.CharField(max_length=180)
    rep_name = models.CharField(max_length=120)
    coach_name = models.CharField(max_length=120, blank=True)
    call_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_DISCOVERY)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    duration_minutes = models.PositiveIntegerField(default=0)
    recording_url = models.URLField(blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    coaching_notes = models.TextField(blank=True)
    call_date = models.DateField(default=timezone.localdate)
    reviewed_at = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-call_date", "-id"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        reviewed_states = (self.STATUS_REVIEWED, self.STATUS_COACHED)
        if self.status in reviewed_states and self.reviewed_at is None:
            self.reviewed_at = timezone.now()
        if self.status not in reviewed_states:
            self.reviewed_at = None
        super().save(*args, **kwargs)


class CompetitiveCard(models.Model):
    """Competitive Intelligence Library — a battlecard on a competitor."""

    THREAT_LOW = "low"
    THREAT_MEDIUM = "medium"
    THREAT_HIGH = "high"
    THREAT_CHOICES = [
        (THREAT_LOW, "Low"),
        (THREAT_MEDIUM, "Medium"),
        (THREAT_HIGH, "High"),
    ]

    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_PUBLISHED, "Published"),
        (STATUS_ARCHIVED, "Archived"),
    ]

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, related_name="enablement_competitivecards")
    competitor_name = models.CharField(max_length=180)
    category = models.CharField(max_length=120, blank=True)
    threat_level = models.CharField(max_length=20, choices=THREAT_CHOICES, default=THREAT_MEDIUM)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    overview = models.TextField(blank=True)
    our_strengths = models.TextField(blank=True, help_text="Where we win.")
    their_strengths = models.TextField(blank=True, help_text="Where they win.")
    objection_handling = models.TextField(blank=True)
    owner = models.CharField(max_length=120, blank=True)
    last_updated_on = models.DateField(default=timezone.localdate)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["competitor_name"]

    def __str__(self):
        return self.competitor_name
