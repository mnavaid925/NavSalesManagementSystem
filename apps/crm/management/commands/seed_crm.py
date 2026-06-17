"""Seed Module 3 (Contact & Account Management) demo data per tenant.

Idempotent — each model is skipped if data already exists for the tenant.
Depends on `seed_demo` having created the tenants first. Creates parents before
children (tiers -> accounts -> contacts -> relationships -> plans).
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.models import Tenant
from apps.crm.models import Account, AccountPlan, AccountTier, Contact, RelationshipMap

TIERS = [
    ("Tier 1 — Strategic", AccountTier.SEGMENT_STRATEGIC, 1, Decimal("5000000"), "#7c3aed"),
    ("Tier 2 — Enterprise", AccountTier.SEGMENT_ENTERPRISE, 2, Decimal("1000000"), "#2563eb"),
    ("Tier 3 — Mid-Market", AccountTier.SEGMENT_MIDMARKET, 3, Decimal("250000"), "#0ea5e9"),
    ("Tier 4 — SMB", AccountTier.SEGMENT_SMB, 4, Decimal("50000"), "#16a34a"),
]

COMPANIES = [
    ("Northwind Traders", "Wholesale"), ("Initech Solutions", "Software"),
    ("Umbrella Logistics", "Logistics"), ("Stark Manufacturing", "Manufacturing"),
    ("Wayne Industries", "Conglomerate"), ("Cyberdyne Systems", "Robotics"),
    ("Soylent Foods", "Food & Beverage"), ("Hooli Cloud", "Technology"),
    ("Vandelay Imports", "Import/Export"), ("Pied Piper Data", "Software"),
]
SUBSIDIARY_SUFFIX = ["EMEA", "APAC", "North America", "Labs"]

CITIES = [("Austin", "USA"), ("London", "UK"), ("Berlin", "Germany"),
          ("Singapore", "Singapore"), ("Toronto", "Canada"), ("Sydney", "Australia")]

FIRST_NAMES = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley",
               "Jamie", "Cameron", "Drew", "Quinn", "Avery", "Skyler"]
LAST_NAMES = ["Patel", "Nguyen", "Garcia", "Khan", "Okafor", "Rossi",
              "Schmidt", "Kim", "Silva", "Andersson", "Walsh", "Dubois"]
TITLES = ["Chief Executive Officer", "VP of Procurement", "Director of IT",
          "Head of Operations", "Procurement Manager", "Finance Lead",
          "VP of Engineering", "Operations Analyst"]
DEPARTMENTS = ["Executive", "Procurement", "IT", "Operations", "Finance", "Engineering"]

PLAN_TITLES = ["FY Growth & Expansion Plan", "Renewal & Upsell Strategy",
               "Land-and-Expand Roadmap", "Strategic Partnership Plan",
               "Cross-Sell Acceleration Plan"]
OBJECTIVES = [
    "Grow annual spend by 30% through cross-sell into adjacent business units.",
    "Secure multi-year renewal and expand seat count across regions.",
    "Establish executive sponsorship and a joint success plan.",
    "Reduce churn risk by improving product adoption and QBR cadence.",
]


class Command(BaseCommand):
    help = "Seed Module 3 data (accounts, contacts, relationships, tiers, account plans)."

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.WARNING("No tenants found — run `seed_demo` first."))
            return
        for tenant in tenants:
            self._seed(tenant)
        self.stdout.write(self.style.SUCCESS("\nModule 3 data ready. Log in as a tenant admin to view it."))

    def _seed(self, tenant):
        # --- Tiers (parents for accounts) ---
        if not AccountTier.objects.filter(tenant=tenant).exists():
            for name, segment, rank, min_val, color in TIERS:
                AccountTier.objects.create(
                    tenant=tenant, name=name, segment=segment, rank=rank,
                    min_annual_value=min_val, color=color, is_active=True,
                    description=f"{name} accounts (≥ ${min_val:,.0f} annual value).")
        tiers = list(AccountTier.objects.filter(tenant=tenant))

        # --- Accounts (parents + a couple of subsidiaries) ---
        if not Account.objects.filter(tenant=tenant).exists():
            parents = []
            for name, industry in COMPANIES:
                city, country = random.choice(CITIES)
                acct = Account.objects.create(
                    tenant=tenant, name=name, account_type=random.choice(
                        [Account.TYPE_CUSTOMER, Account.TYPE_CUSTOMER, Account.TYPE_PROSPECT, Account.TYPE_PARTNER]),
                    status=Account.STATUS_ACTIVE, industry=industry,
                    website=f"https://www.{name.split()[0].lower()}.example.com",
                    phone=f"+1-555-0{random.randint(100, 999)}",
                    billing_city=city, billing_country=country,
                    employee_count=random.choice([50, 120, 400, 1500, 6000]),
                    annual_revenue=Decimal(random.randint(1, 80)) * Decimal("1000000"),
                    tier=random.choice(tiers) if tiers else None,
                    description=f"{name} operates in the {industry} sector.")
                parents.append(acct)
            # A few parent-child links to exercise the hierarchy.
            for parent in random.sample(parents, k=min(3, len(parents))):
                suffix = random.choice(SUBSIDIARY_SUFFIX)
                city, country = random.choice(CITIES)
                Account.objects.create(
                    tenant=tenant, parent=parent, name=f"{parent.name} {suffix}",
                    account_type=parent.account_type, status=Account.STATUS_ACTIVE,
                    industry=parent.industry, billing_city=city, billing_country=country,
                    employee_count=random.choice([20, 60, 200]),
                    annual_revenue=Decimal(random.randint(1, 20)) * Decimal("500000"),
                    tier=parent.tier,
                    description=f"{suffix} subsidiary of {parent.name}.")
        accounts = list(Account.objects.filter(tenant=tenant))

        # --- Contacts (children of accounts) ---
        if not Contact.objects.filter(tenant=tenant).exists():
            for acct in accounts:
                used = set()
                for i in range(random.randint(1, 3)):
                    first = random.choice(FIRST_NAMES)
                    last = random.choice(LAST_NAMES)
                    while (first, last) in used:
                        first = random.choice(FIRST_NAMES)
                        last = random.choice(LAST_NAMES)
                    used.add((first, last))
                    Contact.objects.create(
                        tenant=tenant, account=acct, first_name=first, last_name=last,
                        title=random.choice(TITLES), department=random.choice(DEPARTMENTS),
                        email=f"{first.lower()}.{last.lower()}@{acct.name.split()[0].lower()}.example.com",
                        phone=f"+1-555-0{random.randint(100, 999)}",
                        mobile=f"+1-555-0{random.randint(100, 999)}",
                        status=Contact.STATUS_ACTIVE,
                        enrichment_status=random.choice(
                            [Contact.ENRICH_NONE, Contact.ENRICH_PARTIAL, Contact.ENRICH_VERIFIED]),
                        is_primary=(i == 0))

        # --- Relationship maps (between contacts within the same account) ---
        if not RelationshipMap.objects.filter(tenant=tenant).exists():
            for acct in accounts:
                contacts = list(Contact.objects.filter(tenant=tenant, account=acct))
                if len(contacts) < 2:
                    continue
                for _ in range(min(2, len(contacts) - 1)):
                    a, b = random.sample(contacts, 2)
                    RelationshipMap.objects.create(
                        tenant=tenant, account=acct, from_contact=a, to_contact=b,
                        relationship_type=random.choice([c[0] for c in RelationshipMap.TYPE_CHOICES]),
                        strength=random.choice([c[0] for c in RelationshipMap.STRENGTH_CHOICES]),
                        notes="Mapped during account planning.")

        # --- Account plans (children of accounts, auto-numbered) ---
        if not AccountPlan.objects.filter(tenant=tenant).exists():
            today = timezone.localdate()
            for acct in random.sample(accounts, k=min(8, len(accounts))):
                target = Decimal(random.randint(2, 50)) * Decimal("100000")
                AccountPlan.objects.create(
                    tenant=tenant, account=acct, title=random.choice(PLAN_TITLES),
                    fiscal_year=today.year,
                    status=random.choice([c[0] for c in AccountPlan.STATUS_CHOICES]),
                    priority=random.choice([c[0] for c in AccountPlan.PRIORITY_CHOICES]),
                    objective=random.choice(OBJECTIVES),
                    growth_strategy="Expand footprint via cross-sell, executive alignment and QBRs.",
                    target_revenue=target,
                    current_revenue=target * Decimal(str(round(random.uniform(0.2, 0.8), 2))),
                    start_date=today - timedelta(days=random.randint(0, 120)),
                    end_date=today + timedelta(days=random.randint(120, 300)))

        self.stdout.write(f"  seeded Module 3 data for '{tenant.slug}'")
