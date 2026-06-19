from django.db import models
from django.utils import timezone


class ProductCatalog(models.Model):
    """Product Catalog & Pricing — a sellable product/SKU with list price and cost."""

    CATEGORY_SOFTWARE = "software"
    CATEGORY_HARDWARE = "hardware"
    CATEGORY_SERVICE = "service"
    CATEGORY_SUBSCRIPTION = "subscription"
    CATEGORY_ADDON = "addon"
    CATEGORY_BUNDLE = "bundle"
    CATEGORY_CHOICES = [
        (CATEGORY_SOFTWARE, "Software"),
        (CATEGORY_HARDWARE, "Hardware"),
        (CATEGORY_SERVICE, "Service"),
        (CATEGORY_SUBSCRIPTION, "Subscription"),
        (CATEGORY_ADDON, "Add-on"),
        (CATEGORY_BUNDLE, "Bundle"),
    ]

    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_DISCONTINUED = "discontinued"
    STATUS_DRAFT = "draft"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_INACTIVE, "Inactive"),
        (STATUS_DISCONTINUED, "Discontinued"),
        (STATUS_DRAFT, "Draft"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="masterdata_productcatalogs")
    name = models.CharField(max_length=150)
    sku = models.CharField(max_length=60, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_SOFTWARE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    unit_price = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    cost = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    currency = models.CharField(max_length=8, default="USD")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="pcat_tenant_status_idx"),
            models.Index(fields=["tenant", "category"], name="pcat_tenant_category_idx"),
        ]

    def __str__(self):
        return self.name


class CustomField(models.Model):
    """Custom Fields & Objects — a tenant-defined field attached to a CRM object."""

    OBJECT_LEAD = "lead"
    OBJECT_OPPORTUNITY = "opportunity"
    OBJECT_ACCOUNT = "account"
    OBJECT_CONTACT = "contact"
    OBJECT_QUOTE = "quote"
    OBJECT_ORDER = "order"
    OBJECT_PRODUCT = "product"
    OBJECT_TYPE_CHOICES = [
        (OBJECT_LEAD, "Lead"),
        (OBJECT_OPPORTUNITY, "Opportunity"),
        (OBJECT_ACCOUNT, "Account"),
        (OBJECT_CONTACT, "Contact"),
        (OBJECT_QUOTE, "Quote"),
        (OBJECT_ORDER, "Order"),
        (OBJECT_PRODUCT, "Product"),
    ]

    FIELD_TEXT = "text"
    FIELD_NUMBER = "number"
    FIELD_DATE = "date"
    FIELD_BOOLEAN = "boolean"
    FIELD_DROPDOWN = "dropdown"
    FIELD_CURRENCY = "currency"
    FIELD_URL = "url"
    FIELD_TYPE_CHOICES = [
        (FIELD_TEXT, "Text"),
        (FIELD_NUMBER, "Number"),
        (FIELD_DATE, "Date"),
        (FIELD_BOOLEAN, "Boolean"),
        (FIELD_DROPDOWN, "Dropdown"),
        (FIELD_CURRENCY, "Currency"),
        (FIELD_URL, "URL"),
    ]

    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_DRAFT = "draft"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_INACTIVE, "Inactive"),
        (STATUS_DRAFT, "Draft"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="masterdata_customfields")
    name = models.CharField(max_length=120)
    field_key = models.CharField(max_length=60)
    object_type = models.CharField(max_length=20, choices=OBJECT_TYPE_CHOICES, default=OBJECT_LEAD)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPE_CHOICES, default=FIELD_TEXT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    required = models.BooleanField(default=False)
    default_value = models.CharField(max_length=150, blank=True)
    help_text = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["object_type", "name"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="cfld_tenant_status_idx"),
            models.Index(fields=["tenant", "object_type"], name="cfld_tenant_object_idx"),
        ]

    def __str__(self):
        return self.name


class MethodologyConfig(models.Model):
    """Sales Methodology Configuration — a configured selling framework for a tenant."""

    METHODOLOGY_MEDDIC = "meddic"
    METHODOLOGY_BANT = "bant"
    METHODOLOGY_SPIN = "spin"
    METHODOLOGY_CHALLENGER = "challenger"
    METHODOLOGY_SANDLER = "sandler"
    METHODOLOGY_CUSTOM = "custom"
    METHODOLOGY_CHOICES = [
        (METHODOLOGY_MEDDIC, "MEDDIC"),
        (METHODOLOGY_BANT, "BANT"),
        (METHODOLOGY_SPIN, "SPIN Selling"),
        (METHODOLOGY_CHALLENGER, "Challenger Sale"),
        (METHODOLOGY_SANDLER, "Sandler"),
        (METHODOLOGY_CUSTOM, "Custom"),
    ]

    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_DRAFT = "draft"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_INACTIVE, "Inactive"),
        (STATUS_DRAFT, "Draft"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="masterdata_methodologyconfigs")
    name = models.CharField(max_length=150)
    methodology = models.CharField(max_length=20, choices=METHODOLOGY_CHOICES, default=METHODOLOGY_BANT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    stages_count = models.IntegerField(default=5)
    qualification_fields = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="mcfg_tenant_status_idx"),
            models.Index(fields=["tenant", "methodology"], name="mcfg_tenant_method_idx"),
        ]

    def __str__(self):
        return self.name


class PriceBook(models.Model):
    """Price Book — a currency/region-scoped collection of catalog prices."""

    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_DRAFT = "draft"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_INACTIVE, "Inactive"),
        (STATUS_DRAFT, "Draft"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="masterdata_pricebooks")
    name = models.CharField(max_length=150)
    currency = models.CharField(max_length=8, default="USD")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    region = models.CharField(max_length=120, blank=True)
    is_default = models.BooleanField(default=False)
    valid_from = models.DateField(default=timezone.localdate)
    valid_to = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="pbk_tenant_status_idx"),
            models.Index(fields=["tenant", "currency"], name="pbk_tenant_currency_idx"),
        ]

    def __str__(self):
        return self.name


class LocalizationSetting(models.Model):
    """Localization & Multi-Language — a supported language/locale configuration."""

    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_DRAFT = "draft"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_INACTIVE, "Inactive"),
        (STATUS_DRAFT, "Draft"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="masterdata_localizationsettings")
    language_code = models.CharField(max_length=10)
    language_name = models.CharField(max_length=60)
    locale = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    is_default = models.BooleanField(default=False)
    date_format = models.CharField(max_length=40, blank=True)
    number_format = models.CharField(max_length=40, blank=True)
    currency = models.CharField(max_length=8, default="USD")
    completion_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["language_name"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="locz_tenant_status_idx"),
            models.Index(fields=["tenant", "language_code"], name="locz_tenant_langcode_idx"),
        ]

    def __str__(self):
        return self.language_name or self.language_code
