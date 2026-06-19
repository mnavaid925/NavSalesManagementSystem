"""Seed Module 11 (Customer Success & Account Management) demo data per tenant.

Idempotent — each model is skipped if data already exists for the tenant.
Depends on `seed_demo` having created the tenants first. Safe to re-run.
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.models import Tenant
from apps.success.models import (
    Advocacy, HealthScore, OnboardingPlan, QBR, Renewal,
)

ACCOUNTS = [
    "Acme Corp", "Globex Industries", "Initech LLC", "Umbrella Group",
    "Stark Enterprises", "Wayne Holdings", "Soylent Foods", "Hooli Inc",
    "Vandelay Imports", "Pied Piper", "Massive Dynamic", "Wonka Co",
]

OWNERS = [
    "Olivia Brown", "Noah Smith", "Sarah Connor", "James Miller",
    "Emma Davis", "Liam Wilson", "Ava Martinez", "Lucas Anderson",
]

CONTACTS = [
    "Diana Prince", "Bruce Banner", "Tony Reed", "Carol Strange",
    "Peter Quill", "Wanda Frost", "Steve Rogers", "Natasha Vue",
]

PERIODS = ["2026-Q1", "2026-Q2", "2025-Q4", "2026-Q3", "Jan 2026", "Apr 2026"]

PLAN_NAMES = [
    "Standard Onboarding", "Enterprise Implementation", "Quick Start",
    "White-Glove Rollout", "Migration & Setup", "Phased Deployment",
]


class Command(BaseCommand):
    help = "Seed Module 11 data (health scores, renewals, onboarding, advocacy, QBRs)."

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.WARNING("No tenants found — run `seed_demo` first."))
            return
        for tenant in tenants:
            self._seed(tenant)
        self.stdout.write(self.style.SUCCESS(
            "\nModule 11 data ready. Log in as a tenant admin to view it."))

    def _seed(self, tenant):
        today = timezone.localdate()

        # --- Health scores ---
        if not HealthScore.objects.filter(tenant=tenant).exists():
            risks = [c[0] for c in HealthScore.RISK_LEVEL_CHOICES]
            trends = [c[0] for c in HealthScore.TREND_CHOICES]
            for account in random.sample(ACCOUNTS, k=random.randint(8, 12)):
                HealthScore.objects.create(
                    tenant=tenant, account_name=account, owner=random.choice(OWNERS),
                    score=random.randint(10, 98), risk_level=random.choice(risks),
                    trend=random.choice(trends),
                    arr=Decimal(random.randint(20000, 500000)),
                    last_reviewed=today - timedelta(days=random.randint(1, 90)),
                    notes="Latest health review based on usage and support signals.",
                )

        # --- Renewals ---
        if not Renewal.objects.filter(tenant=tenant).exists():
            types = [c[0] for c in Renewal.RENEWAL_TYPE_CHOICES]
            statuses = [Renewal.STATUS_OPEN, Renewal.STATUS_AT_RISK, Renewal.STATUS_COMMITTED,
                        Renewal.STATUS_WON, Renewal.STATUS_LOST]
            for i in range(random.randint(8, 12)):
                current = Decimal(random.randint(20000, 300000))
                proposed = (current * Decimal(str(round(random.uniform(0.9, 1.6), 2)))
                            ).quantize(Decimal("0.01"))
                Renewal.objects.create(
                    tenant=tenant, account_name=random.choice(ACCOUNTS),
                    owner=random.choice(OWNERS), renewal_type=random.choice(types),
                    status=random.choice(statuses), arr_current=current, arr_proposed=proposed,
                    probability=random.randint(10, 95),
                    renewal_date=today + timedelta(days=random.randint(-60, 180)),
                    notes="Renewal opportunity tracked in the success pipeline.",
                )

        # --- Onboarding plans ---
        if not OnboardingPlan.objects.filter(tenant=tenant).exists():
            statuses = [c[0] for c in OnboardingPlan.STATUS_CHOICES]
            for i in range(random.randint(6, 10)):
                status = random.choice(statuses)
                progress = (100 if status == OnboardingPlan.STATUS_COMPLETED
                            else 0 if status == OnboardingPlan.STATUS_NOT_STARTED
                            else random.randint(15, 85))
                start = today - timedelta(days=random.randint(5, 120))
                OnboardingPlan.objects.create(
                    tenant=tenant, account_name=random.choice(ACCOUNTS),
                    plan_name=random.choice(PLAN_NAMES), owner=random.choice(OWNERS),
                    status=status, progress_pct=progress, start_date=start,
                    target_go_live=start + timedelta(days=random.randint(30, 120)),
                    notes="Implementation plan covering setup, training and go-live.",
                )

        # --- Advocacy ---
        if not Advocacy.objects.filter(tenant=tenant).exists():
            types = [c[0] for c in Advocacy.ADVOCACY_TYPE_CHOICES]
            statuses = [c[0] for c in Advocacy.STATUS_CHOICES]
            for i in range(random.randint(6, 10)):
                Advocacy.objects.create(
                    tenant=tenant, account_name=random.choice(ACCOUNTS),
                    contact_name=random.choice(CONTACTS),
                    advocacy_type=random.choice(types), status=random.choice(statuses),
                    nps_score=random.randint(0, 10),
                    last_engaged=today - timedelta(days=random.randint(1, 120)),
                    notes="Customer advocate engaged for reference activities.",
                )

        # --- QBRs ---
        if not QBR.objects.filter(tenant=tenant).exists():
            statuses = [c[0] for c in QBR.STATUS_CHOICES]
            sentiments = [c[0] for c in QBR.SENTIMENT_CHOICES]
            for i in range(random.randint(8, 12)):
                QBR.objects.create(
                    tenant=tenant, account_name=random.choice(ACCOUNTS),
                    period_label=random.choice(PERIODS), owner=random.choice(OWNERS),
                    status=random.choice(statuses), sentiment=random.choice(sentiments),
                    scheduled_on=today + timedelta(days=random.randint(-90, 60)),
                    health_summary="Account health steady; key initiatives on track.",
                    notes="Quarterly business review covering goals and outcomes.",
                )

        self.stdout.write(f"  seeded Module 11 data for '{tenant.slug}'")
