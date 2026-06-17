"""Seed Module 4 (Sales Forecasting) demo data per tenant.

Idempotent — each model is skipped if data already exists for the tenant.
Depends on `seed_demo` having created the tenants first.
"""
import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.models import Tenant
from apps.forecasting.models import (
    Forecast, ForecastAccuracy, ForecastAdjustment, ForecastCategory, Quota,
)

CATEGORIES = [
    ("Omitted", ForecastCategory.COMMIT_OMITTED, 5, Decimal("0.00")),
    ("Pipeline", ForecastCategory.COMMIT_PIPELINE, 25, Decimal("0.25")),
    ("Best Case", ForecastCategory.COMMIT_BEST_CASE, 50, Decimal("0.50")),
    ("Commit", ForecastCategory.COMMIT_COMMIT, 80, Decimal("0.80")),
    ("Closed Won", ForecastCategory.COMMIT_CLOSED, 100, Decimal("1.00")),
]

OWNERS = [
    "Sarah Connor", "James Miller", "Olivia Brown", "Noah Smith",
    "West Region Team", "East Region Team", "Enterprise Team",
]

CONFIDENCE = [Forecast.CONFIDENCE_LOW, Forecast.CONFIDENCE_MEDIUM, Forecast.CONFIDENCE_HIGH]
ADJ_TYPES = [t for t, _ in ForecastAdjustment.TYPE_CHOICES]
GRADES = [g for g, _ in ForecastAccuracy.GRADE_CHOICES]


class Command(BaseCommand):
    help = "Seed Module 4 data (forecast categories, forecasts, quotas, adjustments, accuracy)."

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.WARNING("No tenants found — run `seed_demo` first."))
            return
        for tenant in tenants:
            self._seed(tenant)
        self.stdout.write(self.style.SUCCESS(
            "\nModule 4 data ready. Log in as a tenant admin to view it."))

    def _quarter_window(self, base_year, q):
        start_month = (q - 1) * 3 + 1
        start = date(base_year, start_month, 1)
        end_month = start_month + 2
        # last day of the quarter (first of next month minus a day)
        if end_month == 12:
            end = date(base_year, 12, 31)
        else:
            end = date(base_year, end_month + 1, 1) - timedelta(days=1)
        return start, end, f"Q{q} {base_year}"

    def _seed(self, tenant):
        # --- Categories (parents) -----------------------------------------
        categories = []
        if not ForecastCategory.objects.filter(tenant=tenant).exists():
            for name, commitment, prob, weight in CATEGORIES:
                cat = ForecastCategory.objects.create(
                    tenant=tenant, name=name, commitment=commitment,
                    probability=prob, weight=weight, is_active=True,
                    description=f"{name} commitment bucket for roll-ups.")
                categories.append(cat)
        else:
            categories = list(ForecastCategory.objects.filter(tenant=tenant))

        # --- Forecasts (parents for adjustments/accuracy) -----------------
        forecasts = []
        if not Forecast.objects.filter(tenant=tenant).exists():
            today = timezone.localdate()
            year = today.year
            current_q = (today.month - 1) // 3 + 1
            commit_cat = next((c for c in categories if c.commitment == ForecastCategory.COMMIT_COMMIT), None)
            for i in range(8):
                # spread across recent quarters & owners
                q = ((current_q - 1 + i) % 4) + 1
                fy = year if q >= current_q else year + ((current_q - 1 + i) // 4)
                start, end, label = self._quarter_window(fy, q)
                pipeline = Decimal(random.randint(400, 1200)) * 1000
                commit = (pipeline * Decimal("0.45")).quantize(Decimal("1.00"))
                best_case = (pipeline * Decimal("0.70")).quantize(Decimal("1.00"))
                ai_pred = (commit * Decimal(str(round(random.uniform(0.92, 1.12), 2)))).quantize(Decimal("1.00"))
                status = random.choice([
                    Forecast.STATUS_DRAFT, Forecast.STATUS_SUBMITTED,
                    Forecast.STATUS_APPROVED, Forecast.STATUS_CLOSED])
                f = Forecast.objects.create(
                    tenant=tenant, category=commit_cat or (categories[0] if categories else None),
                    name=f"{label} Forecast — {random.choice(OWNERS)}",
                    owner_name=random.choice(OWNERS),
                    period_type=Forecast.PERIOD_QUARTER, period_label=label,
                    period_start=start, period_end=end,
                    pipeline_amount=pipeline, commit_amount=commit,
                    best_case_amount=best_case, ai_predicted_amount=ai_pred,
                    ai_confidence=random.choice(CONFIDENCE), status=status,
                    notes="Auto-generated demo forecast.")
                forecasts.append(f)
        else:
            forecasts = list(Forecast.objects.filter(tenant=tenant))

        # --- Quotas -------------------------------------------------------
        if not Quota.objects.filter(tenant=tenant).exists():
            today = timezone.localdate()
            year = today.year
            current_q = (today.month - 1) // 3 + 1
            for owner in OWNERS[:6]:
                start, end, label = self._quarter_window(year, current_q)
                target = Decimal(random.randint(200, 600)) * 1000
                attained = (target * Decimal(str(round(random.uniform(0.4, 1.15), 2)))).quantize(Decimal("1.00"))
                if attained >= target:
                    status = Quota.STATUS_ACHIEVED
                else:
                    status = Quota.STATUS_ACTIVE
                Quota.objects.create(
                    tenant=tenant, owner_name=owner, period_type=Quota.PERIOD_QUARTER,
                    period_label=label, period_start=start, period_end=end,
                    target_amount=target, attained_amount=attained, status=status,
                    notes="Quarterly quota target.")

        # --- Adjustments (children of forecasts) --------------------------
        if forecasts and not ForecastAdjustment.objects.filter(tenant=tenant).exists():
            for _ in range(random.randint(6, 10)):
                f = random.choice(forecasts)
                adj_type = random.choice(ADJ_TYPES)
                magnitude = Decimal(random.randint(10, 80)) * 1000
                if adj_type == ForecastAdjustment.TYPE_HAIRCUT:
                    magnitude = -magnitude
                ForecastAdjustment.objects.create(
                    tenant=tenant, forecast=f, adjustment_type=adj_type,
                    amount=magnitude, adjusted_by=random.choice(OWNERS),
                    status=random.choice([s for s, _ in ForecastAdjustment.STATUS_CHOICES]),
                    reason="Manager roll-up adjustment based on deal review.")

        # --- Accuracy records (reference closed forecasts) ----------------
        if not ForecastAccuracy.objects.filter(tenant=tenant).exists():
            closed = [f for f in forecasts if f.status == Forecast.STATUS_CLOSED] or forecasts
            for i in range(min(6, max(1, len(closed)))):
                f = closed[i % len(closed)] if closed else None
                forecasted = (f.commit_amount if f else Decimal(random.randint(100, 400) * 1000))
                actual = (forecasted * Decimal(str(round(random.uniform(0.8, 1.2), 2)))).quantize(Decimal("1.00"))
                if forecasted and forecasted > 0:
                    err = abs((actual - forecasted) / forecasted)
                    accuracy = (Decimal("100") - (err * Decimal("100"))).quantize(Decimal("0.01"))
                    if accuracy < 0:
                        accuracy = Decimal("0.00")
                else:
                    accuracy = Decimal("0.00")
                if accuracy >= 95:
                    grade = ForecastAccuracy.GRADE_EXCELLENT
                elif accuracy >= 85:
                    grade = ForecastAccuracy.GRADE_GOOD
                elif accuracy >= 70:
                    grade = ForecastAccuracy.GRADE_FAIR
                else:
                    grade = ForecastAccuracy.GRADE_POOR
                ForecastAccuracy.objects.create(
                    tenant=tenant, forecast=f,
                    period_label=(f.period_label if f else "Past period"),
                    forecasted_amount=forecasted, actual_amount=actual,
                    accuracy_pct=accuracy, grade=grade,
                    analyzed_on=timezone.localdate() - timedelta(days=random.randint(5, 90)),
                    notes="Post-period variance analysis.")

        self.stdout.write(f"  seeded Module 4 data for '{tenant.slug}'")
