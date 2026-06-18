from django.db import models, transaction
from django.utils import timezone


class CommissionPlan(models.Model):
    """Commission Plan Design — an incentive plan a rep can be enrolled on."""

    TYPE_FLAT = "flat"
    TYPE_TIERED = "tiered"
    TYPE_ACCELERATOR = "accelerator"
    TYPE_BONUS = "bonus"
    TYPE_CHOICES = [
        (TYPE_FLAT, "Flat rate"),
        (TYPE_TIERED, "Tiered"),
        (TYPE_ACCELERATOR, "Accelerator"),
        (TYPE_BONUS, "Bonus / SPIFF"),
    ]

    STATUS_DRAFT = "draft"
    STATUS_ACTIVE = "active"
    STATUS_PAUSED = "paused"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_PAUSED, "Paused"),
        (STATUS_ARCHIVED, "Archived"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="compensation_commissionplans")
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=40, blank=True)
    plan_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_FLAT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    base_rate = models.DecimalField(max_digits=6, decimal_places=2, default=0,
                                    help_text="Commission rate as a percentage, e.g. 5.00 for 5%.")
    target_quota = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    effective_from = models.DateField(default=timezone.localdate)
    effective_to = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-effective_from", "name"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="cplan_tenant_status_idx"),
            models.Index(fields=["tenant", "plan_type"], name="cplan_tenant_type_idx"),
            models.Index(fields=["tenant", "effective_from"], name="cplan_tenant_effdate_idx"),
        ]

    def __str__(self):
        return self.name


class Earning(models.Model):
    """Real-Time Earnings Tracking — commission accrued by a rep (auto EARN-00001)."""

    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_PAID = "paid"
    STATUS_DISPUTED = "disputed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_PAID, "Paid"),
        (STATUS_DISPUTED, "Disputed"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="compensation_earnings")
    plan = models.ForeignKey(
        "compensation.CommissionPlan", on_delete=models.SET_NULL,
        related_name="earnings", null=True, blank=True)
    number = models.CharField(max_length=20, blank=True)
    rep_name = models.CharField(max_length=150)
    deal_reference = models.CharField(max_length=120, blank=True)
    deal_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    earned_on = models.DateField(default=timezone.localdate)
    approved_at = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-earned_on", "-id"]
        unique_together = ("tenant", "number")
        indexes = [
            models.Index(fields=["tenant", "status"], name="earn_tenant_status_idx"),
            models.Index(fields=["tenant", "plan"], name="earn_tenant_plan_idx"),
            models.Index(fields=["tenant", "earned_on"], name="earn_tenant_earndate_idx"),
        ]

    def __str__(self):
        return self.number or f"Earning #{self.pk}"

    def save(self, *args, **kwargs):
        if not self.number and self.tenant_id:
            # Per-tenant sequence with a row lock to avoid duplicate numbers under
            # concurrent creation (idempotent for seeds).
            with transaction.atomic():
                last = (Earning.objects.select_for_update()
                        .filter(tenant_id=self.tenant_id, number__startswith="EARN-")
                        .order_by("-number").first())
                seq = 1
                if last and last.number:
                    try:
                        seq = int(last.number.split("-")[1]) + 1
                    except (IndexError, ValueError):
                        seq = (Earning.objects
                               .filter(tenant_id=self.tenant_id, number__startswith="EARN-")
                               .count() + 1)
                self.number = f"EARN-{seq:05d}"
                if self.status in (self.STATUS_APPROVED, self.STATUS_PAID) and self.approved_at is None:
                    self.approved_at = timezone.now()
                if self.status not in (self.STATUS_APPROVED, self.STATUS_PAID):
                    self.approved_at = None
                super().save(*args, **kwargs)
                return
        if self.status in (self.STATUS_APPROVED, self.STATUS_PAID) and self.approved_at is None:
            self.approved_at = timezone.now()
        if self.status not in (self.STATUS_APPROVED, self.STATUS_PAID):
            self.approved_at = None
        super().save(*args, **kwargs)


class Clawback(models.Model):
    """Clawbacks & Adjustments — a reversal/adjustment against an earning."""

    REASON_CANCELLATION = "cancellation"
    REASON_REFUND = "refund"
    REASON_CHARGEBACK = "chargeback"
    REASON_CORRECTION = "correction"
    REASON_OTHER = "other"
    REASON_CHOICES = [
        (REASON_CANCELLATION, "Deal cancellation"),
        (REASON_REFUND, "Customer refund"),
        (REASON_CHARGEBACK, "Chargeback"),
        (REASON_CORRECTION, "Data correction"),
        (REASON_OTHER, "Other"),
    ]

    STATUS_OPEN = "open"
    STATUS_APPLIED = "applied"
    STATUS_WAIVED = "waived"
    STATUS_DISPUTED = "disputed"
    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_APPLIED, "Applied"),
        (STATUS_WAIVED, "Waived"),
        (STATUS_DISPUTED, "Disputed"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="compensation_clawbacks")
    earning = models.ForeignKey(
        "compensation.Earning", on_delete=models.CASCADE,
        related_name="clawbacks", null=True, blank=True)
    rep_name = models.CharField(max_length=150)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, default=REASON_CANCELLATION)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    effective_on = models.DateField(default=timezone.localdate)
    applied_at = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-effective_on", "-id"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="claw_tenant_status_idx"),
            models.Index(fields=["tenant", "reason"], name="claw_tenant_reason_idx"),
            models.Index(fields=["tenant", "effective_on"], name="claw_tenant_effdate_idx"),
        ]

    def __str__(self):
        return f"{self.get_reason_display()} — {self.rep_name}"

    def save(self, *args, **kwargs):
        if self.status == self.STATUS_APPLIED and self.applied_at is None:
            self.applied_at = timezone.now()
        if self.status != self.STATUS_APPLIED:
            self.applied_at = None
        super().save(*args, **kwargs)


class GlobalPlanVariation(models.Model):
    """Multi-Currency & Global Plans — a regional/currency variation of a plan."""

    CURRENCY_USD = "USD"
    CURRENCY_EUR = "EUR"
    CURRENCY_GBP = "GBP"
    CURRENCY_JPY = "JPY"
    CURRENCY_AUD = "AUD"
    CURRENCY_CAD = "CAD"
    CURRENCY_INR = "INR"
    CURRENCY_CHOICES = [
        (CURRENCY_USD, "US Dollar (USD)"),
        (CURRENCY_EUR, "Euro (EUR)"),
        (CURRENCY_GBP, "British Pound (GBP)"),
        (CURRENCY_JPY, "Japanese Yen (JPY)"),
        (CURRENCY_AUD, "Australian Dollar (AUD)"),
        (CURRENCY_CAD, "Canadian Dollar (CAD)"),
        (CURRENCY_INR, "Indian Rupee (INR)"),
    ]

    STATUS_ACTIVE = "active"
    STATUS_PENDING = "pending"
    STATUS_RETIRED = "retired"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_PENDING, "Pending"),
        (STATUS_RETIRED, "Retired"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="compensation_globalplanvariations")
    plan = models.ForeignKey(
        "compensation.CommissionPlan", on_delete=models.CASCADE,
        related_name="variations", null=True, blank=True)
    region = models.CharField(max_length=120)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default=CURRENCY_USD)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    fx_rate = models.DecimalField(max_digits=12, decimal_places=6, default=1,
                                  help_text="Exchange rate to the base (USD) currency.")
    local_quota = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    rate_adjustment = models.DecimalField(max_digits=6, decimal_places=2, default=0,
                                          help_text="Percentage point adjustment to the base rate.")
    effective_from = models.DateField(default=timezone.localdate)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["region", "currency"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="gpv_tenant_status_idx"),
            models.Index(fields=["tenant", "currency"], name="gpv_tenant_currency_idx"),
            models.Index(fields=["tenant", "plan"], name="gpv_tenant_plan_idx"),
        ]

    def __str__(self):
        return f"{self.region} ({self.currency})"


class Payout(models.Model):
    """Payout Processing & Integration — a compensation run to payroll (auto PAY-00001)."""

    METHOD_PAYROLL = "payroll"
    METHOD_BANK = "bank_transfer"
    METHOD_CHECK = "check"
    METHOD_WALLET = "wallet"
    METHOD_CHOICES = [
        (METHOD_PAYROLL, "Payroll system"),
        (METHOD_BANK, "Bank transfer"),
        (METHOD_CHECK, "Check"),
        (METHOD_WALLET, "Digital wallet"),
    ]

    STATUS_SCHEDULED = "scheduled"
    STATUS_PROCESSING = "processing"
    STATUS_PAID = "paid"
    STATUS_FAILED = "failed"
    STATUS_CANCELED = "canceled"
    STATUS_CHOICES = [
        (STATUS_SCHEDULED, "Scheduled"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_PAID, "Paid"),
        (STATUS_FAILED, "Failed"),
        (STATUS_CANCELED, "Canceled"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="compensation_payouts")
    number = models.CharField(max_length=20, blank=True)
    rep_name = models.CharField(max_length=150)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default=METHOD_PAYROLL)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SCHEDULED)
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    period_label = models.CharField(max_length=60, blank=True)
    scheduled_on = models.DateField(default=timezone.localdate)
    paid_at = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    reference = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-scheduled_on", "-id"]
        unique_together = ("tenant", "number")
        indexes = [
            models.Index(fields=["tenant", "status"], name="pay_tenant_status_idx"),
            models.Index(fields=["tenant", "method"], name="pay_tenant_method_idx"),
            models.Index(fields=["tenant", "scheduled_on"], name="pay_tenant_scheddate_idx"),
        ]

    def __str__(self):
        return self.number or f"Payout #{self.pk}"

    def save(self, *args, **kwargs):
        if not self.number and self.tenant_id:
            # Per-tenant sequence with a row lock to avoid duplicate numbers under
            # concurrent creation (idempotent for seeds).
            with transaction.atomic():
                last = (Payout.objects.select_for_update()
                        .filter(tenant_id=self.tenant_id, number__startswith="PAY-")
                        .order_by("-number").first())
                seq = 1
                if last and last.number:
                    try:
                        seq = int(last.number.split("-")[1]) + 1
                    except (IndexError, ValueError):
                        seq = (Payout.objects
                               .filter(tenant_id=self.tenant_id, number__startswith="PAY-")
                               .count() + 1)
                self.number = f"PAY-{seq:05d}"
                if self.status == self.STATUS_PAID and self.paid_at is None:
                    self.paid_at = timezone.now()
                super().save(*args, **kwargs)
                return
        if self.status == self.STATUS_PAID and self.paid_at is None:
            self.paid_at = timezone.now()
        super().save(*args, **kwargs)
