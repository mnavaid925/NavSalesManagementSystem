"""Seed Module 7 (Territory & Quota Management) demo data per tenant.

Idempotent — each model is skipped if data already exists for the tenant.
Depends on `seed_demo` having created the tenants first.
"""
import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.models import Tenant
from apps.territories.models import (
    CoverageModel, QuotaPlan, Territory, TerritoryAssignment, TerritoryPerformance,
)

TERRITORIES = [
    ("North America East", "NA-E", Territory.TYPE_GEOGRAPHIC, "Northeast", "USA"),
    ("North America West", "NA-W", Territory.TYPE_GEOGRAPHIC, "West Coast", "USA"),
    ("EMEA Central", "EMEA-C", Territory.TYPE_GEOGRAPHIC, "Central Europe", "Germany"),
    ("APAC Growth", "APAC-G", Territory.TYPE_GEOGRAPHIC, "Southeast Asia", "Singapore"),
    ("Enterprise Healthcare", "ENT-HC", Territory.TYPE_INDUSTRY, "National", "USA"),
    ("Financial Services", "FIN-SVC", Territory.TYPE_INDUSTRY, "National", "UK"),
    ("SMB Inside", "SMB-IN", Territory.TYPE_ACCOUNT, "Remote", "USA"),
    ("Strategic Named Accounts", "STRAT-NA", Territory.TYPE_NAMED_ACCOUNT, "Global", "USA"),
]

REPS = [
    ("Sarah Connor", "sarah.connor@example.com"),
    ("James Miller", "james.miller@example.com"),
    ("Olivia Brown", "olivia.brown@example.com"),
    ("Noah Smith", "noah.smith@example.com"),
    ("Emma Davis", "emma.davis@example.com"),
    ("Liam Wilson", "liam.wilson@example.com"),
]

COVERAGE_MODELS = [
    ("Field-led Enterprise", CoverageModel.MODEL_DIRECT),
    ("Inside SMB Engine", CoverageModel.MODEL_INSIDE),
    ("Hybrid Mid-market", CoverageModel.MODEL_HYBRID),
    ("Channel Partner Network", CoverageModel.MODEL_PARTNER),
    ("Regional Pod Structure", CoverageModel.MODEL_POD),
]

PERIOD_LABELS = ["Q1 FY25", "Q2 FY25", "Q3 FY25", "Q4 FY25"]


class Command(BaseCommand):
    help = "Seed Module 7 data (territories, assignments, quota plans, coverage models, performance)."

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.WARNING("No tenants found — run `seed_demo` first."))
            return
        for tenant in tenants:
            self._seed(tenant)
        self.stdout.write(self.style.SUCCESS(
            "\nModule 7 data ready. Log in as a tenant admin to view it."))

    def _seed(self, tenant):
        # --- Territories ------------------------------------------------------
        territories = []
        if not Territory.objects.filter(tenant=tenant).exists():
            for name, code, ttype, region, country in TERRITORIES:
                territories.append(Territory.objects.create(
                    tenant=tenant, name=name, code=code, territory_type=ttype,
                    status=random.choice([Territory.STATUS_ACTIVE, Territory.STATUS_ACTIVE,
                                          Territory.STATUS_UNDER_REVIEW]),
                    region=region, country=country,
                    description=f"{name} sales territory covering {region}.",
                    account_count=random.randint(20, 320),
                    annual_potential=Decimal(random.randint(500_000, 12_000_000)),
                ))
        else:
            territories = list(Territory.objects.filter(tenant=tenant))

        # --- Assignments ------------------------------------------------------
        if not TerritoryAssignment.objects.filter(tenant=tenant).exists() and territories:
            today = timezone.localdate()
            for territory in territories:
                owner_name, owner_email = random.choice(REPS)
                TerritoryAssignment.objects.create(
                    tenant=tenant, territory=territory,
                    rep_name=owner_name, rep_email=owner_email,
                    assignment_role=TerritoryAssignment.ROLE_OWNER,
                    status=TerritoryAssignment.STATUS_ACTIVE,
                    workload_percent=random.choice([60, 80, 100]),
                    effective_date=today - timedelta(days=random.randint(30, 300)),
                    notes="Primary territory ownership.",
                )
                if random.random() < 0.5:
                    ov_name, ov_email = random.choice(REPS)
                    TerritoryAssignment.objects.create(
                        tenant=tenant, territory=territory,
                        rep_name=ov_name, rep_email=ov_email,
                        assignment_role=TerritoryAssignment.ROLE_OVERLAY,
                        status=random.choice([TerritoryAssignment.STATUS_ACTIVE,
                                              TerritoryAssignment.STATUS_PROPOSED]),
                        workload_percent=random.choice([20, 40, 50]),
                        effective_date=today - timedelta(days=random.randint(10, 120)),
                        notes="Overlay specialist support.",
                    )

        # --- Quota plans ------------------------------------------------------
        if not QuotaPlan.objects.filter(tenant=tenant).exists() and territories:
            today = timezone.localdate()
            year = today.year
            for territory in territories:
                target = Decimal(random.randint(250_000, 4_000_000))
                QuotaPlan.objects.create(
                    tenant=tenant, territory=territory,
                    name=f"{territory.code} FY{year} Quota",
                    period_type=random.choice([QuotaPlan.PERIOD_QUARTERLY, QuotaPlan.PERIOD_ANNUAL]),
                    fiscal_year=year,
                    status=random.choice([QuotaPlan.STATUS_APPROVED, QuotaPlan.STATUS_APPROVED,
                                          QuotaPlan.STATUS_PROPOSED, QuotaPlan.STATUS_DRAFT]),
                    target_amount=target,
                    stretch_amount=(target * Decimal("1.15")).quantize(Decimal("0.01")),
                    start_date=date(year, 1, 1),
                    end_date=date(year, 12, 31),
                    notes="Annual quota allocation.",
                )

        # --- Coverage models --------------------------------------------------
        if not CoverageModel.objects.filter(tenant=tenant).exists():
            for name, mtype in COVERAGE_MODELS:
                CoverageModel.objects.create(
                    tenant=tenant, name=name, model_type=mtype,
                    status=random.choice([CoverageModel.STATUS_ADOPTED, CoverageModel.STATUS_PILOT,
                                          CoverageModel.STATUS_PROPOSED]),
                    target_ratio=Decimal(str(round(random.uniform(15, 120), 2))),
                    rep_capacity=random.randint(3, 40),
                    coverage_score=Decimal(str(round(random.uniform(55, 98), 2))),
                    description=f"{name} coverage strategy.",
                )

        # --- Performance snapshots --------------------------------------------
        if not TerritoryPerformance.objects.filter(tenant=tenant).exists() and territories:
            today = timezone.localdate()
            for territory in territories:
                for i, label in enumerate(PERIOD_LABELS):
                    quota = Decimal(random.randint(200_000, 1_500_000))
                    actual = (quota * Decimal(str(round(random.uniform(0.55, 1.30), 2)))
                              ).quantize(Decimal("0.01"))
                    ratio = actual / quota if quota else Decimal("0")
                    if ratio >= Decimal("1.05"):
                        rating = TerritoryPerformance.RATING_EXCEEDING
                    elif ratio >= Decimal("0.9"):
                        rating = TerritoryPerformance.RATING_ON_TRACK
                    elif ratio >= Decimal("0.75"):
                        rating = TerritoryPerformance.RATING_AT_RISK
                    else:
                        rating = TerritoryPerformance.RATING_UNDERPERFORMING
                    TerritoryPerformance.objects.create(
                        tenant=tenant, territory=territory,
                        period_type=TerritoryPerformance.PERIOD_QUARTERLY,
                        period_label=label, rating=rating,
                        quota_amount=quota, actual_amount=actual,
                        pipeline_amount=(quota * Decimal(str(round(random.uniform(1.2, 3.0), 2)))
                                         ).quantize(Decimal("0.01")),
                        deals_won=random.randint(2, 30),
                        period_end=today - timedelta(days=(len(PERIOD_LABELS) - i) * 60),
                    )

        self.stdout.write(f"  seeded Module 7 data for '{tenant.slug}'")
