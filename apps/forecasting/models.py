from django.db import models
from django.utils import timezone


class ForecastCategory(models.Model):
    """Forecast Categories & Commitments — a commitment bucket (Pipeline, Best Case,
    Commit, Closed) deals roll up into, with its own weighting and probability."""

    COMMIT_OMITTED = "omitted"
    COMMIT_PIPELINE = "pipeline"
    COMMIT_BEST_CASE = "best_case"
    COMMIT_COMMIT = "commit"
    COMMIT_CLOSED = "closed"
    COMMIT_CHOICES = [
        (COMMIT_OMITTED, "Omitted"),
        (COMMIT_PIPELINE, "Pipeline"),
        (COMMIT_BEST_CASE, "Best Case"),
        (COMMIT_COMMIT, "Commit"),
        (COMMIT_CLOSED, "Closed"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="forecasting_forecastcategorys")
    name = models.CharField(max_length=120)
    commitment = models.CharField(max_length=20, choices=COMMIT_CHOICES, default=COMMIT_PIPELINE)
    probability = models.PositiveIntegerField(default=50, help_text="Default win probability (%) for this category.")
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=1,
                                 help_text="Roll-up weighting multiplier.")
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Forecast(models.Model):
    """AI-Powered Predictive Forecasting — a period forecast snapshot (auto-numbered
    FCT-00001) with a submitted commit number and an AI-predicted number."""

    PERIOD_MONTH = "month"
    PERIOD_QUARTER = "quarter"
    PERIOD_YEAR = "year"
    PERIOD_CHOICES = [
        (PERIOD_MONTH, "Monthly"),
        (PERIOD_QUARTER, "Quarterly"),
        (PERIOD_YEAR, "Annual"),
    ]

    STATUS_DRAFT = "draft"
    STATUS_SUBMITTED = "submitted"
    STATUS_APPROVED = "approved"
    STATUS_CLOSED = "closed"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_SUBMITTED, "Submitted"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_CLOSED, "Closed"),
    ]

    CONFIDENCE_LOW = "low"
    CONFIDENCE_MEDIUM = "medium"
    CONFIDENCE_HIGH = "high"
    CONFIDENCE_CHOICES = [
        (CONFIDENCE_LOW, "Low"),
        (CONFIDENCE_MEDIUM, "Medium"),
        (CONFIDENCE_HIGH, "High"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="forecasting_forecasts")
    category = models.ForeignKey(
        "forecasting.ForecastCategory", on_delete=models.SET_NULL,
        related_name="forecasts", null=True, blank=True)
    number = models.CharField(max_length=20, blank=True)
    name = models.CharField(max_length=150)
    owner_name = models.CharField(max_length=120, blank=True, help_text="Rep or team this forecast belongs to.")
    period_type = models.CharField(max_length=20, choices=PERIOD_CHOICES, default=PERIOD_QUARTER)
    period_label = models.CharField(max_length=40, blank=True, help_text="e.g. Q3 2026.")
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)
    pipeline_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    commit_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0,
                                        help_text="Number the owner is committing to.")
    best_case_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    ai_predicted_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0,
                                              help_text="AI/ML predicted close number.")
    ai_confidence = models.CharField(max_length=10, choices=CONFIDENCE_CHOICES, default=CONFIDENCE_MEDIUM)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    submitted_at = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-period_start", "-id"]
        unique_together = ("tenant", "number")

    def __str__(self):
        return self.number or self.name

    def save(self, *args, **kwargs):
        if not self.number and self.tenant_id:
            # Per-tenant sequence with an existence guard (idempotent for seeds).
            last = (Forecast.objects.filter(tenant_id=self.tenant_id, number__startswith="FCT-")
                    .order_by("-number").first())
            seq = 1
            if last and last.number:
                try:
                    seq = int(last.number.split("-")[1]) + 1
                except (IndexError, ValueError):
                    seq = Forecast.objects.filter(tenant_id=self.tenant_id).count() + 1
            self.number = f"FCT-{seq:05d}"
        if self.status == self.STATUS_SUBMITTED and self.submitted_at is None:
            self.submitted_at = timezone.now()
        super().save(*args, **kwargs)


class Quota(models.Model):
    """Quota Management & Attainment — a target assigned to a rep/team for a period,
    with the closed-to-date attained amount tracked against it."""

    PERIOD_MONTH = "month"
    PERIOD_QUARTER = "quarter"
    PERIOD_YEAR = "year"
    PERIOD_CHOICES = [
        (PERIOD_MONTH, "Monthly"),
        (PERIOD_QUARTER, "Quarterly"),
        (PERIOD_YEAR, "Annual"),
    ]

    STATUS_ACTIVE = "active"
    STATUS_ACHIEVED = "achieved"
    STATUS_MISSED = "missed"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_ACHIEVED, "Achieved"),
        (STATUS_MISSED, "Missed"),
        (STATUS_ARCHIVED, "Archived"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="forecasting_quotas")
    owner_name = models.CharField(max_length=120, help_text="Rep or team the quota is assigned to.")
    period_type = models.CharField(max_length=20, choices=PERIOD_CHOICES, default=PERIOD_QUARTER)
    period_label = models.CharField(max_length=40, blank=True, help_text="e.g. Q3 2026.")
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)
    target_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    attained_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0,
                                          help_text="Closed-won to date against this quota.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-period_start", "owner_name"]

    def __str__(self):
        return f"{self.owner_name} — {self.period_label or self.get_period_type_display()}"

    @property
    def attainment_pct(self):
        if self.target_amount and self.target_amount > 0:
            return round((self.attained_amount / self.target_amount) * 100, 1)
        return 0


class ForecastAdjustment(models.Model):
    """Forecast Rollups & Adjustments — a manager override applied on top of a parent
    forecast (FK to Forecast in this same app)."""

    TYPE_UPLIFT = "uplift"
    TYPE_HAIRCUT = "haircut"
    TYPE_OVERRIDE = "override"
    TYPE_ROLLUP = "rollup"
    TYPE_CHOICES = [
        (TYPE_UPLIFT, "Uplift"),
        (TYPE_HAIRCUT, "Haircut"),
        (TYPE_OVERRIDE, "Override"),
        (TYPE_ROLLUP, "Roll-up"),
    ]

    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="forecasting_forecastadjustments")
    forecast = models.ForeignKey(
        "forecasting.Forecast", on_delete=models.CASCADE, related_name="adjustments")
    adjustment_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_UPLIFT)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0,
                                 help_text="Signed delta applied to the forecast number.")
    adjusted_by = models.CharField(max_length=120, blank=True, help_text="Manager who made the adjustment.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    reason = models.TextField(blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_adjustment_type_display()} ({self.amount})"

    def save(self, *args, **kwargs):
        if self.status == self.STATUS_APPROVED and self.approved_at is None:
            self.approved_at = timezone.now()
        if self.status != self.STATUS_APPROVED:
            self.approved_at = None
        super().save(*args, **kwargs)


class ForecastAccuracy(models.Model):
    """Forecast Accuracy & Variance Analysis — the post-period scorecard comparing a
    forecasted number against the actual closed number."""

    GRADE_EXCELLENT = "excellent"
    GRADE_GOOD = "good"
    GRADE_FAIR = "fair"
    GRADE_POOR = "poor"
    GRADE_CHOICES = [
        (GRADE_EXCELLENT, "Excellent"),
        (GRADE_GOOD, "Good"),
        (GRADE_FAIR, "Fair"),
        (GRADE_POOR, "Poor"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="forecasting_forecastaccuracys")
    forecast = models.ForeignKey(
        "forecasting.Forecast", on_delete=models.SET_NULL,
        related_name="accuracy_records", null=True, blank=True)
    period_label = models.CharField(max_length=40, blank=True, help_text="e.g. Q2 2026.")
    forecasted_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    actual_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    variance_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0,
                                          help_text="Actual minus forecasted (system-computed).")
    accuracy_pct = models.DecimalField(max_digits=6, decimal_places=2, default=0,
                                       help_text="Accuracy score (%) for the period.")
    grade = models.CharField(max_length=20, choices=GRADE_CHOICES, default=GRADE_GOOD)
    analyzed_on = models.DateField(default=timezone.localdate)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-analyzed_on", "-id"]

    def __str__(self):
        return f"{self.period_label or 'Period'} — {self.accuracy_pct}%"

    def save(self, *args, **kwargs):
        # Variance is always derived in code (kept off the form).
        self.variance_amount = self.actual_amount - self.forecasted_amount
        super().save(*args, **kwargs)
