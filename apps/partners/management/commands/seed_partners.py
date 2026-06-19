"""Seed Module 14 (Partner & Channel Management) demo data per tenant.

Idempotent — each model is skipped if data already exists for the tenant.
Depends on `seed_demo` having created the tenants first. Safe to re-run.
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.models import Tenant
from apps.partners.models import (
    ChannelConflict, DealRegistration, Partner, PartnerCollateral, PartnerPerformance,
)

PARTNERS = [
    ("Northwind Solutions", Partner.TYPE_RESELLER, "North America"),
    ("Contoso Integrators", Partner.TYPE_SYSTEM_INTEGRATOR, "Europe"),
    ("Fabrikam Distribution", Partner.TYPE_DISTRIBUTOR, "Asia Pacific"),
    ("Adventure Works Resell", Partner.TYPE_RESELLER, "North America"),
    ("Tailspin Referrals", Partner.TYPE_REFERRAL, "United Kingdom"),
    ("Wingtip MSP", Partner.TYPE_MSP, "Eurozone"),
    ("Proseware OEM", Partner.TYPE_OEM, "North America"),
    ("Litware Channel", Partner.TYPE_DISTRIBUTOR, "Latin America"),
]

CONTACTS = [
    ("Olivia Brown", "olivia@partner.example"),
    ("Noah Smith", "noah@partner.example"),
    ("Sarah Connor", "sarah@partner.example"),
    ("James Miller", "james@partner.example"),
    ("Emma Davis", "emma@partner.example"),
    ("Liam Wilson", "liam@partner.example"),
]

CUSTOMERS = [
    "Globex Corp", "Initech LLC", "Umbrella Industries", "Stark Enterprises",
    "Wayne Holdings", "Acme Co", "Hooli Inc", "Pied Piper",
]

DEAL_NAMES = [
    "ERP Platform Rollout", "Cloud Migration", "Security Suite Upgrade",
    "Analytics Expansion", "Managed Services Renewal", "Net-New Logo Win",
]

COLLATERAL = [
    ("Product Datasheet", PartnerCollateral.ASSET_DATASHEET, PartnerCollateral.ACCESS_PUBLIC),
    ("Sales Playbook", PartnerCollateral.ASSET_PLAYBOOK, PartnerCollateral.ACCESS_PARTNER),
    ("Partner Pricing Guide", PartnerCollateral.ASSET_PRICING, PartnerCollateral.ACCESS_PARTNER),
    ("Certification Training", PartnerCollateral.ASSET_TRAINING, PartnerCollateral.ACCESS_PARTNER),
    ("Brand Logo Pack", PartnerCollateral.ASSET_LOGO, PartnerCollateral.ACCESS_PUBLIC),
    ("Reseller Agreement", PartnerCollateral.ASSET_CONTRACT, PartnerCollateral.ACCESS_INTERNAL),
    ("Competitive Battlecard", PartnerCollateral.ASSET_PLAYBOOK, PartnerCollateral.ACCESS_INTERNAL),
]

PERIODS = ["2026-Q1", "2026-Q2", "Jan 2026", "Feb 2026", "Mar 2026", "Apr 2026"]

ACCOUNTS = [
    "Globex Corp", "Initech LLC", "Umbrella Industries", "Stark Enterprises",
    "Wayne Holdings", "Acme Co",
]


class Command(BaseCommand):
    help = "Seed Module 14 data (partners, deals, collateral, performance, conflicts)."

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.WARNING("No tenants found — run `seed_demo` first."))
            return
        for tenant in tenants:
            self._seed(tenant)
        self.stdout.write(self.style.SUCCESS(
            "\nModule 14 data ready. Log in as a tenant admin to view it."))

    def _seed(self, tenant):
        today = timezone.localdate()

        # --- Partners (parent) ---
        partners = []
        if not Partner.objects.filter(tenant=tenant).exists():
            tiers = [c[0] for c in Partner.TIER_CHOICES]
            statuses = [Partner.STATUS_ACTIVE, Partner.STATUS_ACTIVE,
                        Partner.STATUS_ONBOARDING, Partner.STATUS_PROSPECT,
                        Partner.STATUS_SUSPENDED, Partner.STATUS_CHURNED]
            for name, ptype, region in PARTNERS:
                contact_name, contact_email = random.choice(CONTACTS)
                status = random.choice(statuses)
                partner = Partner.objects.create(
                    tenant=tenant, name=name, partner_type=ptype,
                    tier=random.choice(tiers), status=status, region=region,
                    contact_name=contact_name, contact_email=contact_email,
                    onboarded_on=(today - timedelta(days=random.randint(30, 500))
                                  if status in (Partner.STATUS_ACTIVE, Partner.STATUS_SUSPENDED,
                                                Partner.STATUS_CHURNED) else None),
                    notes=f"{name} — {region} channel partner.",
                )
                partners.append(partner)
        else:
            partners = list(Partner.objects.filter(tenant=tenant))

        # --- Deal registrations ---
        if not DealRegistration.objects.filter(tenant=tenant).exists() and partners:
            statuses = [DealRegistration.STATUS_SUBMITTED, DealRegistration.STATUS_APPROVED,
                        DealRegistration.STATUS_APPROVED, DealRegistration.STATUS_WON,
                        DealRegistration.STATUS_REJECTED, DealRegistration.STATUS_EXPIRED]
            for i in range(random.randint(8, 12)):
                registered = today - timedelta(days=random.randint(1, 200))
                DealRegistration.objects.create(
                    tenant=tenant, partner=random.choice(partners),
                    deal_name=random.choice(DEAL_NAMES),
                    customer_name=random.choice(CUSTOMERS),
                    amount=Decimal(random.randint(20000, 500000)),
                    status=random.choice(statuses),
                    registered_on=registered,
                    expires_on=registered + timedelta(days=random.choice([60, 90, 120])),
                    notes="Deal submitted for registration protection.",
                )

        # --- Partner collateral ---
        if not PartnerCollateral.objects.filter(tenant=tenant).exists():
            chosen = random.sample(COLLATERAL, k=random.randint(6, len(COLLATERAL)))
            for title, asset_type, access in chosen:
                PartnerCollateral.objects.create(
                    tenant=tenant,
                    partner=(random.choice(partners) if partners and random.random() > 0.4 else None),
                    title=title, asset_type=asset_type, access_level=access,
                    version=f"v{random.randint(1, 4)}.{random.randint(0, 9)}",
                    published_on=today - timedelta(days=random.randint(5, 300)),
                    notes=f"{title} available in the partner portal.",
                )

        # --- Partner performance ---
        if not PartnerPerformance.objects.filter(tenant=tenant).exists() and partners:
            for i in range(random.randint(8, 12)):
                partner = random.choice(partners)
                quota = Decimal(random.randint(200000, 1500000))
                revenue = (quota * Decimal(str(round(random.uniform(0.4, 1.4), 2)))
                           ).quantize(Decimal("0.01"))
                attainment = ((revenue / quota) * Decimal("100")).quantize(Decimal("0.01")) if quota else Decimal("0")
                PartnerPerformance.objects.create(
                    tenant=tenant, partner=partner,
                    period_label=random.choice(PERIODS),
                    revenue=revenue, deals_closed=random.randint(1, 40),
                    quota=quota, attainment=attainment,
                    certification_count=random.randint(0, 15),
                    satisfaction_score=Decimal(str(round(random.uniform(2.5, 5.0), 2))),
                    recorded_on=today - timedelta(days=random.randint(1, 120)),
                )

        # --- Channel conflicts ---
        if not ChannelConflict.objects.filter(tenant=tenant).exists():
            ctypes = [c[0] for c in ChannelConflict.CONFLICT_TYPE_CHOICES]
            severities = [c[0] for c in ChannelConflict.SEVERITY_CHOICES]
            statuses = [ChannelConflict.STATUS_OPEN, ChannelConflict.STATUS_INVESTIGATING,
                        ChannelConflict.STATUS_RESOLVED, ChannelConflict.STATUS_RESOLVED,
                        ChannelConflict.STATUS_ESCALATED, ChannelConflict.STATUS_CLOSED]
            for i in range(random.randint(6, 10)):
                status = random.choice(statuses)
                ChannelConflict.objects.create(
                    tenant=tenant,
                    partner=(random.choice(partners) if partners else None),
                    conflict_type=random.choice(ctypes),
                    severity=random.choice(severities),
                    status=status,
                    account_name=random.choice(ACCOUNTS),
                    reported_on=today - timedelta(days=random.randint(1, 150)),
                    resolution=("Conflict resolved through joint account planning."
                                if status in (ChannelConflict.STATUS_RESOLVED,
                                              ChannelConflict.STATUS_CLOSED) else ""),
                    notes="Channel conflict logged for review.",
                )

        self.stdout.write(f"  seeded Module 14 data for '{tenant.slug}'")
