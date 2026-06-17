"""Seed Module 5 (Quote & Proposal Management) demo data per tenant.

Idempotent — each model is skipped if data already exists for the tenant.
Depends on `seed_demo` having created the tenants first. Creates parents
(quotes) before children (line items, proposals, versions).
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.models import Tenant
from apps.quotes.models import (
    PricingRule, Proposal, Quote, QuoteLineItem, QuoteVersion,
)

ACCOUNTS = [
    "Northwind Traders", "Contoso Ltd", "Fabrikam Inc", "Adventure Works",
    "Tailspin Toys", "Wingtip Partners", "Litware Systems", "Proseware Group",
    "Wide World Importers", "Coho Vineyard", "Margie's Travel", "Alpine Ski House",
]

CONTACTS = [
    ("Emily Carter", "emily.carter@example.com"),
    ("Michael Chen", "m.chen@example.com"),
    ("Sofia Reyes", "sofia.reyes@example.com"),
    ("David Okafor", "d.okafor@example.com"),
    ("Hannah Schmidt", "h.schmidt@example.com"),
    ("Raj Patel", "raj.patel@example.com"),
]

QUOTE_TITLES = [
    "Annual Platform Subscription",
    "Enterprise Onboarding Package",
    "Professional Services Engagement",
    "Hardware & Licensing Bundle",
    "Managed Support Renewal",
    "Cloud Migration Project",
    "Security Audit & Remediation",
    "Custom Integration Build",
]

PRODUCTS = [
    ("Platform License", "PLT-100", QuoteLineItem.UNIT_LICENSE, Decimal("1200.00")),
    ("Implementation Hours", "SVC-HRS", QuoteLineItem.UNIT_HOUR, Decimal("185.00")),
    ("Premium Support", "SUP-PRM", QuoteLineItem.UNIT_YEAR, Decimal("4800.00")),
    ("Data Storage Add-on", "STO-ADD", QuoteLineItem.UNIT_MONTH, Decimal("90.00")),
    ("Training Workshop", "TRN-WKS", QuoteLineItem.UNIT_EACH, Decimal("2500.00")),
    ("API Gateway Module", "API-GTW", QuoteLineItem.UNIT_LICENSE, Decimal("750.00")),
]

PRICING_RULES = [
    ("Standard Volume 5%", PricingRule.RULE_VOLUME, Decimal("0"), Decimal("5"), PricingRule.APPROVAL_AUTO, 1),
    ("Volume Tier 10%", PricingRule.RULE_VOLUME, Decimal("5"), Decimal("10"), PricingRule.APPROVAL_MANAGER, 2),
    ("Strategic Volume 20%", PricingRule.RULE_VOLUME, Decimal("10"), Decimal("20"), PricingRule.APPROVAL_DIRECTOR, 3),
    ("Promo Campaign 15%", PricingRule.RULE_PROMO, Decimal("0"), Decimal("15"), PricingRule.APPROVAL_MANAGER, 4),
    ("Loyalty Reward 8%", PricingRule.RULE_LOYALTY, Decimal("0"), Decimal("8"), PricingRule.APPROVAL_AUTO, 5),
    ("Multi-year Contract 25%", PricingRule.RULE_CONTRACT, Decimal("15"), Decimal("25"), PricingRule.APPROVAL_VP, 6),
    ("Clearance 30%", PricingRule.RULE_CLEARANCE, Decimal("20"), Decimal("30"), PricingRule.APPROVAL_DIRECTOR, 7),
]

TEMPLATES = [
    Proposal.TEMPLATE_STANDARD, Proposal.TEMPLATE_EXECUTIVE,
    Proposal.TEMPLATE_TECHNICAL, Proposal.TEMPLATE_MINIMAL,
]

CHANGE_TYPES = [
    QuoteVersion.CHANGE_PRICE, QuoteVersion.CHANGE_SCOPE,
    QuoteVersion.CHANGE_DISCOUNT, QuoteVersion.CHANGE_TERMS,
]


class Command(BaseCommand):
    help = "Seed Module 5 data (quotes, line items, pricing rules, proposals, versions)."

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.WARNING("No tenants found — run `seed_demo` first."))
            return
        for tenant in tenants:
            self._seed(tenant)
        self.stdout.write(self.style.SUCCESS("\nModule 5 data ready. Log in as a tenant admin to view it."))

    def _seed(self, tenant):
        today = timezone.localdate()
        quotes = []

        # ---- Quotes (parents) ---------------------------------------------
        if not Quote.objects.filter(tenant=tenant).exists():
            statuses = [
                Quote.STATUS_DRAFT, Quote.STATUS_PENDING, Quote.STATUS_APPROVED,
                Quote.STATUS_SENT, Quote.STATUS_ACCEPTED, Quote.STATUS_REJECTED,
                Quote.STATUS_EXPIRED, Quote.STATUS_CONVERTED,
            ]
            count = random.randint(8, 12)
            for i in range(count):
                contact, email = random.choice(CONTACTS)
                subtotal = Decimal(random.randint(5000, 60000))
                discount = (subtotal * Decimal(random.choice([0, 5, 10, 15])) / Decimal("100")).quantize(Decimal("0.01"))
                tax = ((subtotal - discount) * Decimal("0.08")).quantize(Decimal("0.01"))
                total = subtotal - discount + tax
                q = Quote.objects.create(
                    tenant=tenant,
                    title=random.choice(QUOTE_TITLES),
                    account_name=random.choice(ACCOUNTS),
                    contact_name=contact,
                    contact_email=email,
                    status=statuses[i % len(statuses)],
                    currency=random.choice([Quote.CURRENCY_USD, Quote.CURRENCY_EUR, Quote.CURRENCY_GBP]),
                    subtotal=subtotal,
                    discount_amount=discount,
                    tax_amount=tax,
                    total_amount=total,
                    valid_until=today + timedelta(days=random.randint(15, 60)),
                    notes="Generated demo quote.",
                )
                quotes.append(q)
        else:
            quotes = list(Quote.objects.filter(tenant=tenant))

        # ---- Quote line items (children) ----------------------------------
        if quotes and not QuoteLineItem.objects.filter(tenant=tenant).exists():
            for q in quotes:
                for pos in range(random.randint(2, 4)):
                    name, sku, unit, price = random.choice(PRODUCTS)
                    QuoteLineItem.objects.create(
                        tenant=tenant, quote=q,
                        product_name=name, sku=sku, unit=unit,
                        description=f"{name} for {q.account_name}",
                        quantity=Decimal(random.randint(1, 12)),
                        unit_price=price,
                        discount_percent=Decimal(random.choice([0, 5, 10])),
                        position=pos + 1,
                    )

        # ---- Pricing rules ------------------------------------------------
        if not PricingRule.objects.filter(tenant=tenant).exists():
            for name, rtype, lo, hi, approval, prio in PRICING_RULES:
                PricingRule.objects.create(
                    tenant=tenant, name=name, rule_type=rtype,
                    description=f"{name} — applies between {lo}% and {hi}% discount.",
                    min_discount_percent=lo, max_discount_percent=hi,
                    approval_level=approval,
                    status=PricingRule.STATUS_ACTIVE, priority=prio,
                )

        # ---- Proposals (children) -----------------------------------------
        if quotes and not Proposal.objects.filter(tenant=tenant).exists():
            statuses = [
                Proposal.STATUS_DRAFT, Proposal.STATUS_REVIEW,
                Proposal.STATUS_FINAL, Proposal.STATUS_SENT,
            ]
            for i, q in enumerate(random.sample(quotes, min(len(quotes), random.randint(6, 8)))):
                Proposal.objects.create(
                    tenant=tenant, quote=q,
                    title=f"Proposal — {q.title}",
                    template=TEMPLATES[i % len(TEMPLATES)],
                    status=statuses[i % len(statuses)],
                    executive_summary=f"Executive summary for {q.account_name}.",
                    body="Detailed scope, deliverables and pricing follow in the sections below.",
                    cover_letter=f"Dear {q.contact_name or 'Customer'}, thank you for your interest.",
                    prepared_by=random.choice([c[0] for c in CONTACTS]),
                )

        # ---- Quote versions (children) ------------------------------------
        if quotes and not QuoteVersion.objects.filter(tenant=tenant).exists():
            for q in quotes:
                n_versions = random.randint(1, 3)
                for v in range(1, n_versions + 1):
                    change = QuoteVersion.CHANGE_INITIAL if v == 1 else random.choice(CHANGE_TYPES)
                    QuoteVersion.objects.create(
                        tenant=tenant, quote=q, version_number=v,
                        change_type=change,
                        change_summary=("Initial draft" if v == 1 else f"Revision {v}"),
                        total_amount=q.total_amount + Decimal(random.randint(-2000, 2000)),
                        is_current=(v == n_versions),
                        snapshot_notes=f"Snapshot of {q.number} at version {v}.",
                    )

        self.stdout.write(f"  seeded Module 5 data for '{tenant.slug}'")
