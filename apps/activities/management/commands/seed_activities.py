"""Seed Module 8 (Sales Activity & Task Management) demo data per tenant.

Idempotent — each model is skipped if data already exists for the tenant.
Depends on `seed_demo` having created the tenants first.
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.activities.models import Activity, EmailLog, Meeting, SalesPlan, SalesTask
from apps.core.models import Tenant

CONTACTS = [
    ("John Carter", "Northwind Traders"),
    ("Maria Lopez", "Contoso Ltd"),
    ("David Kim", "Fabrikam Inc"),
    ("Emma Watson", "Tailspin Toys"),
    ("Liam Nguyen", "Adventure Works"),
    ("Sophia Patel", "Wide World Importers"),
    ("Oliver Smith", "Proseware Inc"),
    ("Ava Johnson", "Litware Inc"),
]

OWNERS = ["Sarah Connor", "James Miller", "Olivia Brown", "Noah Smith"]

ACTIVITY_SUBJECTS = [
    "Intro call with prospect",
    "Discovery call on requirements",
    "Sent pricing proposal",
    "Product demo walkthrough",
    "Follow-up on quote",
    "Quarterly check-in",
    "Onsite visit and assessment",
    "Renewal discussion",
    "Cold outreach call",
    "Contract negotiation call",
]

TASK_TITLES = [
    "Follow up on proposal",
    "Send contract for signature",
    "Prepare demo environment",
    "Call back to confirm meeting",
    "Update CRM notes",
    "Share case study",
    "Schedule onboarding session",
    "Review pricing with manager",
    "Send recap email",
    "Qualify new inbound lead",
]

MEETING_TITLES = [
    "Discovery session",
    "Solution demo",
    "Proposal review",
    "Contract negotiation",
    "Quarterly business review",
    "Kickoff meeting",
    "Technical deep-dive",
    "Pricing discussion",
]

EMAIL_SUBJECTS = [
    "Following up on our call",
    "Your custom proposal is ready",
    "Quick question about your timeline",
    "Demo recording and next steps",
    "Pricing breakdown attached",
    "Checking in for Q3 planning",
    "Re: Contract terms",
    "Introduction and overview",
]

PLAN_TITLES = [
    "Week 1 outreach sprint",
    "Daily prospecting plan",
    "Monthly pipeline push",
    "Enterprise account focus week",
    "Renewals and upsell week",
    "New-logo acquisition plan",
]


class Command(BaseCommand):
    help = "Seed Module 8 data (activities, tasks, meetings, emails, sales plans)."

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.WARNING("No tenants found — run `seed_demo` first."))
            return
        for tenant in tenants:
            self._seed(tenant)
        self.stdout.write(self.style.SUCCESS(
            "\nModule 8 data ready. Log in as a tenant admin to view it."))

    def _seed(self, tenant):
        today = timezone.localdate()

        activities = []
        if not Activity.objects.filter(tenant=tenant).exists():
            for i in range(random.randint(8, 12)):
                contact, company = random.choice(CONTACTS)
                act = Activity.objects.create(
                    tenant=tenant,
                    subject=random.choice(ACTIVITY_SUBJECTS),
                    activity_type=random.choice([c[0] for c in Activity.TYPE_CHOICES]),
                    direction=random.choice([c[0] for c in Activity.DIRECTION_CHOICES]),
                    outcome=random.choice([c[0] for c in Activity.OUTCOME_CHOICES]),
                    contact_name=contact, company_name=company,
                    owner_name=random.choice(OWNERS),
                    duration_minutes=random.choice([5, 10, 15, 30, 45, 60]),
                    activity_date=today - timedelta(days=random.randint(0, 45)),
                    notes="Logged from the activity tracker.",
                )
                activities.append(act)
        else:
            activities = list(Activity.objects.filter(tenant=tenant)[:12])

        if not SalesTask.objects.filter(tenant=tenant).exists():
            for i in range(random.randint(8, 12)):
                status = random.choice([c[0] for c in SalesTask.STATUS_CHOICES])
                linked = random.choice(activities) if activities and random.random() < 0.5 else None
                SalesTask.objects.create(
                    tenant=tenant, activity=linked,
                    title=random.choice(TASK_TITLES),
                    description="Auto-generated demo task.",
                    priority=random.choice([c[0] for c in SalesTask.PRIORITY_CHOICES]),
                    status=status,
                    assigned_to=random.choice(OWNERS),
                    related_to=random.choice([c[1] for c in CONTACTS]),
                    due_date=today + timedelta(days=random.randint(-10, 20)),
                    reminder_date=today + timedelta(days=random.randint(-12, 18)),
                )

        if not Meeting.objects.filter(tenant=tenant).exists():
            for i in range(random.randint(6, 10)):
                contact, company = random.choice(CONTACTS)
                start_h = random.randint(8, 16)
                Meeting.objects.create(
                    tenant=tenant,
                    title=random.choice(MEETING_TITLES),
                    meeting_type=random.choice([c[0] for c in Meeting.TYPE_CHOICES]),
                    location_type=random.choice([c[0] for c in Meeting.LOCATION_CHOICES]),
                    status=random.choice([c[0] for c in Meeting.STATUS_CHOICES]),
                    attendees=f"{contact}, {random.choice(OWNERS)}",
                    location=random.choice(["Zoom", "Google Meet", "HQ Boardroom", "Client office"]),
                    organizer_name=random.choice(OWNERS),
                    scheduled_date=today + timedelta(days=random.randint(-15, 25)),
                    start_time=f"{start_h:02d}:00",
                    end_time=f"{start_h + 1:02d}:00",
                    agenda=f"Agenda for {company}.",
                )

        if not EmailLog.objects.filter(tenant=tenant).exists():
            domain = (tenant.slug or "demo").lower()
            for i in range(random.randint(8, 12)):
                contact, company = random.choice(CONTACTS)
                status = random.choice([c[0] for c in EmailLog.STATUS_CHOICES])
                opened = status in {EmailLog.STATUS_OPENED, EmailLog.STATUS_CLICKED, EmailLog.STATUS_REPLIED}
                linked = random.choice(activities) if activities and random.random() < 0.4 else None
                EmailLog.objects.create(
                    tenant=tenant, activity=linked,
                    subject=random.choice(EMAIL_SUBJECTS),
                    direction=random.choice([c[0] for c in EmailLog.DIRECTION_CHOICES]),
                    status=status,
                    from_email=f"sales@{domain}.example.com",
                    to_email=f"{contact.split()[0].lower()}@example.com",
                    open_count=random.randint(1, 5) if opened else 0,
                    click_count=random.randint(0, 3) if status == EmailLog.STATUS_CLICKED else 0,
                    body="Demo email body for tracking.",
                )

        if not SalesPlan.objects.filter(tenant=tenant).exists():
            for i in range(random.randint(6, 9)):
                period = random.choice([c[0] for c in SalesPlan.PERIOD_CHOICES])
                span = {"daily": 1, "weekly": 7, "monthly": 30}[period]
                start = today - timedelta(days=random.randint(0, 40))
                SalesPlan.objects.create(
                    tenant=tenant,
                    title=random.choice(PLAN_TITLES),
                    owner_name=random.choice(OWNERS),
                    period_type=period,
                    status=random.choice([c[0] for c in SalesPlan.STATUS_CHOICES]),
                    start_date=start,
                    end_date=start + timedelta(days=span),
                    target_calls=random.choice([10, 20, 30, 50]),
                    target_meetings=random.choice([3, 5, 8, 12]),
                    revenue_goal=Decimal(random.choice([5000, 10000, 25000, 50000])),
                    objectives="Hit the weekly activity and revenue targets.",
                )

        self.stdout.write(f"  seeded Module 8 data for '{tenant.slug}'")
