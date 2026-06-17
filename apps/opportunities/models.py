from django.db import models
from django.utils import timezone


class PipelineStage(models.Model):
    """Opportunity Creation & Staging — a stage in the sales pipeline.

    Stages give the pipeline its columns (Qualification -> Closed Won) and carry a
    default win-probability used for weighted forecasting.
    """

    TYPE_OPEN = "open"
    TYPE_WON = "won"
    TYPE_LOST = "lost"
    TYPE_CHOICES = [
        (TYPE_OPEN, "Open"),
        (TYPE_WON, "Won"),
        (TYPE_LOST, "Lost"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="opportunities_pipelinestages")
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    probability = models.PositiveIntegerField(default=10, help_text="Default win probability (0-100%).")
    stage_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_OPEN)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


class Opportunity(models.Model):
    """Opportunity Tracking & Updates — a revenue deal moving through the pipeline.

    Auto-numbered per tenant (OPP-00001). System timestamps (closed_at) are set in
    code when the stage type flips to won/lost — kept off the form.
    """

    STATUS_OPEN = "open"
    STATUS_WON = "won"
    STATUS_LOST = "lost"
    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_WON, "Won"),
        (STATUS_LOST, "Lost"),
    ]

    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"
    PRIORITY_CRITICAL = "critical"
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, "Low"),
        (PRIORITY_MEDIUM, "Medium"),
        (PRIORITY_HIGH, "High"),
        (PRIORITY_CRITICAL, "Critical"),
    ]

    FORECAST_PIPELINE = "pipeline"
    FORECAST_BEST_CASE = "best_case"
    FORECAST_COMMIT = "commit"
    FORECAST_OMITTED = "omitted"
    FORECAST_CHOICES = [
        (FORECAST_PIPELINE, "Pipeline"),
        (FORECAST_BEST_CASE, "Best case"),
        (FORECAST_COMMIT, "Commit"),
        (FORECAST_OMITTED, "Omitted"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="opportunities_opportunities")
    number = models.CharField(max_length=20, blank=True)
    name = models.CharField(max_length=180)
    account_name = models.CharField(max_length=180, blank=True)
    stage = models.ForeignKey(
        "opportunities.PipelineStage", on_delete=models.SET_NULL,
        related_name="opportunities", null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_OPEN)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    forecast_category = models.CharField(max_length=12, choices=FORECAST_CHOICES, default=FORECAST_PIPELINE)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    probability = models.PositiveIntegerField(default=10, help_text="Win probability (0-100%).")
    owner_name = models.CharField(max_length=150, blank=True)
    source = models.CharField(max_length=120, blank=True)
    expected_close_date = models.DateField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        unique_together = ("tenant", "number")
        indexes = [
            models.Index(fields=["tenant", "status"], name="opp_tenant_status_idx"),
            models.Index(fields=["tenant", "stage"], name="opp_tenant_stage_idx"),
        ]

    def __str__(self):
        return f"{self.number} — {self.name}" if self.number else self.name

    @property
    def weighted_amount(self):
        """Expected value = amount x probability (used in forecasting rollups)."""
        return (self.amount or 0) * self.probability / 100

    def save(self, *args, **kwargs):
        if not self.number and self.tenant_id:
            # Per-tenant sequence with an existence guard (idempotent for seeds).
            last = (Opportunity.objects.filter(tenant_id=self.tenant_id, number__startswith="OPP-")
                    .order_by("-number").first())
            seq = 1
            if last and last.number:
                try:
                    seq = int(last.number.split("-")[1]) + 1
                except (IndexError, ValueError):
                    seq = Opportunity.objects.filter(tenant_id=self.tenant_id).count() + 1
            self.number = f"OPP-{seq:05d}"
        # Sync close timestamp with terminal statuses (won/lost) — system-set.
        if self.status in (self.STATUS_WON, self.STATUS_LOST) and self.closed_at is None:
            self.closed_at = timezone.now()
        if self.status == self.STATUS_OPEN:
            self.closed_at = None
        super().save(*args, **kwargs)


class OpportunityActivity(models.Model):
    """Opportunity Tracking & Updates — a logged touch on a deal (call, email, note)."""

    TYPE_NOTE = "note"
    TYPE_CALL = "call"
    TYPE_EMAIL = "email"
    TYPE_MEETING = "meeting"
    TYPE_STAGE_CHANGE = "stage_change"
    TYPE_CHOICES = [
        (TYPE_NOTE, "Note"),
        (TYPE_CALL, "Call"),
        (TYPE_EMAIL, "Email"),
        (TYPE_MEETING, "Meeting"),
        (TYPE_STAGE_CHANGE, "Stage change"),
    ]

    OUTCOME_PENDING = "pending"
    OUTCOME_POSITIVE = "positive"
    OUTCOME_NEUTRAL = "neutral"
    OUTCOME_NEGATIVE = "negative"
    OUTCOME_CHOICES = [
        (OUTCOME_PENDING, "Pending"),
        (OUTCOME_POSITIVE, "Positive"),
        (OUTCOME_NEUTRAL, "Neutral"),
        (OUTCOME_NEGATIVE, "Negative"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="opportunities_opportunityactivitys")
    opportunity = models.ForeignKey(
        "opportunities.Opportunity", on_delete=models.CASCADE, related_name="activities")
    subject = models.CharField(max_length=180)
    activity_type = models.CharField(max_length=15, choices=TYPE_CHOICES, default=TYPE_NOTE)
    outcome = models.CharField(max_length=10, choices=OUTCOME_CHOICES, default=OUTCOME_PENDING)
    performed_by = models.CharField(max_length=150, blank=True)
    activity_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-activity_date", "-created_at"]

    def __str__(self):
        return self.subject


class Competitor(models.Model):
    """Competitive Intelligence — a rival contesting a deal, with a threat read."""

    THREAT_LOW = "low"
    THREAT_MEDIUM = "medium"
    THREAT_HIGH = "high"
    THREAT_CHOICES = [
        (THREAT_LOW, "Low"),
        (THREAT_MEDIUM, "Medium"),
        (THREAT_HIGH, "High"),
    ]

    STATUS_ACTIVE = "active"
    STATUS_ELIMINATED = "eliminated"
    STATUS_WON_AGAINST = "won_against"
    STATUS_LOST_TO = "lost_to"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_ELIMINATED, "Eliminated"),
        (STATUS_WON_AGAINST, "Won against"),
        (STATUS_LOST_TO, "Lost to"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="opportunities_competitors")
    opportunity = models.ForeignKey(
        "opportunities.Opportunity", on_delete=models.CASCADE, related_name="competitors")
    name = models.CharField(max_length=180)
    threat_level = models.CharField(max_length=10, choices=THREAT_CHOICES, default=THREAT_MEDIUM)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    strengths = models.TextField(blank=True)
    weaknesses = models.TextField(blank=True)
    our_strategy = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name", "-created_at"]

    def __str__(self):
        return self.name


class DealCollaborator(models.Model):
    """Deal Collaboration & Team Selling — a teammate engaged on a deal."""

    ROLE_OWNER = "owner"
    ROLE_SALES_ENG = "sales_engineer"
    ROLE_EXEC_SPONSOR = "exec_sponsor"
    ROLE_PRODUCT = "product"
    ROLE_LEGAL = "legal"
    ROLE_SUPPORT = "support"
    ROLE_CHOICES = [
        (ROLE_OWNER, "Deal owner"),
        (ROLE_SALES_ENG, "Sales engineer"),
        (ROLE_EXEC_SPONSOR, "Executive sponsor"),
        (ROLE_PRODUCT, "Product specialist"),
        (ROLE_LEGAL, "Legal"),
        (ROLE_SUPPORT, "Support"),
    ]

    STATUS_INVITED = "invited"
    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_CHOICES = [
        (STATUS_INVITED, "Invited"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_INACTIVE, "Inactive"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="opportunities_dealcollaborators")
    opportunity = models.ForeignKey(
        "opportunities.Opportunity", on_delete=models.CASCADE, related_name="collaborators")
    member_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    team_role = models.CharField(max_length=15, choices=ROLE_CHOICES, default=ROLE_SALES_ENG)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    contribution = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["member_name", "-created_at"]

    def __str__(self):
        return f"{self.member_name} ({self.get_team_role_display()})"
