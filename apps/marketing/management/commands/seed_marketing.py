"""Seed Module 13 (Marketing Alignment & Attribution) demo data per tenant.

Idempotent — each model is skipped if data already exists for the tenant.
Depends on `seed_demo` having created the tenants first. Safe to re-run.
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.models import Tenant
from apps.marketing.models import (
    CampaignInfluence, CampaignPerformance, ContentEngagement, MarketingEvent, MQLHandoff,
)

CAMPAIGNS = [
    "Q1 Demand Gen", "Summer Product Launch", "Always-On Nurture", "Cloud Migration Push",
    "ABM Enterprise Blitz", "Holiday Retargeting", "Partner Co-Marketing", "Brand Awareness Wave",
    "Webinar Series 2026", "Free Trial Acquisition",
]

PERIODS = ["2026-Q1", "2026-Q2", "Jan 2026", "Feb 2026", "Mar 2026", "Apr 2026"]

LEADS = [
    "Olivia Brown", "Noah Smith", "Sarah Connor", "James Miller",
    "Emma Davis", "Liam Wilson", "Ava Martinez", "Lucas Anderson",
]

COMPANIES = [
    "Acme Corp", "Globex", "Initech", "Umbrella Inc", "Stark Industries",
    "Wayne Enterprises", "Soylent Co", "Hooli", "Pied Piper", "Vandelay",
]

SOURCES = ["Webinar", "Content download", "Paid search", "Trade show", "Referral", "Organic"]
SDRS = ["Mia Reyes", "Ethan Cole", "Priya Nair", "Tom Becker", "Hana Sato"]

CONTENT = [
    "The State of Sales 2026", "ROI Calculator Guide", "Customer Success Story: Acme",
    "Migration Playbook", "Buyer's Guide to CRM", "Product Demo Replay",
    "Pipeline Velocity eBook", "Competitive Battlecard", "Quarterly Trends Report",
    "Onboarding Datasheet",
]

EVENTS = [
    "SalesOps Summit 2026", "Product Deep-Dive Webinar", "Regional Trade Show",
    "Enablement Workshop", "Virtual Customer Day", "Industry Conference Booth",
    "Partner Roadshow", "Lunch & Learn Series",
]

LOCATIONS = ["San Francisco, CA", "London, UK", "New York, NY", "Online", "Austin, TX", "Berlin, DE"]


class Command(BaseCommand):
    help = "Seed Module 13 data (campaign influence, MQL handoffs, performance, content, events)."

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.WARNING("No tenants found — run `seed_demo` first."))
            return
        for tenant in tenants:
            self._seed(tenant)
        self.stdout.write(self.style.SUCCESS(
            "\nModule 13 data ready. Log in as a tenant admin to view it."))

    def _seed(self, tenant):
        today = timezone.localdate()

        # --- Campaign influence & attribution ---
        if not CampaignInfluence.objects.filter(tenant=tenant).exists():
            models = [c[0] for c in CampaignInfluence.MODEL_TYPE_CHOICES]
            for name in random.sample(CAMPAIGNS, k=random.randint(6, len(CAMPAIGNS))):
                CampaignInfluence.objects.create(
                    tenant=tenant, campaign_name=name,
                    model_type=random.choice(models),
                    influenced_amount=Decimal(random.randint(25000, 850000)),
                    opportunities_count=random.randint(3, 60),
                    attribution_pct=Decimal(str(round(random.uniform(5, 95), 2))),
                    period_label=random.choice(PERIODS),
                    recorded_on=today - timedelta(days=random.randint(1, 180)),
                    notes="Multi-touch attribution rollup for the period.",
                )

        # --- MQL-to-SQL handoffs ---
        if not MQLHandoff.objects.filter(tenant=tenant).exists():
            statuses = [c[0] for c in MQLHandoff.STATUS_CHOICES]
            for i in range(random.randint(8, 12)):
                MQLHandoff.objects.create(
                    tenant=tenant, lead_name=random.choice(LEADS),
                    company=random.choice(COMPANIES),
                    mql_score=random.randint(20, 100),
                    status=random.choice(statuses),
                    source=random.choice(SOURCES),
                    handed_to=random.choice(SDRS),
                    handoff_date=today - timedelta(days=random.randint(1, 120)),
                    notes="Lead handed from marketing to sales for qualification.",
                )

        # --- Campaign performance integration ---
        if not CampaignPerformance.objects.filter(tenant=tenant).exists():
            channels = [c[0] for c in CampaignPerformance.CHANNEL_CHOICES]
            statuses = [CampaignPerformance.STATUS_PLANNED, CampaignPerformance.STATUS_ACTIVE,
                        CampaignPerformance.STATUS_ACTIVE, CampaignPerformance.STATUS_PAUSED,
                        CampaignPerformance.STATUS_COMPLETED]
            for name in random.sample(CAMPAIGNS, k=random.randint(6, len(CAMPAIGNS))):
                spend = Decimal(random.randint(2000, 90000))
                revenue = (spend * Decimal(str(round(random.uniform(0.5, 8.0), 2)))).quantize(Decimal("0.01"))
                roi = ((revenue - spend) / spend * Decimal("100")).quantize(Decimal("0.01")) if spend else Decimal("0")
                CampaignPerformance.objects.create(
                    tenant=tenant, campaign_name=name,
                    channel=random.choice(channels), status=random.choice(statuses),
                    spend=spend, leads_generated=random.randint(10, 800),
                    revenue_influenced=revenue, roi=roi,
                    start_date=today - timedelta(days=random.randint(10, 300)),
                    notes="Channel campaign performance synced from ad platform.",
                )

        # --- Content performance & engagement ---
        if not ContentEngagement.objects.filter(tenant=tenant).exists():
            types = [c[0] for c in ContentEngagement.CONTENT_TYPE_CHOICES]
            for title in random.sample(CONTENT, k=random.randint(6, len(CONTENT))):
                views = random.randint(150, 25000)
                downloads = random.randint(0, views // 2)
                conversions = random.randint(0, max(1, downloads // 3))
                ContentEngagement.objects.create(
                    tenant=tenant, content_title=title,
                    content_type=random.choice(types),
                    views=views, downloads=downloads,
                    avg_time_seconds=random.randint(30, 600),
                    conversions=conversions,
                    engagement_score=Decimal(str(round(random.uniform(10, 99), 2))),
                    published_on=today - timedelta(days=random.randint(5, 365)),
                )

        # --- Event & webinar management ---
        if not MarketingEvent.objects.filter(tenant=tenant).exists():
            etypes = [c[0] for c in MarketingEvent.EVENT_TYPE_CHOICES]
            statuses = [MarketingEvent.STATUS_PLANNED, MarketingEvent.STATUS_REGISTRATION_OPEN,
                        MarketingEvent.STATUS_LIVE, MarketingEvent.STATUS_COMPLETED,
                        MarketingEvent.STATUS_COMPLETED, MarketingEvent.STATUS_CANCELED]
            for name in random.sample(EVENTS, k=random.randint(6, len(EVENTS))):
                registrations = random.randint(20, 1500)
                attendees = random.randint(0, registrations)
                MarketingEvent.objects.create(
                    tenant=tenant, name=name,
                    event_type=random.choice(etypes), status=random.choice(statuses),
                    event_date=today + timedelta(days=random.randint(-120, 90)),
                    registrations=registrations, attendees=attendees,
                    leads_captured=random.randint(0, attendees),
                    location=random.choice(LOCATIONS),
                    notes="Event managed through the marketing calendar.",
                )

        self.stdout.write(f"  seeded Module 13 data for '{tenant.slug}'")
