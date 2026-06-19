from django.db import models, transaction
from django.utils import timezone


class Contract(models.Model):
    """Subscription Lifecycle — a contract record (auto CTR-00001)."""

    TYPE_NEW = "new"
    TYPE_RENEWAL = "renewal"
    TYPE_AMENDMENT = "amendment"
    TYPE_NDA = "nda"
    TYPE_MSA = "msa"
    TYPE_SOW = "sow"
    TYPE_CHOICES = [
        (TYPE_NEW, "New business"),
        (TYPE_RENEWAL, "Renewal"),
        (TYPE_AMENDMENT, "Amendment"),
        (TYPE_NDA, "NDA"),
        (TYPE_MSA, "Master service agreement"),
        (TYPE_SOW, "Statement of work"),
    ]

    STATUS_DRAFT = "draft"
    STATUS_IN_REVIEW = "in_review"
    STATUS_SENT = "sent"
    STATUS_SIGNED = "signed"
    STATUS_ACTIVE = "active"
    STATUS_EXPIRED = "expired"
    STATUS_TERMINATED = "terminated"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_IN_REVIEW, "In review"),
        (STATUS_SENT, "Sent"),
        (STATUS_SIGNED, "Signed"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_EXPIRED, "Expired"),
        (STATUS_TERMINATED, "Terminated"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="contracts_contracts")
    number = models.CharField(max_length=20, blank=True)
    title = models.CharField(max_length=150)
    account_name = models.CharField(max_length=150)
    contract_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_NEW)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    value = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    start_date = models.DateField(default=timezone.localdate)
    end_date = models.DateField(null=True, blank=True)
    owner = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date", "-id"]
        unique_together = ("tenant", "number")
        indexes = [
            models.Index(fields=["tenant", "status"], name="ctr_tenant_status_idx"),
            models.Index(fields=["tenant", "contract_type"], name="ctr_tenant_type_idx"),
            models.Index(fields=["tenant", "start_date"], name="ctr_tenant_startdate_idx"),
        ]

    def __str__(self):
        return self.number or self.title

    def save(self, *args, **kwargs):
        if not self.number and self.tenant_id:
            # Per-tenant sequence with a row lock to avoid duplicate numbers under
            # concurrent creation (idempotent for seeds).
            with transaction.atomic():
                last = (Contract.objects.select_for_update()
                        .filter(tenant_id=self.tenant_id, number__startswith="CTR-")
                        .order_by("-number").first())
                seq = 1
                if last and last.number:
                    try:
                        seq = int(last.number.split("-")[1]) + 1
                    except (IndexError, ValueError):
                        seq = (Contract.objects
                               .filter(tenant_id=self.tenant_id, number__startswith="CTR-")
                               .count() + 1)
                self.number = f"CTR-{seq:05d}"
                super().save(*args, **kwargs)
                return
        super().save(*args, **kwargs)


class ContractClause(models.Model):
    """Contract Authoring & Redlining — a clause within a contract."""

    TYPE_PAYMENT = "payment"
    TYPE_LIABILITY = "liability"
    TYPE_TERMINATION = "termination"
    TYPE_SLA = "sla"
    TYPE_CONFIDENTIALITY = "confidentiality"
    TYPE_RENEWAL = "renewal"
    TYPE_IP = "ip"
    CLAUSE_TYPE_CHOICES = [
        (TYPE_PAYMENT, "Payment terms"),
        (TYPE_LIABILITY, "Liability"),
        (TYPE_TERMINATION, "Termination"),
        (TYPE_SLA, "Service level"),
        (TYPE_CONFIDENTIALITY, "Confidentiality"),
        (TYPE_RENEWAL, "Renewal"),
        (TYPE_IP, "Intellectual property"),
    ]

    STATUS_STANDARD = "standard"
    STATUS_REDLINED = "redlined"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_STANDARD, "Standard"),
        (STATUS_REDLINED, "Redlined"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    RISK_LOW = "low"
    RISK_MEDIUM = "medium"
    RISK_HIGH = "high"
    RISK_LEVEL_CHOICES = [
        (RISK_LOW, "Low"),
        (RISK_MEDIUM, "Medium"),
        (RISK_HIGH, "High"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="contracts_contractclauses")
    contract = models.ForeignKey(
        "contracts.Contract", on_delete=models.SET_NULL,
        related_name="clauses", null=True, blank=True)
    title = models.CharField(max_length=150)
    clause_type = models.CharField(max_length=20, choices=CLAUSE_TYPE_CHOICES, default=TYPE_PAYMENT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_STANDARD)
    risk_level = models.CharField(max_length=10, choices=RISK_LEVEL_CHOICES, default=RISK_LOW)
    body = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title", "-id"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="ccl_tenant_status_idx"),
            models.Index(fields=["tenant", "clause_type"], name="ccl_tenant_type_idx"),
            models.Index(fields=["tenant", "contract"], name="ccl_tenant_contract_idx"),
        ]

    def __str__(self):
        return self.title


class RenewalSchedule(models.Model):
    """Renewal Automation — a tracked renewal for an account/contract."""

    STATUS_UPCOMING = "upcoming"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_RENEWED = "renewed"
    STATUS_CHURNED = "churned"
    STATUS_AT_RISK = "at_risk"
    STATUS_CHOICES = [
        (STATUS_UPCOMING, "Upcoming"),
        (STATUS_IN_PROGRESS, "In progress"),
        (STATUS_RENEWED, "Renewed"),
        (STATUS_CHURNED, "Churned"),
        (STATUS_AT_RISK, "At risk"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="contracts_renewalschedules")
    contract = models.ForeignKey(
        "contracts.Contract", on_delete=models.SET_NULL,
        related_name="renewals", null=True, blank=True)
    account_name = models.CharField(max_length=150)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_UPCOMING)
    renewal_date = models.DateField(default=timezone.localdate)
    current_value = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    proposed_value = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    auto_renew = models.BooleanField(default=False)
    notice_days = models.IntegerField(default=30)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["renewal_date", "-id"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="rsc_tenant_status_idx"),
            models.Index(fields=["tenant", "renewal_date"], name="rsc_tenant_rendate_idx"),
            models.Index(fields=["tenant", "contract"], name="rsc_tenant_contract_idx"),
        ]

    def __str__(self):
        return self.account_name


class UsageRecord(models.Model):
    """Usage-Based Billing — a metered usage line for an account/contract."""

    UNIT_CALLS = "calls"
    UNIT_SEATS = "seats"
    UNIT_GB = "gb"
    UNIT_HOURS = "hours"
    UNIT_UNITS = "units"
    UNIT_CHOICES = [
        (UNIT_CALLS, "API calls"),
        (UNIT_SEATS, "Seats"),
        (UNIT_GB, "Gigabytes"),
        (UNIT_HOURS, "Hours"),
        (UNIT_UNITS, "Units"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="contracts_usagerecords")
    contract = models.ForeignKey(
        "contracts.Contract", on_delete=models.SET_NULL,
        related_name="usage_records", null=True, blank=True)
    account_name = models.CharField(max_length=150)
    metric_name = models.CharField(max_length=120)
    quantity = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default=UNIT_UNITS)
    rate = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    period_label = models.CharField(max_length=60)
    recorded_on = models.DateField(default=timezone.localdate)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-recorded_on", "-id"]
        indexes = [
            models.Index(fields=["tenant", "unit"], name="usg_tenant_unit_idx"),
            models.Index(fields=["tenant", "recorded_on"], name="usg_tenant_recdate_idx"),
            models.Index(fields=["tenant", "contract"], name="usg_tenant_contract_idx"),
        ]

    def __str__(self):
        return f"{self.metric_name} — {self.account_name}"


class ContractObligation(models.Model):
    """Contract Compliance & Obligations — a tracked obligation for a contract."""

    TYPE_DELIVERABLE = "deliverable"
    TYPE_PAYMENT = "payment"
    TYPE_REPORTING = "reporting"
    TYPE_SLA = "sla"
    TYPE_COMPLIANCE = "compliance"
    TYPE_RENEWAL_NOTICE = "renewal_notice"
    OBLIGATION_TYPE_CHOICES = [
        (TYPE_DELIVERABLE, "Deliverable"),
        (TYPE_PAYMENT, "Payment"),
        (TYPE_REPORTING, "Reporting"),
        (TYPE_SLA, "Service level"),
        (TYPE_COMPLIANCE, "Compliance"),
        (TYPE_RENEWAL_NOTICE, "Renewal notice"),
    ]

    STATUS_PENDING = "pending"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_MET = "met"
    STATUS_MISSED = "missed"
    STATUS_WAIVED = "waived"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_IN_PROGRESS, "In progress"),
        (STATUS_MET, "Met"),
        (STATUS_MISSED, "Missed"),
        (STATUS_WAIVED, "Waived"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="contracts_contractobligations")
    contract = models.ForeignKey(
        "contracts.Contract", on_delete=models.SET_NULL,
        related_name="obligations", null=True, blank=True)
    title = models.CharField(max_length=150)
    obligation_type = models.CharField(
        max_length=20, choices=OBLIGATION_TYPE_CHOICES, default=TYPE_DELIVERABLE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    due_date = models.DateField(default=timezone.localdate)
    owner = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due_date", "-id"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="cob_tenant_status_idx"),
            models.Index(fields=["tenant", "obligation_type"], name="cob_tenant_type_idx"),
            models.Index(fields=["tenant", "contract"], name="cob_tenant_contract_idx"),
        ]

    def __str__(self):
        return self.title
