from django.db import models
from django.utils import timezone


def _current_year():
    """Callable default so the fiscal year is resolved at row-creation time."""
    return timezone.localdate().year


class AccountTier(models.Model):
    """Account Segmentation & Tiering — a named tier/segment definition.

    Drives how accounts are grouped (Strategic, Enterprise, SMB...). Accounts FK
    here so each account can be classified by tier within this same app.
    """

    SEGMENT_STRATEGIC = "strategic"
    SEGMENT_ENTERPRISE = "enterprise"
    SEGMENT_MIDMARKET = "mid_market"
    SEGMENT_SMB = "smb"
    SEGMENT_STARTUP = "startup"
    SEGMENT_CHOICES = [
        (SEGMENT_STRATEGIC, "Strategic"),
        (SEGMENT_ENTERPRISE, "Enterprise"),
        (SEGMENT_MIDMARKET, "Mid-Market"),
        (SEGMENT_SMB, "SMB"),
        (SEGMENT_STARTUP, "Startup"),
    ]

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, related_name="crm_accounttiers")
    name = models.CharField(max_length=120)
    segment = models.CharField(max_length=20, choices=SEGMENT_CHOICES, default=SEGMENT_MIDMARKET)
    rank = models.PositiveIntegerField(default=0, help_text="Lower ranks sort first (Tier 1 = 1).")
    min_annual_value = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    color = models.CharField(max_length=9, default="#2563eb")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["rank", "name"]
        indexes = [
            models.Index(fields=["tenant", "segment"], name="crm_tier_tenant_segment_idx"),
        ]

    def __str__(self):
        return self.name


class Account(models.Model):
    """Account Hierarchy & Parent-Child — a company/organisation record.

    Self-references via `parent` to model corporate hierarchies (HQ -> subsidiary).
    Auto-numbered per tenant (ACC-00001) like Invoice.save().
    """

    TYPE_PROSPECT = "prospect"
    TYPE_CUSTOMER = "customer"
    TYPE_PARTNER = "partner"
    TYPE_RESELLER = "reseller"
    TYPE_COMPETITOR = "competitor"
    TYPE_CHOICES = [
        (TYPE_PROSPECT, "Prospect"),
        (TYPE_CUSTOMER, "Customer"),
        (TYPE_PARTNER, "Partner"),
        (TYPE_RESELLER, "Reseller"),
        (TYPE_COMPETITOR, "Competitor"),
    ]

    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_CHURNED = "churned"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_INACTIVE, "Inactive"),
        (STATUS_CHURNED, "Churned"),
    ]

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, related_name="crm_accounts")
    parent = models.ForeignKey(
        "crm.Account", on_delete=models.SET_NULL,
        related_name="children", null=True, blank=True,
    )
    tier = models.ForeignKey(
        "crm.AccountTier", on_delete=models.SET_NULL,
        related_name="accounts", null=True, blank=True,
    )
    number = models.CharField(max_length=20, blank=True)
    name = models.CharField(max_length=160)
    account_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_PROSPECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    industry = models.CharField(max_length=120, blank=True)
    website = models.URLField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    billing_city = models.CharField(max_length=120, blank=True)
    billing_country = models.CharField(max_length=120, blank=True)
    employee_count = models.PositiveIntegerField(null=True, blank=True)
    annual_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name", "-id"]
        unique_together = ("tenant", "number")
        indexes = [
            models.Index(fields=["tenant", "status"], name="crm_acct_tenant_status_idx"),
            models.Index(fields=["tenant", "account_type"], name="crm_acct_tenant_type_idx"),
            models.Index(fields=["tenant", "tier"], name="crm_acct_tenant_tier_idx"),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.number and self.tenant_id:
            # Per-tenant sequence with an existence guard (idempotent for seeds).
            last = (Account.objects.filter(tenant_id=self.tenant_id, number__startswith="ACC-")
                    .order_by("-number").first())
            seq = 1
            if last and last.number:
                try:
                    seq = int(last.number.split("-")[1]) + 1
                except (IndexError, ValueError):
                    seq = Account.objects.filter(tenant_id=self.tenant_id).count() + 1
            self.number = f"ACC-{seq:05d}"
        super().save(*args, **kwargs)


class Contact(models.Model):
    """Contact Profiles & Enrichment — an individual person at an account."""

    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_BOUNCED = "bounced"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_INACTIVE, "Inactive"),
        (STATUS_BOUNCED, "Bounced"),
    ]

    ENRICH_NONE = "none"
    ENRICH_PARTIAL = "partial"
    ENRICH_VERIFIED = "verified"
    ENRICH_CHOICES = [
        (ENRICH_NONE, "Not enriched"),
        (ENRICH_PARTIAL, "Partial"),
        (ENRICH_VERIFIED, "Verified"),
    ]

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, related_name="crm_contacts")
    account = models.ForeignKey(
        "crm.Account", on_delete=models.CASCADE,
        related_name="contacts", null=True, blank=True,
    )
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    title = models.CharField(max_length=120, blank=True)
    department = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    mobile = models.CharField(max_length=40, blank=True)
    linkedin_url = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    enrichment_status = models.CharField(max_length=20, choices=ENRICH_CHOICES, default=ENRICH_NONE)
    is_primary = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name", "-id"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="crm_contact_tenant_status_idx"),
            models.Index(fields=["tenant", "account"], name="crm_contact_tenant_account_idx"),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class RelationshipMap(models.Model):
    """Relationship Mapping — a directed relationship between two contacts.

    Captures org-chart and influence links (reports-to, influences, sponsors...)
    so reps can navigate the buying committee.
    """

    TYPE_REPORTS_TO = "reports_to"
    TYPE_INFLUENCES = "influences"
    TYPE_SPONSOR = "sponsor"
    TYPE_BLOCKER = "blocker"
    TYPE_PEER = "peer"
    TYPE_CHOICES = [
        (TYPE_REPORTS_TO, "Reports to"),
        (TYPE_INFLUENCES, "Influences"),
        (TYPE_SPONSOR, "Sponsor"),
        (TYPE_BLOCKER, "Blocker"),
        (TYPE_PEER, "Peer"),
    ]

    STRENGTH_STRONG = "strong"
    STRENGTH_MODERATE = "moderate"
    STRENGTH_WEAK = "weak"
    STRENGTH_CHOICES = [
        (STRENGTH_STRONG, "Strong"),
        (STRENGTH_MODERATE, "Moderate"),
        (STRENGTH_WEAK, "Weak"),
    ]

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, related_name="crm_relationshipmaps")
    account = models.ForeignKey(
        "crm.Account", on_delete=models.CASCADE,
        related_name="relationship_maps", null=True, blank=True,
    )
    from_contact = models.ForeignKey(
        "crm.Contact", on_delete=models.CASCADE,
        related_name="relationships_from",
    )
    to_contact = models.ForeignKey(
        "crm.Contact", on_delete=models.CASCADE,
        related_name="relationships_to",
    )
    relationship_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_REPORTS_TO)
    strength = models.CharField(max_length=20, choices=STRENGTH_CHOICES, default=STRENGTH_MODERATE)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["tenant", "account"], name="crm_relmap_tenant_account_idx"),
            models.Index(fields=["tenant", "relationship_type"], name="crm_relmap_tenant_type_idx"),
        ]

    def __str__(self):
        return f"{self.from_contact} → {self.to_contact} ({self.get_relationship_type_display()})"


class AccountPlan(models.Model):
    """Account Plans & Growth Strategies — a strategic plan for an account.

    Auto-numbered per tenant (PLAN-00001). `approved_at` is system-set when the
    plan moves to approved/active and is kept off the form.
    """

    STATUS_DRAFT = "draft"
    STATUS_ACTIVE = "active"
    STATUS_ON_TRACK = "on_track"
    STATUS_AT_RISK = "at_risk"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_ON_TRACK, "On track"),
        (STATUS_AT_RISK, "At risk"),
        (STATUS_COMPLETED, "Completed"),
    ]

    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, "Low"),
        (PRIORITY_MEDIUM, "Medium"),
        (PRIORITY_HIGH, "High"),
    ]

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, related_name="crm_accountplans")
    account = models.ForeignKey(
        "crm.Account", on_delete=models.CASCADE,
        related_name="account_plans",
    )
    number = models.CharField(max_length=20, blank=True)
    title = models.CharField(max_length=160)
    fiscal_year = models.PositiveIntegerField(default=_current_year)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    objective = models.TextField(blank=True)
    growth_strategy = models.TextField(blank=True)
    target_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    current_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fiscal_year", "-id"]
        unique_together = ("tenant", "number")
        indexes = [
            models.Index(fields=["tenant", "status"], name="crm_plan_tenant_status_idx"),
            models.Index(fields=["tenant", "account"], name="crm_plan_tenant_account_idx"),
        ]

    def __str__(self):
        return self.number or self.title

    def save(self, *args, **kwargs):
        if not self.number and self.tenant_id:
            # Per-tenant sequence with an existence guard (idempotent for seeds).
            last = (AccountPlan.objects.filter(tenant_id=self.tenant_id, number__startswith="PLAN-")
                    .order_by("-number").first())
            seq = 1
            if last and last.number:
                try:
                    seq = int(last.number.split("-")[1]) + 1
                except (IndexError, ValueError):
                    seq = AccountPlan.objects.filter(tenant_id=self.tenant_id).count() + 1
            self.number = f"PLAN-{seq:05d}"
        if self.status in (self.STATUS_ACTIVE, self.STATUS_ON_TRACK, self.STATUS_COMPLETED) and self.approved_at is None:
            self.approved_at = timezone.now()
        super().save(*args, **kwargs)
