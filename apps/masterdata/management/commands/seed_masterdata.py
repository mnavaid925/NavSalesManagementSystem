"""Seed Module 19 (Master Data & Configuration) demo data per tenant.

Idempotent — each model is skipped if data already exists for the tenant.
Depends on `seed_demo` having created the tenants first. Safe to re-run.
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.models import Tenant
from apps.masterdata.models import (
    CustomField, LocalizationSetting, MethodologyConfig, PriceBook, ProductCatalog,
)

PRODUCTS = [
    ("CRM Pro License", "CRM-PRO", ProductCatalog.CATEGORY_SOFTWARE, Decimal("1200.00"), Decimal("300.00")),
    ("Analytics Add-on", "AN-ADD", ProductCatalog.CATEGORY_ADDON, Decimal("450.00"), Decimal("110.00")),
    ("Enterprise Suite", "ENT-STE", ProductCatalog.CATEGORY_BUNDLE, Decimal("8500.00"), Decimal("2100.00")),
    ("Onboarding Service", "SVC-ONB", ProductCatalog.CATEGORY_SERVICE, Decimal("2500.00"), Decimal("900.00")),
    ("Mobile Scanner", "HW-SCN", ProductCatalog.CATEGORY_HARDWARE, Decimal("320.00"), Decimal("140.00")),
    ("Support Subscription", "SUB-SUP", ProductCatalog.CATEGORY_SUBSCRIPTION, Decimal("99.00"), Decimal("22.00")),
    ("API Gateway", "SW-API", ProductCatalog.CATEGORY_SOFTWARE, Decimal("680.00"), Decimal("170.00")),
    ("Data Migration", "SVC-MIG", ProductCatalog.CATEGORY_SERVICE, Decimal("4200.00"), Decimal("1500.00")),
]

CUSTOM_FIELDS = [
    ("Lead Source Detail", "lead_source_detail", CustomField.OBJECT_LEAD, CustomField.FIELD_TEXT),
    ("Deal Health Score", "deal_health_score", CustomField.OBJECT_OPPORTUNITY, CustomField.FIELD_NUMBER),
    ("Renewal Date", "renewal_date", CustomField.OBJECT_ACCOUNT, CustomField.FIELD_DATE),
    ("VIP Contact", "vip_contact", CustomField.OBJECT_CONTACT, CustomField.FIELD_BOOLEAN),
    ("Quote Tier", "quote_tier", CustomField.OBJECT_QUOTE, CustomField.FIELD_DROPDOWN),
    ("Contract Value", "contract_value", CustomField.OBJECT_ORDER, CustomField.FIELD_CURRENCY),
    ("Product Demo URL", "product_demo_url", CustomField.OBJECT_PRODUCT, CustomField.FIELD_URL),
    ("Industry Vertical", "industry_vertical", CustomField.OBJECT_ACCOUNT, CustomField.FIELD_TEXT),
]

METHODOLOGIES = [
    ("MEDDIC Enterprise", MethodologyConfig.METHODOLOGY_MEDDIC, 7,
     "Metrics, Economic buyer, Decision criteria, Decision process, Identify pain, Champion."),
    ("BANT Standard", MethodologyConfig.METHODOLOGY_BANT, 5, "Budget, Authority, Need, Timeline."),
    ("SPIN Selling Flow", MethodologyConfig.METHODOLOGY_SPIN, 6,
     "Situation, Problem, Implication, Need-payoff questions."),
    ("Challenger Playbook", MethodologyConfig.METHODOLOGY_CHALLENGER, 6, "Teach, Tailor, Take control."),
    ("Sandler Submarine", MethodologyConfig.METHODOLOGY_SANDLER, 7, "Bonding, contracts, pain, budget, decision."),
    ("Custom SMB Flow", MethodologyConfig.METHODOLOGY_CUSTOM, 4, "Lightweight qualification for SMB deals."),
]

PRICE_BOOKS = [
    ("North America List", "USD", "North America"),
    ("EMEA Price Book", "EUR", "EMEA"),
    ("UK Price Book", "GBP", "United Kingdom"),
    ("APAC Price Book", "AUD", "Asia Pacific"),
    ("India Price Book", "INR", "India"),
    ("Partner Wholesale", "USD", "Global"),
]

LANGUAGES = [
    ("en", "English", "en-US", "MM/DD/YYYY", "1,234.56", "USD", Decimal("100.00")),
    ("es", "Spanish", "es-ES", "DD/MM/YYYY", "1.234,56", "EUR", Decimal("92.50")),
    ("fr", "French", "fr-FR", "DD/MM/YYYY", "1 234,56", "EUR", Decimal("88.00")),
    ("de", "German", "de-DE", "DD.MM.YYYY", "1.234,56", "EUR", Decimal("85.40")),
    ("ja", "Japanese", "ja-JP", "YYYY/MM/DD", "1,234.56", "JPY", Decimal("70.00")),
    ("pt", "Portuguese", "pt-BR", "DD/MM/YYYY", "1.234,56", "BRL", Decimal("64.20")),
    ("hi", "Hindi", "hi-IN", "DD-MM-YYYY", "1,23,456.78", "INR", Decimal("48.00")),
]


class Command(BaseCommand):
    help = "Seed Module 19 data (products, custom fields, methodologies, price books, localization)."

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.WARNING("No tenants found — run `seed_demo` first."))
            return
        for tenant in tenants:
            self._seed(tenant)
        self.stdout.write(self.style.SUCCESS(
            "\nModule 19 data ready. Log in as a tenant admin to view it."))

    def _seed(self, tenant):
        today = timezone.localdate()

        # --- Product catalog ---
        if not ProductCatalog.objects.filter(tenant=tenant).exists():
            statuses = [ProductCatalog.STATUS_ACTIVE, ProductCatalog.STATUS_ACTIVE,
                        ProductCatalog.STATUS_DRAFT, ProductCatalog.STATUS_INACTIVE,
                        ProductCatalog.STATUS_DISCONTINUED]
            for name, sku, category, price, cost in PRODUCTS:
                ProductCatalog.objects.create(
                    tenant=tenant, name=name, sku=sku, category=category,
                    status=random.choice(statuses), unit_price=price, cost=cost,
                    currency="USD",
                    description=f"{name} — list price ${price}.",
                )

        # --- Custom fields ---
        if not CustomField.objects.filter(tenant=tenant).exists():
            statuses = [CustomField.STATUS_ACTIVE, CustomField.STATUS_ACTIVE,
                        CustomField.STATUS_DRAFT, CustomField.STATUS_INACTIVE]
            for name, key, obj_type, field_type in CUSTOM_FIELDS:
                CustomField.objects.create(
                    tenant=tenant, name=name, field_key=key, object_type=obj_type,
                    field_type=field_type, status=random.choice(statuses),
                    required=random.choice([True, False]),
                    help_text=f"Captures {name.lower()} on the {obj_type}.",
                    notes="Tenant-defined custom field.",
                )

        # --- Methodology configs ---
        if not MethodologyConfig.objects.filter(tenant=tenant).exists():
            statuses = [MethodologyConfig.STATUS_ACTIVE, MethodologyConfig.STATUS_ACTIVE,
                        MethodologyConfig.STATUS_DRAFT, MethodologyConfig.STATUS_INACTIVE]
            chosen = random.sample(METHODOLOGIES, k=random.randint(4, len(METHODOLOGIES)))
            for i, (name, methodology, stages, fields) in enumerate(chosen):
                MethodologyConfig.objects.create(
                    tenant=tenant, name=name, methodology=methodology,
                    status=random.choice(statuses), stages_count=stages,
                    qualification_fields=fields, is_default=(i == 0),
                    description=f"{name} qualification framework.",
                )

        # --- Price books ---
        if not PriceBook.objects.filter(tenant=tenant).exists():
            statuses = [PriceBook.STATUS_ACTIVE, PriceBook.STATUS_ACTIVE,
                        PriceBook.STATUS_DRAFT, PriceBook.STATUS_INACTIVE]
            chosen = random.sample(PRICE_BOOKS, k=random.randint(4, len(PRICE_BOOKS)))
            for i, (name, currency, region) in enumerate(chosen):
                valid_to = today + timedelta(days=random.randint(180, 540)) if random.random() > 0.4 else None
                PriceBook.objects.create(
                    tenant=tenant, name=name, currency=currency, region=region,
                    status=random.choice(statuses), is_default=(i == 0),
                    valid_from=today - timedelta(days=random.randint(30, 300)),
                    valid_to=valid_to,
                    description=f"Pricing for the {region} market in {currency}.",
                )

        # --- Localization settings ---
        if not LocalizationSetting.objects.filter(tenant=tenant).exists():
            statuses = [LocalizationSetting.STATUS_ACTIVE, LocalizationSetting.STATUS_ACTIVE,
                        LocalizationSetting.STATUS_DRAFT, LocalizationSetting.STATUS_INACTIVE]
            chosen = random.sample(LANGUAGES, k=random.randint(5, len(LANGUAGES)))
            for i, (code, lang_name, locale, date_fmt, num_fmt, currency, pct) in enumerate(chosen):
                LocalizationSetting.objects.create(
                    tenant=tenant, language_code=code, language_name=lang_name,
                    locale=locale, status=random.choice(statuses), is_default=(i == 0),
                    date_format=date_fmt, number_format=num_fmt, currency=currency,
                    completion_pct=pct,
                    notes=f"{lang_name} ({locale}) localization profile.",
                )

        self.stdout.write(f"  seeded Module 19 data for '{tenant.slug}'")
