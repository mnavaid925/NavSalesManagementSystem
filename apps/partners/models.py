from django.db import models, transaction
from django.utils import timezone


class Partner(models.Model):
    """Partner Recruitment & Onboarding — a channel partner in the program."""

    TYPE_RESELLER = "reseller"
    TYPE_REFERRAL = "referral"
    TYPE_OEM = "oem"
    TYPE_SYSTEM_INTEGRATOR = "system_integrator"
    TYPE_DISTRIBUTOR = "distributor"
    TYPE_MSP = "msp"
    TYPE_CHOICES = [
        (TYPE_RESELLER, "Reseller"),
        (TYPE_REFERRAL, "Referral"),
        (TYPE_OEM, "OEM"),
        (TYPE_SYSTEM_INTEGRATOR, "System Integrator"),
        (TYPE_DISTRIBUTOR, "Distributor"),
        (TYPE_MSP, "Managed Service Provider"),
    ]

    TIER_REGISTERED = "registered"
    TIER_SILVER = "silver"
    TIER_GOLD = "gold"
    TIER_PLATINUM = "platinum"
    TIER_CHOICES = [
        (TIER_REGISTERED, "Registered"),
        (TIER_SILVER, "Silver"),
        (TIER_GOLD, "Gold"),
        (TIER_PLATINUM, "Platinum"),
    ]

    STATUS_PROSPECT = "prospect"
    STATUS_ONBOARDING = "onboarding"
    STATUS_ACTIVE = "active"
    STATUS_SUSPENDED = "suspended"
    STATUS_CHURNED = "churned"
    STATUS_CHOICES = [
        (STATUS_PROSPECT, "Prospect"),
        (STATUS_ONBOARDING, "Onboarding"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_SUSPENDED, "Suspended"),
        (STATUS_CHURNED, "Churned"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="partners_partners")
    name = models.CharField(max_length=150)
    partner_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_RESELLER)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default=TIER_REGISTERED)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PROSPECT)
    region = models.CharField(max_length=120, blank=True)
    contact_name = models.CharField(max_length=120, blank=True)
    contact_email = models.EmailField(blank=True)
    onboarded_on = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="prt_tenant_status_idx"),
            models.Index(fields=["tenant", "partner_type"], name="prt_tenant_type_idx"),
            models.Index(fields=["tenant", "tier"], name="prt_tenant_tier_idx"),
        ]

    def __str__(self):
        return self.name


class DealRegistration(models.Model):
    """Deal Registration & Protection — a registered partner deal (auto DR-00001)."""

    STATUS_SUBMITTED = "submitted"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_EXPIRED = "expired"
    STATUS_WON = "won"
    STATUS_CHOICES = [
        (STATUS_SUBMITTED, "Submitted"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_EXPIRED, "Expired"),
        (STATUS_WON, "Won"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="partners_dealregistrations")
    partner = models.ForeignKey(
        "partners.Partner", on_delete=models.SET_NULL,
        related_name="deal_registrations", null=True, blank=True)
    number = models.CharField(max_length=20, blank=True)
    deal_name = models.CharField(max_length=150)
    customer_name = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SUBMITTED)
    registered_on = models.DateField(default=timezone.localdate)
    expires_on = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-registered_on", "-id"]
        unique_together = ("tenant", "number")
        indexes = [
            models.Index(fields=["tenant", "status"], name="dreg_tenant_status_idx"),
            models.Index(fields=["tenant", "partner"], name="dreg_tenant_partner_idx"),
            models.Index(fields=["tenant", "registered_on"], name="dreg_tenant_regdate_idx"),
        ]

    def __str__(self):
        return self.number or f"Deal #{self.pk}"

    def save(self, *args, **kwargs):
        if not self.number and self.tenant_id:
            # Per-tenant sequence with a row lock to avoid duplicate numbers under
            # concurrent creation (idempotent for seeds).
            with transaction.atomic():
                last = (DealRegistration.objects.select_for_update()
                        .filter(tenant_id=self.tenant_id, number__startswith="DR-")
                        .order_by("-number").first())
                seq = 1
                if last and last.number:
                    try:
                        seq = int(last.number.split("-")[1]) + 1
                    except (IndexError, ValueError):
                        seq = (DealRegistration.objects
                               .filter(tenant_id=self.tenant_id, number__startswith="DR-")
                               .count() + 1)
                self.number = f"DR-{seq:05d}"
                super().save(*args, **kwargs)
                return
        super().save(*args, **kwargs)


class PartnerCollateral(models.Model):
    """Partner Portal & Collaboration — a partner-facing asset/document."""

    ASSET_DATASHEET = "datasheet"
    ASSET_PLAYBOOK = "playbook"
    ASSET_PRICING = "pricing"
    ASSET_TRAINING = "training"
    ASSET_LOGO = "logo"
    ASSET_CONTRACT = "contract"
    ASSET_TYPE_CHOICES = [
        (ASSET_DATASHEET, "Datasheet"),
        (ASSET_PLAYBOOK, "Playbook"),
        (ASSET_PRICING, "Pricing"),
        (ASSET_TRAINING, "Training"),
        (ASSET_LOGO, "Logo"),
        (ASSET_CONTRACT, "Contract"),
    ]

    ACCESS_PUBLIC = "public"
    ACCESS_PARTNER = "partner"
    ACCESS_INTERNAL = "internal"
    ACCESS_LEVEL_CHOICES = [
        (ACCESS_PUBLIC, "Public"),
        (ACCESS_PARTNER, "Partner"),
        (ACCESS_INTERNAL, "Internal"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="partners_partnercollaterals")
    partner = models.ForeignKey(
        "partners.Partner", on_delete=models.SET_NULL,
        related_name="collateral", null=True, blank=True)
    title = models.CharField(max_length=150)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPE_CHOICES, default=ASSET_DATASHEET)
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVEL_CHOICES, default=ACCESS_PARTNER)
    version = models.CharField(max_length=20, blank=True)
    published_on = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        indexes = [
            models.Index(fields=["tenant", "asset_type"], name="pcol_tenant_asset_idx"),
            models.Index(fields=["tenant", "access_level"], name="pcol_tenant_access_idx"),
            models.Index(fields=["tenant", "partner"], name="pcol_tenant_partner_idx"),
        ]

    def __str__(self):
        return self.title


class PartnerPerformance(models.Model):
    """Partner Performance Tracking — a partner's metrics for a period."""

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="partners_partnerperformances")
    partner = models.ForeignKey(
        "partners.Partner", on_delete=models.SET_NULL,
        related_name="performances", null=True, blank=True)
    period_label = models.CharField(max_length=60)
    revenue = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    deals_closed = models.IntegerField(default=0)
    quota = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    attainment = models.DecimalField(max_digits=6, decimal_places=2, default=0,
                                     help_text="Attainment against quota as a percentage.")
    certification_count = models.IntegerField(default=0)
    satisfaction_score = models.DecimalField(max_digits=4, decimal_places=2, default=0,
                                             help_text="Partner satisfaction score, e.g. 4.50 out of 5.")
    recorded_on = models.DateField(default=timezone.localdate)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-recorded_on", "-id"]
        indexes = [
            models.Index(fields=["tenant", "partner"], name="pperf_tenant_partner_idx"),
            models.Index(fields=["tenant", "recorded_on"], name="pperf_tenant_recdate_idx"),
        ]

    def __str__(self):
        return f"{self.period_label} — {self.partner_id or 'unassigned'}"


class ChannelConflict(models.Model):
    """Channel Conflict Management — a channel conflict case (auto CC-00001)."""

    CONFLICT_OVERLAP = "overlap"
    CONFLICT_PRICING = "pricing"
    CONFLICT_TERRITORY = "territory"
    CONFLICT_ACCOUNT_OWNERSHIP = "account_ownership"
    CONFLICT_LEAD_DISPUTE = "lead_dispute"
    CONFLICT_TYPE_CHOICES = [
        (CONFLICT_OVERLAP, "Overlap"),
        (CONFLICT_PRICING, "Pricing"),
        (CONFLICT_TERRITORY, "Territory"),
        (CONFLICT_ACCOUNT_OWNERSHIP, "Account Ownership"),
        (CONFLICT_LEAD_DISPUTE, "Lead Dispute"),
    ]

    SEVERITY_LOW = "low"
    SEVERITY_MEDIUM = "medium"
    SEVERITY_HIGH = "high"
    SEVERITY_CRITICAL = "critical"
    SEVERITY_CHOICES = [
        (SEVERITY_LOW, "Low"),
        (SEVERITY_MEDIUM, "Medium"),
        (SEVERITY_HIGH, "High"),
        (SEVERITY_CRITICAL, "Critical"),
    ]

    STATUS_OPEN = "open"
    STATUS_INVESTIGATING = "investigating"
    STATUS_RESOLVED = "resolved"
    STATUS_ESCALATED = "escalated"
    STATUS_CLOSED = "closed"
    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_INVESTIGATING, "Investigating"),
        (STATUS_RESOLVED, "Resolved"),
        (STATUS_ESCALATED, "Escalated"),
        (STATUS_CLOSED, "Closed"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="partners_channelconflicts")
    partner = models.ForeignKey(
        "partners.Partner", on_delete=models.SET_NULL,
        related_name="conflicts", null=True, blank=True)
    number = models.CharField(max_length=20, blank=True)
    conflict_type = models.CharField(max_length=20, choices=CONFLICT_TYPE_CHOICES, default=CONFLICT_OVERLAP)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default=SEVERITY_MEDIUM)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    account_name = models.CharField(max_length=150, blank=True)
    reported_on = models.DateField(default=timezone.localdate)
    resolution = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-reported_on", "-id"]
        unique_together = ("tenant", "number")
        indexes = [
            models.Index(fields=["tenant", "status"], name="cconf_tenant_status_idx"),
            models.Index(fields=["tenant", "severity"], name="cconf_tenant_severity_idx"),
            models.Index(fields=["tenant", "conflict_type"], name="cconf_tenant_type_idx"),
        ]

    def __str__(self):
        return self.number or f"Conflict #{self.pk}"

    def save(self, *args, **kwargs):
        if not self.number and self.tenant_id:
            # Per-tenant sequence with a row lock to avoid duplicate numbers under
            # concurrent creation (idempotent for seeds).
            with transaction.atomic():
                last = (ChannelConflict.objects.select_for_update()
                        .filter(tenant_id=self.tenant_id, number__startswith="CC-")
                        .order_by("-number").first())
                seq = 1
                if last and last.number:
                    try:
                        seq = int(last.number.split("-")[1]) + 1
                    except (IndexError, ValueError):
                        seq = (ChannelConflict.objects
                               .filter(tenant_id=self.tenant_id, number__startswith="CC-")
                               .count() + 1)
                self.number = f"CC-{seq:05d}"
                super().save(*args, **kwargs)
                return
        super().save(*args, **kwargs)
