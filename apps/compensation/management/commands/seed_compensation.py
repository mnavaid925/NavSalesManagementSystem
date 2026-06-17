"""Seed Module 10 (Incentive Compensation Management) demo data per tenant.

Idempotent — each model is skipped if data already exists for the tenant.
Depends on `seed_demo` having created the tenants first. Safe to re-run.
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.compensation.models import (
    Clawback, CommissionPlan, Earning, GlobalPlanVariation, Payout,
)
from apps.core.models import Tenant

REPS = [
    "Olivia Brown", "Noah Smith", "Sarah Connor", "James Miller",
    "Emma Davis", "Liam Wilson", "Ava Martinez", "Lucas Anderson",
]

PLANS = [
    ("Enterprise AE Plan", "AE-ENT", CommissionPlan.TYPE_TIERED, Decimal("8.00"), Decimal("1200000")),
    ("SMB Closer Plan", "SMB-CL", CommissionPlan.TYPE_FLAT, Decimal("5.00"), Decimal("600000")),
    ("New Logo Accelerator", "NL-ACC", CommissionPlan.TYPE_ACCELERATOR, Decimal("6.50"), Decimal("900000")),
    ("Renewal Bonus SPIFF", "REN-SPF", CommissionPlan.TYPE_BONUS, Decimal("2.50"), Decimal("400000")),
    ("Channel Partner Plan", "CH-PTR", CommissionPlan.TYPE_TIERED, Decimal("4.00"), Decimal("750000")),
    ("Field Sales Plan", "FS-STD", CommissionPlan.TYPE_FLAT, Decimal("5.50"), Decimal("800000")),
]

REGIONS = [
    ("North America", GlobalPlanVariation.CURRENCY_USD, Decimal("1.000000")),
    ("United Kingdom", GlobalPlanVariation.CURRENCY_GBP, Decimal("1.270000")),
    ("Eurozone", GlobalPlanVariation.CURRENCY_EUR, Decimal("1.080000")),
    ("Japan", GlobalPlanVariation.CURRENCY_JPY, Decimal("0.006700")),
    ("Australia", GlobalPlanVariation.CURRENCY_AUD, Decimal("0.660000")),
    ("Canada", GlobalPlanVariation.CURRENCY_CAD, Decimal("0.730000")),
    ("India", GlobalPlanVariation.CURRENCY_INR, Decimal("0.012000")),
]

PERIODS = ["2026-Q1", "2026-Q2", "Jan 2026", "Feb 2026", "Mar 2026", "Apr 2026"]


class Command(BaseCommand):
    help = "Seed Module 10 data (plans, earnings, clawbacks, global variations, payouts)."

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.WARNING("No tenants found — run `seed_demo` first."))
            return
        for tenant in tenants:
            self._seed(tenant)
        self.stdout.write(self.style.SUCCESS(
            "\nModule 10 data ready. Log in as a tenant admin to view it."))

    def _seed(self, tenant):
        today = timezone.localdate()

        # --- Commission plans ---
        plans = []
        if not CommissionPlan.objects.filter(tenant=tenant).exists():
            statuses = [CommissionPlan.STATUS_ACTIVE, CommissionPlan.STATUS_ACTIVE,
                        CommissionPlan.STATUS_DRAFT, CommissionPlan.STATUS_PAUSED]
            for name, code, ptype, rate, quota in PLANS:
                plan = CommissionPlan.objects.create(
                    tenant=tenant, name=name, code=code, plan_type=ptype,
                    status=random.choice(statuses), base_rate=rate, target_quota=quota,
                    effective_from=today - timedelta(days=random.randint(60, 400)),
                    description=f"{name} — pays {rate}% on attainment toward a ${quota} quota.",
                )
                plans.append(plan)
        else:
            plans = list(CommissionPlan.objects.filter(tenant=tenant))

        active_plans = [p for p in plans if p.status == CommissionPlan.STATUS_ACTIVE] or plans

        # --- Earnings ---
        earnings = []
        if not Earning.objects.filter(tenant=tenant).exists():
            statuses = [Earning.STATUS_PENDING, Earning.STATUS_APPROVED,
                        Earning.STATUS_PAID, Earning.STATUS_DISPUTED]
            for i in range(random.randint(8, 12)):
                deal_amount = Decimal(random.randint(15000, 250000))
                plan = random.choice(active_plans) if active_plans else None
                rate = plan.base_rate if plan else Decimal("5.00")
                commission = (deal_amount * rate / Decimal("100")).quantize(Decimal("0.01"))
                earning = Earning.objects.create(
                    tenant=tenant, plan=plan, rep_name=random.choice(REPS),
                    deal_reference=f"DEAL-{random.randint(1000, 9999)}",
                    deal_amount=deal_amount, commission_amount=commission,
                    status=random.choice(statuses),
                    earned_on=today - timedelta(days=random.randint(1, 180)),
                    notes="Commission accrued on closed-won deal.",
                )
                earnings.append(earning)
        else:
            earnings = list(Earning.objects.filter(tenant=tenant))

        # --- Clawbacks ---
        if not Clawback.objects.filter(tenant=tenant).exists() and earnings:
            reasons = [c[0] for c in Clawback.REASON_CHOICES]
            statuses = [Clawback.STATUS_OPEN, Clawback.STATUS_APPLIED,
                        Clawback.STATUS_WAIVED, Clawback.STATUS_DISPUTED]
            for i in range(random.randint(6, 9)):
                earning = random.choice(earnings)
                Clawback.objects.create(
                    tenant=tenant, earning=earning, rep_name=earning.rep_name,
                    reason=random.choice(reasons), status=random.choice(statuses),
                    amount=(earning.commission_amount * Decimal(str(round(random.uniform(0.2, 0.9), 2)))
                            ).quantize(Decimal("0.01")),
                    effective_on=today - timedelta(days=random.randint(1, 90)),
                    notes="Adjustment applied against prior earning.",
                )

        # --- Global plan variations ---
        if not GlobalPlanVariation.objects.filter(tenant=tenant).exists() and plans:
            statuses = [GlobalPlanVariation.STATUS_ACTIVE, GlobalPlanVariation.STATUS_ACTIVE,
                        GlobalPlanVariation.STATUS_PENDING, GlobalPlanVariation.STATUS_RETIRED]
            chosen = random.sample(REGIONS, k=random.randint(6, len(REGIONS)))
            for region, currency, fx in chosen:
                plan = random.choice(plans)
                GlobalPlanVariation.objects.create(
                    tenant=tenant, plan=plan, region=region, currency=currency,
                    status=random.choice(statuses), fx_rate=fx,
                    local_quota=(plan.target_quota / fx).quantize(Decimal("0.01")) if fx else plan.target_quota,
                    rate_adjustment=Decimal(str(round(random.uniform(-1.5, 2.0), 2))),
                    effective_from=today - timedelta(days=random.randint(30, 300)),
                    notes=f"Localised plan for {region}.",
                )

        # --- Payouts ---
        if not Payout.objects.filter(tenant=tenant).exists():
            methods = [c[0] for c in Payout.METHOD_CHOICES]
            statuses = [Payout.STATUS_SCHEDULED, Payout.STATUS_PROCESSING,
                        Payout.STATUS_PAID, Payout.STATUS_PAID, Payout.STATUS_FAILED]
            for i in range(random.randint(8, 12)):
                gross = Decimal(random.randint(2000, 30000))
                deductions = (gross * Decimal(str(round(random.uniform(0.05, 0.25), 2)))
                              ).quantize(Decimal("0.01"))
                net = (gross - deductions).quantize(Decimal("0.01"))
                Payout.objects.create(
                    tenant=tenant, rep_name=random.choice(REPS),
                    method=random.choice(methods), status=random.choice(statuses),
                    gross_amount=gross, deductions=deductions, net_amount=net,
                    period_label=random.choice(PERIODS),
                    scheduled_on=today - timedelta(days=random.randint(0, 120)),
                    reference=f"TXN-{random.randint(100000, 999999)}",
                    notes="Compensation run pushed to payroll.",
                )

        self.stdout.write(f"  seeded Module 10 data for '{tenant.slug}'")
