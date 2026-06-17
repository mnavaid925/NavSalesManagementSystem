"""Seed Module 6 (Order Management) demo data per tenant.

Idempotent — each model is skipped if data already exists for the tenant.
Depends on `seed_demo` having created the tenants first. Creates parent Orders
before child lines/fulfillments/amendments/revenue schedules.
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.models import Tenant
from apps.orders.models import (
    Fulfillment, Order, OrderAmendment, OrderLine, RevenueSchedule,
)

CUSTOMERS = [
    "Northwind Traders", "Contoso Ltd", "Fabrikam Inc", "Adventure Works",
    "Tailspin Toys", "Wingtip Toys", "Litware Inc", "Proseware Inc",
    "Coho Vineyard", "Wide World Importers", "Margie's Travel", "Blue Yonder Airlines",
]

PRODUCTS = [
    ("Enterprise CRM License", "SKU-CRM-ENT", Decimal("1200.00")),
    ("Pro Analytics Add-on", "SKU-ANL-PRO", Decimal("450.00")),
    ("Onboarding Package", "SKU-ONB-STD", Decimal("2500.00")),
    ("API Gateway Seat", "SKU-API-SEAT", Decimal("99.00")),
    ("Premium Support Plan", "SKU-SUP-PRM", Decimal("750.00")),
    ("Data Migration Service", "SKU-DMG-SVC", Decimal("3200.00")),
    ("Mobile Module", "SKU-MOB-MOD", Decimal("320.00")),
    ("Sandbox Environment", "SKU-SBX-ENV", Decimal("180.00")),
]

WAREHOUSES = ["East DC", "West DC", "Central Hub", "Cloud (Digital)"]

PERIODS = ["2025-Q1", "2025-Q2", "2025-Q3", "2025-Q4", "2026-Q1", "2026-Q2"]


class Command(BaseCommand):
    help = "Seed Module 6 data (orders, lines, fulfillments, amendments, revenue schedules)."

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.WARNING("No tenants found — run `seed_demo` first."))
            return
        for tenant in tenants:
            self._seed(tenant)
        self.stdout.write(self.style.SUCCESS("\nModule 6 data ready. Log in as a tenant admin to view it."))

    def _seed(self, tenant):
        today = timezone.localdate()
        orders = []

        # ---- Orders (parents) ----
        if not Order.objects.filter(tenant=tenant).exists():
            for i in range(random.randint(8, 12)):
                status = random.choice([
                    Order.STATUS_DRAFT, Order.STATUS_VALIDATED, Order.STATUS_CONFIRMED,
                    Order.STATUS_CONFIRMED, Order.STATUS_FULFILLED, Order.STATUS_CANCELLED,
                ])
                customer = random.choice(CUSTOMERS)
                order = Order(
                    tenant=tenant,
                    customer_name=customer,
                    customer_email=f"orders@{customer.split()[0].lower()}.example.com",
                    channel=random.choice([c[0] for c in Order.CHANNEL_CHOICES]),
                    status=status,
                    currency="USD",
                    total_amount=Decimal(random.randint(500, 25000)),
                    is_validated=status != Order.STATUS_DRAFT,
                    order_date=today - timedelta(days=random.randint(0, 180)),
                    requested_ship_date=today + timedelta(days=random.randint(2, 30)),
                    billing_address=f"{random.randint(10, 999)} Market St, Suite {random.randint(100, 900)}",
                    shipping_address=f"{random.randint(10, 999)} Industrial Pkwy",
                    notes="Seeded demo order",
                )
                order.save()
                orders.append(order)
        else:
            orders = list(Order.objects.filter(tenant=tenant))

        if not orders:
            self.stdout.write(f"  Module 6 already seeded for '{tenant.slug}' — skipping.")
            return

        # ---- Order lines (children) ----
        if not OrderLine.objects.filter(tenant=tenant).exists():
            for order in orders:
                for _ in range(random.randint(1, 4)):
                    name, sku, price = random.choice(PRODUCTS)
                    OrderLine.objects.create(
                        tenant=tenant, order=order, product_name=name, sku=sku,
                        quantity=random.randint(1, 10), unit_price=price,
                        discount_percent=Decimal(random.choice([0, 0, 5, 10, 15])),
                    )

        # ---- Fulfillments (children) ----
        if not Fulfillment.objects.filter(tenant=tenant).exists():
            shippable = [o for o in orders if o.status in (
                Order.STATUS_CONFIRMED, Order.STATUS_FULFILLED)]
            for order in shippable:
                status = random.choice([
                    Fulfillment.STATUS_PENDING, Fulfillment.STATUS_PACKED,
                    Fulfillment.STATUS_SHIPPED, Fulfillment.STATUS_DELIVERED,
                ])
                carrier = random.choice([c[0] for c in Fulfillment.CARRIER_CHOICES])
                shipped = today - timedelta(days=random.randint(0, 20))
                Fulfillment.objects.create(
                    tenant=tenant, order=order, warehouse=random.choice(WAREHOUSES),
                    carrier=carrier,
                    tracking_number=f"{carrier.upper()}{random.randint(10**9, 10**10 - 1)}",
                    status=status, shipped_on=shipped,
                    expected_delivery=shipped + timedelta(days=random.randint(2, 7)),
                    notes="Seeded demo shipment",
                )

        # ---- Amendments (children) ----
        if not OrderAmendment.objects.filter(tenant=tenant).exists():
            for order in random.sample(orders, min(len(orders), random.randint(4, 7))):
                a_type = random.choice([t[0] for t in OrderAmendment.TYPE_CHOICES])
                status = random.choice([s[0] for s in OrderAmendment.STATUS_CHOICES])
                OrderAmendment.objects.create(
                    tenant=tenant, order=order, amendment_type=a_type, status=status,
                    reason=f"Customer requested a {a_type} change before delivery.",
                    requested_by=random.choice(CUSTOMERS),
                    amount_delta=Decimal(random.choice([-500, -200, 0, 150, 400])),
                    requested_on=today - timedelta(days=random.randint(0, 60)),
                )

        # ---- Revenue schedules (children) ----
        if not RevenueSchedule.objects.filter(tenant=tenant).exists():
            recognized = [o for o in orders if o.status in (
                Order.STATUS_CONFIRMED, Order.STATUS_FULFILLED)]
            for order in recognized:
                method = random.choice([m[0] for m in RevenueSchedule.METHOD_CHOICES])
                installments = random.randint(1, 4)
                per = (order.total_amount / installments).quantize(Decimal("0.01"))
                for n in range(installments):
                    status = random.choice([
                        RevenueSchedule.STATUS_SCHEDULED, RevenueSchedule.STATUS_RECOGNIZED,
                        RevenueSchedule.STATUS_DEFERRED,
                    ])
                    RevenueSchedule.objects.create(
                        tenant=tenant, order=order, method=method, status=status,
                        period_label=random.choice(PERIODS), amount=per,
                        recognition_date=today + timedelta(days=30 * n),
                        notes="Seeded recognition installment",
                    )

        self.stdout.write(f"  seeded Module 6 data for '{tenant.slug}'")
