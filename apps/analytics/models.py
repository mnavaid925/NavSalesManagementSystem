from django.db import models
from django.utils import timezone


class WinLossAnalysis(models.Model):
    """Win/Loss Analysis — outcome review of a closed deal."""

    OUTCOME_WON = "won"
    OUTCOME_LOST = "lost"
    OUTCOME_NO_DECISION = "no_decision"
    OUTCOME_CHOICES = [
        (OUTCOME_WON, "Won"),
        (OUTCOME_LOST, "Lost"),
        (OUTCOME_NO_DECISION, "No decision"),
    ]

    REASON_PRICE = "price"
    REASON_PRODUCT = "product"
    REASON_RELATIONSHIP = "relationship"
    REASON_TIMING = "timing"
    REASON_FEATURES = "features"
    REASON_OTHER = "other"
    REASON_CATEGORY_CHOICES = [
        (REASON_PRICE, "Price"),
        (REASON_PRODUCT, "Product fit"),
        (REASON_RELATIONSHIP, "Relationship"),
        (REASON_TIMING, "Timing"),
        (REASON_FEATURES, "Features"),
        (REASON_OTHER, "Other"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="analytics_winlossanalysises")
    deal_name = models.CharField(max_length=150)
    rep_name = models.CharField(max_length=120)
    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES, default=OUTCOME_WON)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    competitor = models.CharField(max_length=120, blank=True)
    reason_category = models.CharField(
        max_length=20, choices=REASON_CATEGORY_CHOICES, default=REASON_PRICE)
    closed_on = models.DateField(default=timezone.localdate)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-closed_on", "-id"]
        indexes = [
            models.Index(fields=["tenant", "outcome"], name="wla_tenant_outcome_idx"),
            models.Index(fields=["tenant", "reason_category"], name="wla_tenant_reason_idx"),
            models.Index(fields=["tenant", "closed_on"], name="wla_tenant_closed_idx"),
        ]

    def __str__(self):
        return self.deal_name


class SalesVelocity(models.Model):
    """Sales Velocity & Cycle Time — pipeline throughput for a period/segment."""

    SEGMENT_ENTERPRISE = "enterprise"
    SEGMENT_MIDMARKET = "midmarket"
    SEGMENT_SMB = "smb"
    SEGMENT_ALL = "all"
    SEGMENT_CHOICES = [
        (SEGMENT_ENTERPRISE, "Enterprise"),
        (SEGMENT_MIDMARKET, "Mid-market"),
        (SEGMENT_SMB, "SMB"),
        (SEGMENT_ALL, "All segments"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="analytics_salesvelocitys")
    period_label = models.CharField(max_length=60)
    segment = models.CharField(max_length=20, choices=SEGMENT_CHOICES, default=SEGMENT_ALL)
    avg_deal_size = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    win_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sales_cycle_days = models.IntegerField(default=0)
    pipeline_value = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    velocity_score = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    recorded_on = models.DateField(default=timezone.localdate)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-recorded_on", "-id"]
        indexes = [
            models.Index(fields=["tenant", "segment"], name="sv_tenant_segment_idx"),
            models.Index(fields=["tenant", "recorded_on"], name="sv_tenant_recorded_idx"),
        ]

    def __str__(self):
        return self.period_label


class ConversionFunnel(models.Model):
    """Conversion Funnel Analytics — stage-level conversion for a period/segment."""

    SEGMENT_ENTERPRISE = "enterprise"
    SEGMENT_MIDMARKET = "midmarket"
    SEGMENT_SMB = "smb"
    SEGMENT_ALL = "all"
    SEGMENT_CHOICES = [
        (SEGMENT_ENTERPRISE, "Enterprise"),
        (SEGMENT_MIDMARKET, "Mid-market"),
        (SEGMENT_SMB, "SMB"),
        (SEGMENT_ALL, "All segments"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="analytics_conversionfunnels")
    stage_name = models.CharField(max_length=120)
    segment = models.CharField(max_length=20, choices=SEGMENT_CHOICES, default=SEGMENT_ALL)
    period_label = models.CharField(max_length=60)
    entered_count = models.IntegerField(default=0)
    converted_count = models.IntegerField(default=0)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    avg_days_in_stage = models.IntegerField(default=0)
    recorded_on = models.DateField(default=timezone.localdate)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-recorded_on", "-id"]
        indexes = [
            models.Index(fields=["tenant", "segment"], name="cf_tenant_segment_idx"),
            models.Index(fields=["tenant", "recorded_on"], name="cf_tenant_recorded_idx"),
        ]

    def __str__(self):
        return self.stage_name


class RepScorecard(models.Model):
    """Rep Performance Scorecards — period performance summary for a rep."""

    GRADE_A = "a"
    GRADE_B = "b"
    GRADE_C = "c"
    GRADE_D = "d"
    GRADE_CHOICES = [
        (GRADE_A, "A — Outstanding"),
        (GRADE_B, "B — Strong"),
        (GRADE_C, "C — Meets"),
        (GRADE_D, "D — Below"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="analytics_repscorecards")
    rep_name = models.CharField(max_length=120)
    period_label = models.CharField(max_length=60)
    quota = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    attainment = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    deals_won = models.IntegerField(default=0)
    deals_lost = models.IntegerField(default=0)
    activities = models.IntegerField(default=0)
    ranking = models.IntegerField(null=True, blank=True)
    grade = models.CharField(max_length=1, choices=GRADE_CHOICES, default=GRADE_C)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["ranking", "-attainment", "rep_name"]
        indexes = [
            models.Index(fields=["tenant", "grade"], name="rsc_tenant_grade_idx"),
            models.Index(fields=["tenant", "ranking"], name="rsc_tenant_ranking_idx"),
        ]

    def __str__(self):
        return f"{self.rep_name} — {self.period_label}"


class Benchmark(models.Model):
    """Benchmarking & Peer Comparison — our metric vs peer median / top quartile."""

    CATEGORY_WIN_RATE = "win_rate"
    CATEGORY_CYCLE_TIME = "cycle_time"
    CATEGORY_DEAL_SIZE = "deal_size"
    CATEGORY_QUOTA = "quota_attainment"
    CATEGORY_ACTIVITY = "activity"
    CATEGORY_CHOICES = [
        (CATEGORY_WIN_RATE, "Win rate"),
        (CATEGORY_CYCLE_TIME, "Cycle time"),
        (CATEGORY_DEAL_SIZE, "Deal size"),
        (CATEGORY_QUOTA, "Quota attainment"),
        (CATEGORY_ACTIVITY, "Activity"),
    ]

    STATUS_ABOVE = "above"
    STATUS_AT = "at"
    STATUS_BELOW = "below"
    STATUS_CHOICES = [
        (STATUS_ABOVE, "Above peers"),
        (STATUS_AT, "At par"),
        (STATUS_BELOW, "Below peers"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="analytics_benchmarks")
    metric_name = models.CharField(max_length=150)
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_WIN_RATE)
    our_value = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    peer_median = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    top_quartile = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    period_label = models.CharField(max_length=60)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_AT)
    recorded_on = models.DateField(default=timezone.localdate)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-recorded_on", "metric_name"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="bm_tenant_status_idx"),
            models.Index(fields=["tenant", "category"], name="bm_tenant_category_idx"),
            models.Index(fields=["tenant", "recorded_on"], name="bm_tenant_recorded_idx"),
        ]

    def __str__(self):
        return self.metric_name
