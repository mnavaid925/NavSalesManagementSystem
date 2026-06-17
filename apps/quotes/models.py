from decimal import Decimal

from django.db import models
from django.utils import timezone


class Quote(models.Model):
    """Quote Configuration (CPQ) — a configurable, auto-numbered quote (QUO-00001)."""

    STATUS_DRAFT = "draft"
    STATUS_PENDING = "pending_approval"
    STATUS_APPROVED = "approved"
    STATUS_SENT = "sent"
    STATUS_ACCEPTED = "accepted"
    STATUS_REJECTED = "rejected"
    STATUS_EXPIRED = "expired"
    STATUS_CONVERTED = "converted"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_PENDING, "Pending approval"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_SENT, "Sent"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_EXPIRED, "Expired"),
        (STATUS_CONVERTED, "Converted to order"),
    ]

    CURRENCY_USD = "USD"
    CURRENCY_EUR = "EUR"
    CURRENCY_GBP = "GBP"
    CURRENCY_AUD = "AUD"
    CURRENCY_CHOICES = [
        (CURRENCY_USD, "US Dollar"),
        (CURRENCY_EUR, "Euro"),
        (CURRENCY_GBP, "British Pound"),
        (CURRENCY_AUD, "Australian Dollar"),
    ]

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, related_name="quotes_quotes")
    number = models.CharField(max_length=20, blank=True)
    title = models.CharField(max_length=200)
    account_name = models.CharField(max_length=200, blank=True)
    contact_name = models.CharField(max_length=150, blank=True)
    contact_email = models.EmailField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default=CURRENCY_USD)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valid_until = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    converted_at = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        unique_together = ("tenant", "number")
        indexes = [
            models.Index(fields=["tenant", "status"], name="quote_tenant_status_idx"),
            models.Index(fields=["tenant", "created_at"], name="quote_tenant_created_idx"),
        ]

    def __str__(self):
        return self.number or self.title or f"Quote #{self.pk}"

    def save(self, *args, **kwargs):
        if not self.number and self.tenant_id:
            # Per-tenant sequence with an existence guard (idempotent for seeds).
            last = (Quote.objects.filter(tenant_id=self.tenant_id, number__startswith="QUO-")
                    .order_by("-number").first())
            seq = 1
            if last and last.number:
                try:
                    seq = int(last.number.split("-")[1]) + 1
                except (IndexError, ValueError):
                    seq = Quote.objects.filter(tenant_id=self.tenant_id).count() + 1
            self.number = f"QUO-{seq:05d}"
        if self.status == self.STATUS_SENT and self.sent_at is None:
            self.sent_at = timezone.now()
        if self.status == self.STATUS_CONVERTED and self.converted_at is None:
            self.converted_at = timezone.now()
        super().save(*args, **kwargs)


class QuoteLineItem(models.Model):
    """Quote Configuration (CPQ) — a configured product/service line on a quote."""

    UNIT_EACH = "each"
    UNIT_HOUR = "hour"
    UNIT_MONTH = "month"
    UNIT_YEAR = "year"
    UNIT_LICENSE = "license"
    UNIT_CHOICES = [
        (UNIT_EACH, "Each"),
        (UNIT_HOUR, "Hour"),
        (UNIT_MONTH, "Month"),
        (UNIT_YEAR, "Year"),
        (UNIT_LICENSE, "License"),
    ]

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, related_name="quotes_quotelineitems")
    quote = models.ForeignKey("quotes.Quote", on_delete=models.CASCADE, related_name="line_items")
    product_name = models.CharField(max_length=200)
    sku = models.CharField(max_length=60, blank=True)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default=UNIT_EACH)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position", "id"]
        indexes = [
            models.Index(fields=["tenant", "quote"], name="qli_tenant_quote_idx"),
        ]

    def __str__(self):
        return f"{self.product_name} ×{self.quantity}"

    @property
    def computed_total(self):
        gross = (self.quantity or Decimal("0")) * (self.unit_price or Decimal("0"))
        discount = gross * (self.discount_percent or Decimal("0")) / Decimal("100")
        return gross - discount

    def save(self, *args, **kwargs):
        self.line_total = self.computed_total
        super().save(*args, **kwargs)


class PricingRule(models.Model):
    """Pricing & Discount Approval — a discount band and the approval it requires."""

    RULE_VOLUME = "volume"
    RULE_PROMO = "promotional"
    RULE_LOYALTY = "loyalty"
    RULE_CONTRACT = "contract"
    RULE_CLEARANCE = "clearance"
    RULE_CHOICES = [
        (RULE_VOLUME, "Volume discount"),
        (RULE_PROMO, "Promotional"),
        (RULE_LOYALTY, "Loyalty"),
        (RULE_CONTRACT, "Contract"),
        (RULE_CLEARANCE, "Clearance"),
    ]

    APPROVAL_AUTO = "auto"
    APPROVAL_MANAGER = "manager"
    APPROVAL_DIRECTOR = "director"
    APPROVAL_VP = "vp"
    APPROVAL_CHOICES = [
        (APPROVAL_AUTO, "Auto-approved"),
        (APPROVAL_MANAGER, "Manager approval"),
        (APPROVAL_DIRECTOR, "Director approval"),
        (APPROVAL_VP, "VP approval"),
    ]

    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_INACTIVE, "Inactive"),
        (STATUS_ARCHIVED, "Archived"),
    ]

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, related_name="quotes_pricingrules")
    name = models.CharField(max_length=160)
    rule_type = models.CharField(max_length=20, choices=RULE_CHOICES, default=RULE_VOLUME)
    description = models.TextField(blank=True)
    min_discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    max_discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    approval_level = models.CharField(max_length=20, choices=APPROVAL_CHOICES, default=APPROVAL_AUTO)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    priority = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["priority", "name"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="pricerule_tenant_status_idx"),
        ]

    def __str__(self):
        return self.name


class Proposal(models.Model):
    """Proposal Generation & Templating — a formatted proposal document for a quote."""

    TEMPLATE_STANDARD = "standard"
    TEMPLATE_EXECUTIVE = "executive"
    TEMPLATE_TECHNICAL = "technical"
    TEMPLATE_MINIMAL = "minimal"
    TEMPLATE_CHOICES = [
        (TEMPLATE_STANDARD, "Standard"),
        (TEMPLATE_EXECUTIVE, "Executive summary"),
        (TEMPLATE_TECHNICAL, "Technical deep-dive"),
        (TEMPLATE_MINIMAL, "Minimal"),
    ]

    STATUS_DRAFT = "draft"
    STATUS_REVIEW = "in_review"
    STATUS_FINAL = "final"
    STATUS_SENT = "sent"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_REVIEW, "In review"),
        (STATUS_FINAL, "Final"),
        (STATUS_SENT, "Sent"),
    ]

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, related_name="quotes_proposals")
    quote = models.ForeignKey(
        "quotes.Quote", on_delete=models.SET_NULL,
        related_name="proposals", null=True, blank=True,
    )
    title = models.CharField(max_length=200)
    template = models.CharField(max_length=20, choices=TEMPLATE_CHOICES, default=TEMPLATE_STANDARD)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    executive_summary = models.TextField(blank=True)
    body = models.TextField(blank=True)
    cover_letter = models.TextField(blank=True)
    prepared_by = models.CharField(max_length=150, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="proposal_tenant_status_idx"),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.status == self.STATUS_SENT and self.sent_at is None:
            self.sent_at = timezone.now()
        super().save(*args, **kwargs)


class QuoteVersion(models.Model):
    """Quote Versioning & Comparison — an immutable snapshot of a quote revision."""

    CHANGE_INITIAL = "initial"
    CHANGE_PRICE = "price_change"
    CHANGE_SCOPE = "scope_change"
    CHANGE_DISCOUNT = "discount_change"
    CHANGE_TERMS = "terms_change"
    CHANGE_CHOICES = [
        (CHANGE_INITIAL, "Initial version"),
        (CHANGE_PRICE, "Price change"),
        (CHANGE_SCOPE, "Scope change"),
        (CHANGE_DISCOUNT, "Discount change"),
        (CHANGE_TERMS, "Terms change"),
    ]

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, related_name="quotes_quoteversions")
    quote = models.ForeignKey("quotes.Quote", on_delete=models.CASCADE, related_name="versions")
    version_number = models.PositiveIntegerField(default=1)
    change_type = models.CharField(max_length=20, choices=CHANGE_CHOICES, default=CHANGE_INITIAL)
    change_summary = models.CharField(max_length=255, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_current = models.BooleanField(default=False)
    snapshot_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["quote", "-version_number"]
        unique_together = ("quote", "version_number")
        indexes = [
            models.Index(fields=["tenant", "quote"], name="qver_tenant_quote_idx"),
        ]

    def __str__(self):
        return f"v{self.version_number} — {self.quote}"
