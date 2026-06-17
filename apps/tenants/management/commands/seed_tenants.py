"""Seed Module 0 (Tenant & Subscription Management) demo data per tenant.

Idempotent — each model is skipped if data already exists for the tenant.
Depends on `seed_demo` having created the tenants first.
"""
import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.models import Tenant
from apps.tenants.models import (
    BrandingSetting, EncryptionKey, HealthMetric, Invoice, Subscription,
)

PLAN_PRICE = {
    Subscription.PLAN_STARTER: Decimal("499.00"),
    Subscription.PLAN_PRO: Decimal("1499.00"),
    Subscription.PLAN_ENTERPRISE: Decimal("3999.00"),
}

METRICS = [
    ("CPU Utilisation", HealthMetric.CATEGORY_RESOURCE, "%", Decimal("90")),
    ("Storage Used", HealthMetric.CATEGORY_RESOURCE, "GB", Decimal("100")),
    ("API Requests / day", HealthMetric.CATEGORY_USAGE, "k", Decimal("500")),
    ("Avg API Latency", HealthMetric.CATEGORY_PERFORMANCE, "ms", Decimal("400")),
    ("Uptime (30d)", HealthMetric.CATEGORY_UPTIME, "%", Decimal("99.9")),
]


class Command(BaseCommand):
    help = "Seed Module 0 data (subscriptions, invoices, keys, branding, health metrics)."

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.WARNING("No tenants found — run `seed_demo` first."))
            return
        for tenant in tenants:
            self._seed(tenant)
        self.stdout.write(self.style.SUCCESS("\nModule 0 data ready. Log in as a tenant admin to view it."))

    def _seed(self, tenant):
        plan = random.choice([Subscription.PLAN_PRO, Subscription.PLAN_ENTERPRISE])
        if not Subscription.objects.filter(tenant=tenant).exists():
            today = timezone.localdate()
            sub = Subscription.objects.create(
                tenant=tenant, plan=plan, status=Subscription.STATUS_ACTIVE,
                seats=random.choice([10, 25, 50]), monthly_amount=PLAN_PRICE[plan],
                started_on=today - timedelta(days=300),
                renews_on=today + timedelta(days=65), is_auto_renew=True,
            )
        else:
            sub = Subscription.objects.filter(tenant=tenant).first()

        if not Invoice.objects.filter(tenant=tenant).exists():
            today = timezone.localdate()
            year = today.year
            for month in range(1, today.month + 1):
                issued = date(year, month, 1)
                is_current = month == today.month
                status = Invoice.STATUS_PAID
                if is_current:
                    status = Invoice.STATUS_SENT
                elif month == today.month - 1 and tenant.slug == "globex":
                    status = Invoice.STATUS_OVERDUE
                amount = sub.monthly_amount + Decimal(random.randint(0, 400))
                Invoice.objects.create(
                    tenant=tenant, subscription=sub, amount=amount, status=status,
                    period_start=issued, period_end=issued + timedelta(days=27),
                    issued_on=issued, due_on=issued + timedelta(days=14),
                    notes="Monthly subscription charge",
                )

        if not EncryptionKey.objects.filter(tenant=tenant).exists():
            for label, status in [("Primary API Key", EncryptionKey.STATUS_ACTIVE),
                                  ("Data-at-rest Key", EncryptionKey.STATUS_ACTIVE),
                                  ("Legacy Key", EncryptionKey.STATUS_ROTATED)]:
                _, prefix, hashed = EncryptionKey.generate_secret()
                EncryptionKey.objects.create(
                    tenant=tenant, label=label, key_prefix=prefix, hashed_key=hashed,
                    algorithm=EncryptionKey.ALGO_AES256, status=status)

        if not BrandingSetting.objects.filter(tenant=tenant).exists():
            BrandingSetting.objects.create(
                tenant=tenant, name="Default", is_default=True,
                primary_color="#2563eb", accent_color="#0ea5e9",
                login_message=f"Welcome to {tenant.name}",
                email_from_name=tenant.name, theme=BrandingSetting.THEME_LIGHT)

        if not HealthMetric.objects.filter(tenant=tenant).exists():
            for name, category, unit, threshold in METRICS:
                value = Decimal(str(round(random.uniform(20, float(threshold) * 0.95), 1)))
                status = HealthMetric.STATUS_OK
                if value >= threshold * Decimal("0.9"):
                    status = HealthMetric.STATUS_CRITICAL
                elif value >= threshold * Decimal("0.75"):
                    status = HealthMetric.STATUS_WARNING
                HealthMetric.objects.create(
                    tenant=tenant, metric_name=name, category=category, value=value,
                    unit=unit, threshold=threshold, status=status)

        self.stdout.write(f"  seeded Module 0 data for '{tenant.slug}'")
