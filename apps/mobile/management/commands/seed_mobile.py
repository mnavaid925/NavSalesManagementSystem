"""Seed Module 16 (Mobile Sales) demo data per tenant.

Idempotent — each model is skipped if data already exists for the tenant.
Depends on `seed_demo` having created the tenants first. Safe to re-run.
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.models import Tenant
from apps.mobile.models import (
    CallActivity, FieldVisit, MobileAlert, MobileDevice, MobileQuote,
)

REPS = [
    "Olivia Brown", "Noah Smith", "Sarah Connor", "James Miller",
    "Emma Davis", "Liam Wilson", "Ava Martinez", "Lucas Anderson",
]

ACCOUNTS = [
    "Acme Corp", "Globex Industries", "Initech LLC", "Umbrella Group",
    "Soylent Foods", "Stark Enterprises", "Wayne Holdings", "Wonka Co",
]

CONTACTS = [
    "Michael Scott", "Pam Beesly", "Jim Halpert", "Dwight Schrute",
    "Angela Martin", "Kevin Malone", "Oscar Nunez", "Stanley Hudson",
]

DEVICE_NAMES = [
    "iPhone 15 Pro", "iPad Air", "Galaxy S24", "Pixel 8",
    "iPhone 14", "Galaxy Tab S9", "OnePlus 12", "Web Console",
]

LOCATIONS = [
    "Downtown Office", "Client HQ", "Regional Branch", "Trade Show Booth",
    "Co-working Space", "Customer Plant", "Airport Lounge",
]

APP_VERSIONS = ["3.2.1", "3.3.0", "3.4.2", "4.0.0", "4.1.1"]

ALERT_TITLES = [
    "Deal moved to negotiation",
    "Quote awaiting your approval",
    "Quota at 60% with 10 days left",
    "Follow-up task due today",
    "New lead assigned to you",
    "Renewal contract expiring soon",
    "Demo scheduled for tomorrow",
    "Discount approval requested",
]


class Command(BaseCommand):
    help = "Seed Module 16 data (devices, field visits, mobile quotes, calls, alerts)."

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.WARNING("No tenants found — run `seed_demo` first."))
            return
        for tenant in tenants:
            self._seed(tenant)
        self.stdout.write(self.style.SUCCESS(
            "\nModule 16 data ready. Log in as a tenant admin to view it."))

    def _seed(self, tenant):
        today = timezone.localdate()

        # --- Mobile devices ---
        if not MobileDevice.objects.filter(tenant=tenant).exists():
            platforms = [c[0] for c in MobileDevice.PLATFORM_CHOICES]
            statuses = [MobileDevice.STATUS_ACTIVE, MobileDevice.STATUS_ACTIVE,
                        MobileDevice.STATUS_INACTIVE, MobileDevice.STATUS_LOST,
                        MobileDevice.STATUS_WIPED]
            for i in range(random.randint(8, 12)):
                MobileDevice.objects.create(
                    tenant=tenant, device_name=random.choice(DEVICE_NAMES),
                    user_name=random.choice(REPS),
                    platform=random.choice(platforms), status=random.choice(statuses),
                    app_version=random.choice(APP_VERSIONS),
                    push_enabled=random.choice([True, True, False]),
                    last_sync=timezone.now() - timedelta(hours=random.randint(1, 240)),
                    notes="Enrolled mobile CRM device.",
                )

        # --- Field visits ---
        if not FieldVisit.objects.filter(tenant=tenant).exists():
            types = [c[0] for c in FieldVisit.TYPE_CHOICES]
            statuses = [FieldVisit.STATUS_PLANNED, FieldVisit.STATUS_CHECKED_IN,
                        FieldVisit.STATUS_COMPLETED, FieldVisit.STATUS_COMPLETED,
                        FieldVisit.STATUS_CANCELED, FieldVisit.STATUS_NO_SHOW]
            for i in range(random.randint(8, 12)):
                FieldVisit.objects.create(
                    tenant=tenant, rep_name=random.choice(REPS),
                    account_name=random.choice(ACCOUNTS),
                    visit_type=random.choice(types), status=random.choice(statuses),
                    scheduled_on=today + timedelta(days=random.randint(-60, 30)),
                    location=random.choice(LOCATIONS),
                    duration_minutes=random.choice([30, 45, 60, 90, 120]),
                    notes="In-person sales engagement logged from mobile.",
                )

        # --- Mobile quotes ---
        if not MobileQuote.objects.filter(tenant=tenant).exists():
            statuses = [MobileQuote.STATUS_DRAFT, MobileQuote.STATUS_SUBMITTED,
                        MobileQuote.STATUS_APPROVED, MobileQuote.STATUS_APPROVED,
                        MobileQuote.STATUS_REJECTED, MobileQuote.STATUS_EXPIRED]
            for i in range(random.randint(8, 12)):
                MobileQuote.objects.create(
                    tenant=tenant, rep_name=random.choice(REPS),
                    customer_name=random.choice(ACCOUNTS),
                    amount=Decimal(random.randint(5000, 150000)),
                    discount_pct=Decimal(str(round(random.uniform(0, 25), 2))),
                    status=random.choice(statuses),
                    submitted_on=today - timedelta(days=random.randint(0, 90)),
                    notes="Quote prepared in the mobile app.",
                )

        # --- Call activities ---
        if not CallActivity.objects.filter(tenant=tenant).exists():
            directions = [c[0] for c in CallActivity.DIRECTION_CHOICES]
            call_types = [c[0] for c in CallActivity.TYPE_CHOICES]
            outcomes = [c[0] for c in CallActivity.OUTCOME_CHOICES]
            for i in range(random.randint(8, 12)):
                CallActivity.objects.create(
                    tenant=tenant, rep_name=random.choice(REPS),
                    contact_name=random.choice(CONTACTS),
                    direction=random.choice(directions),
                    call_type=random.choice(call_types),
                    outcome=random.choice(outcomes),
                    duration_seconds=random.choice([0, 45, 120, 300, 600, 900]),
                    call_date=today - timedelta(days=random.randint(0, 60)),
                    notes="Call logged via the mobile dialer integration.",
                )

        # --- Mobile alerts ---
        if not MobileAlert.objects.filter(tenant=tenant).exists():
            types = [c[0] for c in MobileAlert.TYPE_CHOICES]
            priorities = [MobileAlert.PRIORITY_LOW, MobileAlert.PRIORITY_MEDIUM,
                          MobileAlert.PRIORITY_MEDIUM, MobileAlert.PRIORITY_HIGH,
                          MobileAlert.PRIORITY_URGENT]
            statuses = [MobileAlert.STATUS_UNREAD, MobileAlert.STATUS_UNREAD,
                        MobileAlert.STATUS_READ, MobileAlert.STATUS_DISMISSED,
                        MobileAlert.STATUS_ACTIONED]
            for i in range(random.randint(8, 12)):
                MobileAlert.objects.create(
                    tenant=tenant, title=random.choice(ALERT_TITLES),
                    alert_type=random.choice(types), priority=random.choice(priorities),
                    status=random.choice(statuses), recipient=random.choice(REPS),
                    body="Tap to open the related record in the mobile app.",
                    notes="Push alert surfaced on the mobile dashboard.",
                )

        self.stdout.write(f"  seeded Module 16 data for '{tenant.slug}'")
