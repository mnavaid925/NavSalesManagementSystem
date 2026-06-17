from django.db import models
from django.utils import timezone


class LeadSource(models.Model):
    """Lead Qualification & Routing — an inbound channel that captures leads.

    Sources hold the routing rule (round-robin / owner) and qualification config
    that downstream leads inherit. Self-contained to this app (no cross-module FKs).
    """

    TYPE_WEB_FORM = "web_form"
    TYPE_LANDING_PAGE = "landing_page"
    TYPE_REFERRAL = "referral"
    TYPE_EVENT = "event"
    TYPE_PAID_ADS = "paid_ads"
    TYPE_COLD_OUTREACH = "cold_outreach"
    TYPE_PARTNER = "partner"
    TYPE_CHOICES = [
        (TYPE_WEB_FORM, "Web form"),
        (TYPE_LANDING_PAGE, "Landing page"),
        (TYPE_REFERRAL, "Referral"),
        (TYPE_EVENT, "Event"),
        (TYPE_PAID_ADS, "Paid ads"),
        (TYPE_COLD_OUTREACH, "Cold outreach"),
        (TYPE_PARTNER, "Partner"),
    ]

    ROUTING_ROUND_ROBIN = "round_robin"
    ROUTING_OWNER = "owner"
    ROUTING_TEAM = "team"
    ROUTING_MANUAL = "manual"
    ROUTING_CHOICES = [
        (ROUTING_ROUND_ROBIN, "Round robin"),
        (ROUTING_OWNER, "Single owner"),
        (ROUTING_TEAM, "Team queue"),
        (ROUTING_MANUAL, "Manual review"),
    ]

    STATUS_ACTIVE = "active"
    STATUS_PAUSED = "paused"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_PAUSED, "Paused"),
        (STATUS_ARCHIVED, "Archived"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="leads_leadsources")
    name = models.CharField(max_length=150)
    source_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_WEB_FORM)
    routing_rule = models.CharField(max_length=20, choices=ROUTING_CHOICES, default=ROUTING_ROUND_ROBIN)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    default_owner = models.CharField(max_length=120, blank=True)
    cost_per_lead = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class NurtureCampaign(models.Model):
    """Lead Nurturing & Drip Campaigns — a multi-touch drip sequence."""

    CHANNEL_EMAIL = "email"
    CHANNEL_SMS = "sms"
    CHANNEL_SOCIAL = "social"
    CHANNEL_MULTI = "multi"
    CHANNEL_CHOICES = [
        (CHANNEL_EMAIL, "Email"),
        (CHANNEL_SMS, "SMS"),
        (CHANNEL_SOCIAL, "Social"),
        (CHANNEL_MULTI, "Multi-channel"),
    ]

    STATUS_DRAFT = "draft"
    STATUS_SCHEDULED = "scheduled"
    STATUS_RUNNING = "running"
    STATUS_PAUSED = "paused"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_SCHEDULED, "Scheduled"),
        (STATUS_RUNNING, "Running"),
        (STATUS_PAUSED, "Paused"),
        (STATUS_COMPLETED, "Completed"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="leads_nurturecampaigns")
    name = models.CharField(max_length=150)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default=CHANNEL_EMAIL)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    step_count = models.PositiveIntegerField(default=1)
    cadence_days = models.PositiveIntegerField(default=3)
    enrolled_count = models.PositiveIntegerField(default=0)
    start_on = models.DateField(null=True, blank=True)
    end_on = models.DateField(null=True, blank=True)
    goal = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "name"]

    def __str__(self):
        return self.name


class Lead(models.Model):
    """Lead Capture & Ingestion — a captured prospect record (auto-numbered LEAD-00001)."""

    STATUS_NEW = "new"
    STATUS_CONTACTED = "contacted"
    STATUS_WORKING = "working"
    STATUS_NURTURING = "nurturing"
    STATUS_QUALIFIED = "qualified"
    STATUS_UNQUALIFIED = "unqualified"
    STATUS_CONVERTED = "converted"
    STATUS_CHOICES = [
        (STATUS_NEW, "New"),
        (STATUS_CONTACTED, "Contacted"),
        (STATUS_WORKING, "Working"),
        (STATUS_NURTURING, "Nurturing"),
        (STATUS_QUALIFIED, "Qualified"),
        (STATUS_UNQUALIFIED, "Unqualified"),
        (STATUS_CONVERTED, "Converted"),
    ]

    RATING_HOT = "hot"
    RATING_WARM = "warm"
    RATING_COLD = "cold"
    RATING_CHOICES = [
        (RATING_HOT, "Hot"),
        (RATING_WARM, "Warm"),
        (RATING_COLD, "Cold"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="leads_leads")
    source = models.ForeignKey(
        "leads.LeadSource", on_delete=models.SET_NULL,
        related_name="leads", null=True, blank=True)
    campaign = models.ForeignKey(
        "leads.NurtureCampaign", on_delete=models.SET_NULL,
        related_name="leads", null=True, blank=True)
    number = models.CharField(max_length=20, blank=True)
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    company = models.CharField(max_length=150, blank=True)
    job_title = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    rating = models.CharField(max_length=10, choices=RATING_CHOICES, default=RATING_COLD)
    owner = models.CharField(max_length=120, blank=True)
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    captured_on = models.DateField(default=timezone.localdate)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-captured_on", "-id"]
        unique_together = ("tenant", "number")
        indexes = [
            models.Index(fields=["tenant", "status"], name="lead_tenant_status_idx"),
            models.Index(fields=["tenant", "captured_on"], name="lead_tenant_captured_idx"),
        ]

    def __str__(self):
        full = f"{self.first_name} {self.last_name}".strip()
        return f"{self.number} — {full}" if self.number else full

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def save(self, *args, **kwargs):
        if not self.number and self.tenant_id:
            # Per-tenant sequence with an existence guard (idempotent for seeds).
            last = (Lead.objects.filter(tenant_id=self.tenant_id, number__startswith="LEAD-")
                    .order_by("-number").first())
            seq = 1
            if last and last.number:
                try:
                    seq = int(last.number.split("-")[1]) + 1
                except (IndexError, ValueError):
                    seq = Lead.objects.filter(tenant_id=self.tenant_id).count() + 1
            self.number = f"LEAD-{seq:05d}"
        super().save(*args, **kwargs)


class LeadScore(models.Model):
    """Lead Scoring & Grading — a computed score + grade snapshot for a lead."""

    GRADE_A = "A"
    GRADE_B = "B"
    GRADE_C = "C"
    GRADE_D = "D"
    GRADE_CHOICES = [
        (GRADE_A, "A — Excellent"),
        (GRADE_B, "B — Good"),
        (GRADE_C, "C — Fair"),
        (GRADE_D, "D — Poor"),
    ]

    MODEL_RULES = "rules"
    MODEL_PREDICTIVE = "predictive"
    MODEL_MANUAL = "manual"
    MODEL_CHOICES = [
        (MODEL_RULES, "Rules-based"),
        (MODEL_PREDICTIVE, "Predictive (AI)"),
        (MODEL_MANUAL, "Manual"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="leads_leadscores")
    lead = models.ForeignKey(
        "leads.Lead", on_delete=models.CASCADE, related_name="scores")
    score = models.PositiveIntegerField(default=0)
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, default=GRADE_C)
    scoring_model = models.CharField(max_length=20, choices=MODEL_CHOICES, default=MODEL_RULES)
    demographic_points = models.IntegerField(default=0)
    behavioral_points = models.IntegerField(default=0)
    reason = models.CharField(max_length=255, blank=True)
    scored_on = models.DateField(default=timezone.localdate)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-scored_on", "-score"]
        indexes = [
            models.Index(fields=["tenant", "grade"], name="leadscore_tenant_grade_idx"),
        ]

    def __str__(self):
        return f"{self.lead.full_name} — {self.score} ({self.grade})"


class LeadConversion(models.Model):
    """Lead Conversion & Handoff — the qualified-lead handoff record (auto-numbered CNV-00001)."""

    STATUS_PENDING = "pending"
    STATUS_ACCEPTED = "accepted"
    STATUS_REJECTED = "rejected"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_COMPLETED, "Completed"),
    ]

    OUTCOME_OPPORTUNITY = "opportunity"
    OUTCOME_ACCOUNT = "account"
    OUTCOME_CONTACT = "contact"
    OUTCOME_DISQUALIFIED = "disqualified"
    OUTCOME_CHOICES = [
        (OUTCOME_OPPORTUNITY, "Opportunity created"),
        (OUTCOME_ACCOUNT, "Account created"),
        (OUTCOME_CONTACT, "Contact created"),
        (OUTCOME_DISQUALIFIED, "Disqualified"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="leads_leadconversions")
    lead = models.ForeignKey(
        "leads.Lead", on_delete=models.CASCADE, related_name="conversions")
    number = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES, default=OUTCOME_OPPORTUNITY)
    assigned_to = models.CharField(max_length=120, blank=True)
    deal_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    handoff_notes = models.TextField(blank=True)
    converted_at = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        unique_together = ("tenant", "number")
        indexes = [
            models.Index(fields=["tenant", "status"], name="leadconv_tenant_status_idx"),
        ]

    def __str__(self):
        return self.number or f"Conversion #{self.pk}"

    def save(self, *args, **kwargs):
        if not self.number and self.tenant_id:
            # Per-tenant sequence with an existence guard (idempotent for seeds).
            last = (LeadConversion.objects.filter(tenant_id=self.tenant_id, number__startswith="CNV-")
                    .order_by("-number").first())
            seq = 1
            if last and last.number:
                try:
                    seq = int(last.number.split("-")[1]) + 1
                except (IndexError, ValueError):
                    seq = LeadConversion.objects.filter(tenant_id=self.tenant_id).count() + 1
            self.number = f"CNV-{seq:05d}"
        # Mark the system timestamp once the handoff reaches a terminal accept state.
        if self.status in (self.STATUS_ACCEPTED, self.STATUS_COMPLETED) and self.converted_at is None:
            self.converted_at = timezone.now()
        super().save(*args, **kwargs)
