"""Seed Module 12 (Sales Analytics & Intelligence) demo data per tenant.

Idempotent — each model is skipped if data already exists for the tenant.
Depends on `seed_demo` having created the tenants first. Safe to re-run.
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.analytics.models import (
    Benchmark, ConversionFunnel, RepScorecard, SalesVelocity, WinLossAnalysis,
)
from apps.core.models import Tenant

REPS = [
    "Olivia Brown", "Noah Smith", "Sarah Connor", "James Miller",
    "Emma Davis", "Liam Wilson", "Ava Martinez", "Lucas Anderson",
]

DEALS = [
    "Acme Corp Renewal", "Globex Platform Expansion", "Initech License Upgrade",
    "Umbrella Suite Rollout", "Soylent Annual Contract", "Hooli Enterprise Deal",
    "Stark Industries SaaS", "Wayne Tech Migration", "Cyberdyne Onboarding",
    "Wonka Logistics Bundle", "Pied Piper Compression", "Vandelay Imports Plan",
]

COMPETITORS = [
    "Salesforce", "HubSpot", "Pipedrive", "Zoho", "Microsoft Dynamics",
    "In-house build", "", "Freshsales",
]

STAGES = [
    "Lead", "Qualified", "Demo Scheduled", "Proposal Sent",
    "Negotiation", "Closed Won",
]

METRICS = [
    ("Average Win Rate", Benchmark.CATEGORY_WIN_RATE),
    ("Sales Cycle Length", Benchmark.CATEGORY_CYCLE_TIME),
    ("Average Deal Size", Benchmark.CATEGORY_DEAL_SIZE),
    ("Quota Attainment", Benchmark.CATEGORY_QUOTA),
    ("Weekly Activities per Rep", Benchmark.CATEGORY_ACTIVITY),
    ("New Logo Win Rate", Benchmark.CATEGORY_WIN_RATE),
    ("Renewal Cycle Time", Benchmark.CATEGORY_CYCLE_TIME),
]

PERIODS = ["2026-Q1", "2026-Q2", "Jan 2026", "Feb 2026", "Mar 2026", "Apr 2026"]


class Command(BaseCommand):
    help = "Seed Module 12 data (win/loss, velocity, funnel, scorecards, benchmarks)."

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.WARNING("No tenants found — run `seed_demo` first."))
            return
        for tenant in tenants:
            self._seed(tenant)
        self.stdout.write(self.style.SUCCESS(
            "\nModule 12 data ready. Log in as a tenant admin to view it."))

    def _seed(self, tenant):
        today = timezone.localdate()

        # --- Win/Loss analyses ---
        if not WinLossAnalysis.objects.filter(tenant=tenant).exists():
            outcomes = [WinLossAnalysis.OUTCOME_WON, WinLossAnalysis.OUTCOME_WON,
                        WinLossAnalysis.OUTCOME_LOST, WinLossAnalysis.OUTCOME_NO_DECISION]
            reasons = [c[0] for c in WinLossAnalysis.REASON_CATEGORY_CHOICES]
            for deal in random.sample(DEALS, k=random.randint(8, len(DEALS))):
                WinLossAnalysis.objects.create(
                    tenant=tenant, deal_name=deal, rep_name=random.choice(REPS),
                    outcome=random.choice(outcomes),
                    amount=Decimal(random.randint(15000, 350000)),
                    competitor=random.choice(COMPETITORS),
                    reason_category=random.choice(reasons),
                    closed_on=today - timedelta(days=random.randint(1, 180)),
                    notes="Post-mortem review of the deal outcome.",
                )

        # --- Sales velocity ---
        if not SalesVelocity.objects.filter(tenant=tenant).exists():
            segments = [c[0] for c in SalesVelocity.SEGMENT_CHOICES]
            for i in range(random.randint(6, 10)):
                avg_deal = Decimal(random.randint(8000, 120000))
                win_rate = Decimal(str(round(random.uniform(15, 55), 2)))
                cycle = random.randint(20, 110)
                pipeline = Decimal(random.randint(400000, 4000000))
                # velocity = (opps * win_rate% * avg_deal) / cycle -> stored, never computed live
                velocity = ((pipeline / Decimal(str(max(avg_deal, 1)))) * (win_rate / Decimal("100"))
                            * avg_deal / Decimal(str(cycle))).quantize(Decimal("0.01"))
                SalesVelocity.objects.create(
                    tenant=tenant, period_label=random.choice(PERIODS),
                    segment=random.choice(segments), avg_deal_size=avg_deal,
                    win_rate=win_rate, sales_cycle_days=cycle, pipeline_value=pipeline,
                    velocity_score=velocity,
                    recorded_on=today - timedelta(days=random.randint(0, 120)),
                )

        # --- Conversion funnel ---
        if not ConversionFunnel.objects.filter(tenant=tenant).exists():
            segments = [c[0] for c in ConversionFunnel.SEGMENT_CHOICES]
            period = random.choice(PERIODS)
            segment = random.choice(segments)
            entered = random.randint(800, 2000)
            for stage in STAGES:
                converted = int(entered * random.uniform(0.45, 0.85))
                rate = (Decimal(converted) / Decimal(str(max(entered, 1)))
                        * Decimal("100")).quantize(Decimal("0.01"))
                ConversionFunnel.objects.create(
                    tenant=tenant, stage_name=stage, segment=segment, period_label=period,
                    entered_count=entered, converted_count=converted,
                    conversion_rate=rate, avg_days_in_stage=random.randint(2, 25),
                    recorded_on=today - timedelta(days=random.randint(0, 60)),
                )
                entered = converted  # next stage starts from those that converted

        # --- Rep scorecards ---
        if not RepScorecard.objects.filter(tenant=tenant).exists():
            grades = [c[0] for c in RepScorecard.GRADE_CHOICES]
            period = random.choice(PERIODS)
            chosen = random.sample(REPS, k=random.randint(6, len(REPS)))
            for rank, rep in enumerate(chosen, start=1):
                quota = Decimal(random.randint(300000, 900000))
                attainment = Decimal(str(round(random.uniform(45, 135), 2)))
                RepScorecard.objects.create(
                    tenant=tenant, rep_name=rep, period_label=period,
                    quota=quota, attainment=attainment,
                    deals_won=random.randint(3, 25), deals_lost=random.randint(1, 15),
                    activities=random.randint(40, 320), ranking=rank,
                    grade=random.choice(grades),
                    notes="Quarterly performance scorecard.",
                )

        # --- Benchmarks ---
        if not Benchmark.objects.filter(tenant=tenant).exists():
            statuses = [Benchmark.STATUS_ABOVE, Benchmark.STATUS_AT, Benchmark.STATUS_BELOW]
            for name, category in METRICS:
                peer = Decimal(str(round(random.uniform(20, 200), 2)))
                top = (peer * Decimal(str(round(random.uniform(1.1, 1.4), 2)))
                       ).quantize(Decimal("0.01"))
                ours = (peer * Decimal(str(round(random.uniform(0.8, 1.3), 2)))
                        ).quantize(Decimal("0.01"))
                if ours > top:
                    status = Benchmark.STATUS_ABOVE
                elif ours < peer:
                    status = Benchmark.STATUS_BELOW
                else:
                    status = random.choice(statuses)
                Benchmark.objects.create(
                    tenant=tenant, metric_name=name, category=category,
                    our_value=ours, peer_median=peer, top_quartile=top,
                    period_label=random.choice(PERIODS), status=status,
                    recorded_on=today - timedelta(days=random.randint(0, 90)),
                )

        self.stdout.write(f"  seeded Module 12 data for '{tenant.slug}'")
