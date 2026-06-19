from django.db import models, transaction
from django.utils import timezone


class HealthScore(models.Model):
    """Health Scoring & Risk Alerts — an account's health score and churn risk."""

    RISK_LOW = "low"
    RISK_MEDIUM = "medium"
    RISK_HIGH = "high"
    RISK_CRITICAL = "critical"
    RISK_LEVEL_CHOICES = [
        (RISK_LOW, "Low"),
        (RISK_MEDIUM, "Medium"),
        (RISK_HIGH, "High"),
        (RISK_CRITICAL, "Critical"),
    ]

    TREND_IMPROVING = "improving"
    TREND_STABLE = "stable"
    TREND_DECLINING = "declining"
    TREND_CHOICES = [
        (TREND_IMPROVING, "Improving"),
        (TREND_STABLE, "Stable"),
        (TREND_DECLINING, "Declining"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="success_healthscores")
    account_name = models.CharField(max_length=150)
    owner = models.CharField(max_length=120, blank=True)
    score = models.IntegerField(default=50)
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, default=RISK_MEDIUM)
    trend = models.CharField(max_length=20, choices=TREND_CHOICES, default=TREND_STABLE)
    arr = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    last_reviewed = models.DateField(default=timezone.localdate)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_reviewed", "account_name"]
        indexes = [
            models.Index(fields=["tenant", "risk_level"], name="hs_tenant_risk_idx"),
            models.Index(fields=["tenant", "trend"], name="hs_tenant_trend_idx"),
            models.Index(fields=["tenant", "last_reviewed"], name="hs_tenant_reviewed_idx"),
        ]

    def __str__(self):
        return self.account_name


class Renewal(models.Model):
    """Renewal & Expansion Pipeline — a renewal/expansion opportunity (auto REN-00001)."""

    TYPE_RENEWAL = "renewal"
    TYPE_UPSELL = "upsell"
    TYPE_CROSS_SELL = "cross_sell"
    TYPE_EXPANSION = "expansion"
    RENEWAL_TYPE_CHOICES = [
        (TYPE_RENEWAL, "Renewal"),
        (TYPE_UPSELL, "Upsell"),
        (TYPE_CROSS_SELL, "Cross-sell"),
        (TYPE_EXPANSION, "Expansion"),
    ]

    STATUS_OPEN = "open"
    STATUS_AT_RISK = "at_risk"
    STATUS_COMMITTED = "committed"
    STATUS_WON = "won"
    STATUS_LOST = "lost"
    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_AT_RISK, "At risk"),
        (STATUS_COMMITTED, "Committed"),
        (STATUS_WON, "Won"),
        (STATUS_LOST, "Lost"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="success_renewals")
    number = models.CharField(max_length=20, blank=True)
    account_name = models.CharField(max_length=150)
    owner = models.CharField(max_length=120, blank=True)
    renewal_type = models.CharField(max_length=20, choices=RENEWAL_TYPE_CHOICES, default=TYPE_RENEWAL)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    arr_current = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    arr_proposed = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    probability = models.IntegerField(default=50)
    renewal_date = models.DateField(default=timezone.localdate)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-renewal_date", "-id"]
        unique_together = ("tenant", "number")
        indexes = [
            models.Index(fields=["tenant", "status"], name="ren_tenant_status_idx"),
            models.Index(fields=["tenant", "renewal_type"], name="ren_tenant_type_idx"),
            models.Index(fields=["tenant", "renewal_date"], name="ren_tenant_date_idx"),
        ]

    def __str__(self):
        return self.number or f"Renewal #{self.pk}"

    def save(self, *args, **kwargs):
        if not self.number and self.tenant_id:
            # Per-tenant sequence with a row lock to avoid duplicate numbers under
            # concurrent creation (idempotent for seeds).
            with transaction.atomic():
                last = (Renewal.objects.select_for_update()
                        .filter(tenant_id=self.tenant_id, number__startswith="REN-")
                        .order_by("-number").first())
                seq = 1
                if last and last.number:
                    try:
                        seq = int(last.number.split("-")[1]) + 1
                    except (IndexError, ValueError):
                        seq = (Renewal.objects
                               .filter(tenant_id=self.tenant_id, number__startswith="REN-")
                               .count() + 1)
                self.number = f"REN-{seq:05d}"
                super().save(*args, **kwargs)
                return
        super().save(*args, **kwargs)


class OnboardingPlan(models.Model):
    """Onboarding & Implementation — an account's onboarding/implementation plan."""

    STATUS_NOT_STARTED = "not_started"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_BLOCKED = "blocked"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = [
        (STATUS_NOT_STARTED, "Not started"),
        (STATUS_IN_PROGRESS, "In progress"),
        (STATUS_BLOCKED, "Blocked"),
        (STATUS_COMPLETED, "Completed"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="success_onboardingplans")
    account_name = models.CharField(max_length=150)
    plan_name = models.CharField(max_length=150)
    owner = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NOT_STARTED)
    progress_pct = models.IntegerField(default=0)
    start_date = models.DateField(default=timezone.localdate)
    target_go_live = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date", "account_name"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="onb_tenant_status_idx"),
            models.Index(fields=["tenant", "start_date"], name="onb_tenant_start_idx"),
        ]

    def __str__(self):
        return self.plan_name


class Advocacy(models.Model):
    """Advocacy & Reference Management — a customer advocate/reference record."""

    TYPE_REFERENCE = "reference"
    TYPE_CASE_STUDY = "case_study"
    TYPE_TESTIMONIAL = "testimonial"
    TYPE_REVIEW = "review"
    TYPE_SPEAKER = "speaker"
    ADVOCACY_TYPE_CHOICES = [
        (TYPE_REFERENCE, "Reference"),
        (TYPE_CASE_STUDY, "Case study"),
        (TYPE_TESTIMONIAL, "Testimonial"),
        (TYPE_REVIEW, "Review"),
        (TYPE_SPEAKER, "Speaker"),
    ]

    STATUS_NOMINATED = "nominated"
    STATUS_ACTIVE = "active"
    STATUS_DECLINED = "declined"
    STATUS_RETIRED = "retired"
    STATUS_CHOICES = [
        (STATUS_NOMINATED, "Nominated"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_DECLINED, "Declined"),
        (STATUS_RETIRED, "Retired"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="success_advocacies")
    account_name = models.CharField(max_length=150)
    contact_name = models.CharField(max_length=150)
    advocacy_type = models.CharField(max_length=20, choices=ADVOCACY_TYPE_CHOICES, default=TYPE_REFERENCE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NOMINATED)
    nps_score = models.IntegerField(null=True, blank=True)
    last_engaged = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Advocacies"
        ordering = ["account_name", "contact_name"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="adv_tenant_status_idx"),
            models.Index(fields=["tenant", "advocacy_type"], name="adv_tenant_type_idx"),
        ]

    def __str__(self):
        return f"{self.contact_name} ({self.account_name})"


class QBR(models.Model):
    """Quarterly Business Reviews — a scheduled/completed QBR for an account."""

    STATUS_SCHEDULED = "scheduled"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELED = "canceled"
    STATUS_CHOICES = [
        (STATUS_SCHEDULED, "Scheduled"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELED, "Canceled"),
    ]

    SENTIMENT_POSITIVE = "positive"
    SENTIMENT_NEUTRAL = "neutral"
    SENTIMENT_NEGATIVE = "negative"
    SENTIMENT_CHOICES = [
        (SENTIMENT_POSITIVE, "Positive"),
        (SENTIMENT_NEUTRAL, "Neutral"),
        (SENTIMENT_NEGATIVE, "Negative"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="success_qbrs")
    account_name = models.CharField(max_length=150)
    period_label = models.CharField(max_length=60)
    owner = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SCHEDULED)
    sentiment = models.CharField(max_length=20, choices=SENTIMENT_CHOICES, default=SENTIMENT_NEUTRAL)
    scheduled_on = models.DateField(default=timezone.localdate)
    health_summary = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "QBR"
        verbose_name_plural = "QBRs"
        ordering = ["-scheduled_on", "account_name"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="qbr_tenant_status_idx"),
            models.Index(fields=["tenant", "sentiment"], name="qbr_tenant_sentiment_idx"),
            models.Index(fields=["tenant", "scheduled_on"], name="qbr_tenant_sched_idx"),
        ]

    def __str__(self):
        return f"{self.account_name} — {self.period_label}"
