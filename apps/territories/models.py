from decimal import Decimal

from django.db import models, transaction
from django.utils import timezone


def _current_year():
    """Callable default so the fiscal year is resolved at row-creation time."""
    return timezone.localdate().year


class Territory(models.Model):
    """Territory Design & Mapping — a sales territory defined by geography/segment."""

    TYPE_GEOGRAPHIC = "geographic"
    TYPE_INDUSTRY = "industry"
    TYPE_ACCOUNT = "account"
    TYPE_PRODUCT = "product"
    TYPE_NAMED_ACCOUNT = "named_account"
    TYPE_CHOICES = [
        (TYPE_GEOGRAPHIC, "Geographic"),
        (TYPE_INDUSTRY, "Industry / Vertical"),
        (TYPE_ACCOUNT, "Account Size"),
        (TYPE_PRODUCT, "Product Line"),
        (TYPE_NAMED_ACCOUNT, "Named Account"),
    ]

    STATUS_DRAFT = "draft"
    STATUS_ACTIVE = "active"
    STATUS_UNDER_REVIEW = "under_review"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_UNDER_REVIEW, "Under review"),
        (STATUS_ARCHIVED, "Archived"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="territories_territorys")
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=40, blank=True)
    territory_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_GEOGRAPHIC)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    region = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=80, blank=True)
    description = models.TextField(blank=True)
    account_count = models.PositiveIntegerField(default=0)
    annual_potential = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name", "-id"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="terr_tenant_status_idx"),
            models.Index(fields=["tenant", "territory_type"], name="terr_tenant_type_idx"),
        ]

    def __str__(self):
        return self.name


class TerritoryAssignment(models.Model):
    """Territory Assignment & Rebalancing — a rep/team assignment to a territory."""

    ROLE_OWNER = "owner"
    ROLE_OVERLAY = "overlay"
    ROLE_BACKUP = "backup"
    ROLE_MANAGER = "manager"
    ROLE_CHOICES = [
        (ROLE_OWNER, "Primary owner"),
        (ROLE_OVERLAY, "Overlay specialist"),
        (ROLE_BACKUP, "Backup / cover"),
        (ROLE_MANAGER, "Manager"),
    ]

    STATUS_PROPOSED = "proposed"
    STATUS_ACTIVE = "active"
    STATUS_REBALANCING = "rebalancing"
    STATUS_ENDED = "ended"
    STATUS_CHOICES = [
        (STATUS_PROPOSED, "Proposed"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_REBALANCING, "Rebalancing"),
        (STATUS_ENDED, "Ended"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="territories_territoryassignments")
    territory = models.ForeignKey(
        "territories.Territory", on_delete=models.CASCADE, related_name="assignments")
    rep_name = models.CharField(max_length=150)
    rep_email = models.EmailField(blank=True)
    assignment_role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_OWNER)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PROPOSED)
    workload_percent = models.PositiveIntegerField(default=100)
    effective_date = models.DateField(default=timezone.localdate)
    end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-effective_date", "-id"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="ta_tenant_status_idx"),
            models.Index(fields=["tenant", "territory"], name="ta_tenant_territory_idx"),
        ]

    def __str__(self):
        return f"{self.rep_name} → {self.territory.name}"


class QuotaPlan(models.Model):
    """Quota Planning & Allocation — an auto-numbered quota target (QP-00001)."""

    PERIOD_MONTHLY = "monthly"
    PERIOD_QUARTERLY = "quarterly"
    PERIOD_ANNUAL = "annual"
    PERIOD_CHOICES = [
        (PERIOD_MONTHLY, "Monthly"),
        (PERIOD_QUARTERLY, "Quarterly"),
        (PERIOD_ANNUAL, "Annual"),
    ]

    STATUS_DRAFT = "draft"
    STATUS_PROPOSED = "proposed"
    STATUS_APPROVED = "approved"
    STATUS_LOCKED = "locked"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_PROPOSED, "Proposed"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_LOCKED, "Locked"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="territories_quotaplans")
    territory = models.ForeignKey(
        "territories.Territory", on_delete=models.SET_NULL,
        related_name="quota_plans", null=True, blank=True)
    number = models.CharField(max_length=20, blank=True)
    name = models.CharField(max_length=150)
    period_type = models.CharField(max_length=20, choices=PERIOD_CHOICES, default=PERIOD_QUARTERLY)
    fiscal_year = models.PositiveIntegerField(default=_current_year)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    target_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    stretch_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fiscal_year", "-id"]
        unique_together = ("tenant", "number")
        indexes = [
            models.Index(fields=["tenant", "status"], name="qp_tenant_status_idx"),
            models.Index(fields=["tenant", "territory"], name="qp_tenant_territory_idx"),
            models.Index(fields=["tenant", "fiscal_year"], name="qp_tenant_fy_idx"),
        ]

    def __str__(self):
        return self.number or self.name

    def save(self, *args, **kwargs):
        if not self.number and self.tenant_id:
            # Per-tenant sequence with a row lock to avoid a TOCTOU race on
            # concurrent creates colliding on unique_together ('tenant', 'number').
            with transaction.atomic():
                last = (QuotaPlan.objects.select_for_update()
                        .filter(tenant_id=self.tenant_id, number__startswith="QP-")
                        .order_by("-number").first())
                seq = 1
                if last and last.number:
                    try:
                        seq = int(last.number.split("-")[1]) + 1
                    except (IndexError, ValueError):
                        seq = QuotaPlan.objects.filter(tenant_id=self.tenant_id).count() + 1
                self.number = f"QP-{seq:05d}"
        if self.status == self.STATUS_APPROVED and self.approved_at is None:
            self.approved_at = timezone.now()
        super().save(*args, **kwargs)


class CoverageModel(models.Model):
    """Coverage Model Optimization — a coverage strategy/scenario for the org."""

    MODEL_DIRECT = "direct"
    MODEL_INSIDE = "inside"
    MODEL_HYBRID = "hybrid"
    MODEL_PARTNER = "partner"
    MODEL_POD = "pod"
    MODEL_CHOICES = [
        (MODEL_DIRECT, "Direct field"),
        (MODEL_INSIDE, "Inside sales"),
        (MODEL_HYBRID, "Hybrid"),
        (MODEL_PARTNER, "Partner / channel"),
        (MODEL_POD, "Pod / team-based"),
    ]

    STATUS_PROPOSED = "proposed"
    STATUS_PILOT = "pilot"
    STATUS_ADOPTED = "adopted"
    STATUS_RETIRED = "retired"
    STATUS_CHOICES = [
        (STATUS_PROPOSED, "Proposed"),
        (STATUS_PILOT, "Pilot"),
        (STATUS_ADOPTED, "Adopted"),
        (STATUS_RETIRED, "Retired"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="territories_coveragemodels")
    name = models.CharField(max_length=150)
    model_type = models.CharField(max_length=20, choices=MODEL_CHOICES, default=MODEL_DIRECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PROPOSED)
    target_ratio = models.DecimalField(
        max_digits=6, decimal_places=2, default=0,
        help_text="Accounts per rep (coverage ratio).")
    rep_capacity = models.PositiveIntegerField(default=0)
    coverage_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name", "-id"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="cm_tenant_status_idx"),
            models.Index(fields=["tenant", "model_type"], name="cm_tenant_type_idx"),
        ]

    def __str__(self):
        return self.name


class TerritoryPerformance(models.Model):
    """Territory Performance Analytics — an attainment snapshot for a territory."""

    PERIOD_MONTHLY = "monthly"
    PERIOD_QUARTERLY = "quarterly"
    PERIOD_ANNUAL = "annual"
    PERIOD_CHOICES = [
        (PERIOD_MONTHLY, "Monthly"),
        (PERIOD_QUARTERLY, "Quarterly"),
        (PERIOD_ANNUAL, "Annual"),
    ]

    RATING_EXCEEDING = "exceeding"
    RATING_ON_TRACK = "on_track"
    RATING_AT_RISK = "at_risk"
    RATING_UNDERPERFORMING = "underperforming"
    RATING_CHOICES = [
        (RATING_EXCEEDING, "Exceeding"),
        (RATING_ON_TRACK, "On track"),
        (RATING_AT_RISK, "At risk"),
        (RATING_UNDERPERFORMING, "Underperforming"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="territories_territoryperformances")
    territory = models.ForeignKey(
        "territories.Territory", on_delete=models.CASCADE, related_name="performance_snapshots")
    period_type = models.CharField(max_length=20, choices=PERIOD_CHOICES, default=PERIOD_QUARTERLY)
    period_label = models.CharField(max_length=40, blank=True)
    rating = models.CharField(max_length=20, choices=RATING_CHOICES, default=RATING_ON_TRACK)
    quota_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    actual_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    attainment_percent = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    pipeline_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    deals_won = models.PositiveIntegerField(default=0)
    period_end = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-period_end", "-id"]
        indexes = [
            models.Index(fields=["tenant", "territory"], name="tp_tenant_territory_idx"),
            models.Index(fields=["tenant", "rating"], name="tp_tenant_rating_idx"),
            models.Index(fields=["tenant", "period_end"], name="tp_tenant_period_idx"),
        ]

    def __str__(self):
        return f"{self.territory.name} — {self.period_label or self.get_period_type_display()}"

    def save(self, *args, **kwargs):
        if self.quota_amount and self.quota_amount > 0:
            self.attainment_percent = (
                (self.actual_amount / self.quota_amount) * Decimal("100")
            ).quantize(Decimal("0.01"))
        super().save(*args, **kwargs)
