"""Seed Module 1 (Lead Management) demo data per tenant.

Idempotent — each model is skipped if data already exists for the tenant.
Depends on `seed_demo` having created the tenants first. Parents (sources,
campaigns, leads) are created before children (scores, conversions).
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.models import Tenant
from apps.leads.models import (
    Lead, LeadConversion, LeadScore, LeadSource, NurtureCampaign,
)

SOURCES = [
    ("Website Contact Form", LeadSource.TYPE_WEB_FORM, LeadSource.ROUTING_ROUND_ROBIN),
    ("Spring Promo Landing Page", LeadSource.TYPE_LANDING_PAGE, LeadSource.ROUTING_TEAM),
    ("Customer Referrals", LeadSource.TYPE_REFERRAL, LeadSource.ROUTING_OWNER),
    ("Trade Show 2026", LeadSource.TYPE_EVENT, LeadSource.ROUTING_MANUAL),
    ("Google Ads", LeadSource.TYPE_PAID_ADS, LeadSource.ROUTING_ROUND_ROBIN),
    ("Outbound SDR List", LeadSource.TYPE_COLD_OUTREACH, LeadSource.ROUTING_OWNER),
    ("Partner Network", LeadSource.TYPE_PARTNER, LeadSource.ROUTING_TEAM),
]

CAMPAIGNS = [
    ("Welcome Drip", NurtureCampaign.CHANNEL_EMAIL, "Onboard new inbound leads"),
    ("Re-engagement Series", NurtureCampaign.CHANNEL_MULTI, "Reactivate dormant leads"),
    ("Webinar Follow-up", NurtureCampaign.CHANNEL_EMAIL, "Convert webinar attendees"),
    ("SMS Reminders", NurtureCampaign.CHANNEL_SMS, "Nudge demo no-shows"),
    ("Social Retargeting", NurtureCampaign.CHANNEL_SOCIAL, "Stay top of mind"),
    ("Product Education", NurtureCampaign.CHANNEL_EMAIL, "Educate trial users"),
]

FIRST_NAMES = ["Emma", "Liam", "Ava", "Mason", "Sophia", "Lucas", "Mia", "Ethan",
               "Isabella", "Logan", "Charlotte", "Jackson", "Amelia", "Aiden", "Harper"]
LAST_NAMES = ["Johnson", "Williams", "Garcia", "Martinez", "Davis", "Rodriguez",
              "Wilson", "Anderson", "Taylor", "Thomas", "Moore", "Jackson"]
COMPANIES = ["Northwind Traders", "Contoso Ltd", "Fabrikam Inc", "Tailspin Toys",
             "Adventure Works", "Wide World Importers", "Proseware Inc", "Coho Vineyard"]
TITLES = ["VP Sales", "Procurement Lead", "Operations Manager", "CTO", "Founder",
          "Marketing Director", "IT Manager", "Head of Growth"]
OWNERS = ["Olivia Brown", "Noah Smith", "James Miller", "Sarah Connor"]
REASONS = ["Strong demographic fit", "High email engagement", "Visited pricing page",
           "Requested a demo", "Low budget signal", "Decision maker identified"]


class Command(BaseCommand):
    help = "Seed Module 1 data (lead sources, campaigns, leads, scores, conversions)."

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.WARNING("No tenants found — run `seed_demo` first."))
            return
        for tenant in tenants:
            self._seed(tenant)
        self.stdout.write(self.style.SUCCESS("\nModule 1 data ready. Log in as a tenant admin to view it."))

    def _seed(self, tenant):
        today = timezone.localdate()

        # --- Parents: lead sources -----------------------------------------
        sources = []
        if not LeadSource.objects.filter(tenant=tenant).exists():
            for name, stype, routing in SOURCES:
                sources.append(LeadSource.objects.create(
                    tenant=tenant, name=name, source_type=stype, routing_rule=routing,
                    status=LeadSource.STATUS_ACTIVE,
                    default_owner=random.choice(OWNERS),
                    cost_per_lead=Decimal(str(random.choice([0, 5, 12, 25, 40]))),
                    description=f"Leads captured via {name}.",
                ))
        else:
            sources = list(LeadSource.objects.filter(tenant=tenant))

        # --- Parents: nurture campaigns ------------------------------------
        campaigns = []
        if not NurtureCampaign.objects.filter(tenant=tenant).exists():
            for name, channel, goal in CAMPAIGNS:
                status = random.choice([
                    NurtureCampaign.STATUS_RUNNING, NurtureCampaign.STATUS_SCHEDULED,
                    NurtureCampaign.STATUS_DRAFT, NurtureCampaign.STATUS_COMPLETED])
                campaigns.append(NurtureCampaign.objects.create(
                    tenant=tenant, name=name, channel=channel, status=status,
                    step_count=random.randint(3, 8), cadence_days=random.choice([2, 3, 5, 7]),
                    enrolled_count=random.randint(0, 250),
                    start_on=today - timedelta(days=random.randint(5, 60)),
                    end_on=today + timedelta(days=random.randint(10, 90)),
                    goal=goal,
                ))
        else:
            campaigns = list(NurtureCampaign.objects.filter(tenant=tenant))

        # --- Leads (children of sources + campaigns) -----------------------
        leads = []
        if not Lead.objects.filter(tenant=tenant).exists():
            for _ in range(random.randint(8, 12)):
                first = random.choice(FIRST_NAMES)
                last = random.choice(LAST_NAMES)
                status = random.choice([s for s, _ in Lead.STATUS_CHOICES])
                leads.append(Lead.objects.create(
                    tenant=tenant,
                    source=random.choice(sources) if sources else None,
                    campaign=random.choice(campaigns) if campaigns else None,
                    first_name=first, last_name=last,
                    company=random.choice(COMPANIES),
                    job_title=random.choice(TITLES),
                    email=f"{first.lower()}.{last.lower()}@example.com",
                    phone=f"+1-555-{random.randint(1000, 9999)}",
                    status=status,
                    rating=random.choice([r for r, _ in Lead.RATING_CHOICES]),
                    owner=random.choice(OWNERS),
                    estimated_value=Decimal(str(random.choice([2500, 5000, 12000, 30000, 75000]))),
                    captured_on=today - timedelta(days=random.randint(0, 90)),
                    notes="Imported during demo seeding.",
                ))
        else:
            leads = list(Lead.objects.filter(tenant=tenant))

        # --- Lead scores (children of leads) -------------------------------
        if not LeadScore.objects.filter(tenant=tenant).exists() and leads:
            for lead in random.sample(leads, min(len(leads), random.randint(6, len(leads)))):
                demo = random.randint(0, 50)
                behav = random.randint(0, 50)
                score = demo + behav
                if score >= 80:
                    grade = LeadScore.GRADE_A
                elif score >= 60:
                    grade = LeadScore.GRADE_B
                elif score >= 40:
                    grade = LeadScore.GRADE_C
                else:
                    grade = LeadScore.GRADE_D
                LeadScore.objects.create(
                    tenant=tenant, lead=lead, score=score, grade=grade,
                    scoring_model=random.choice([m for m, _ in LeadScore.MODEL_CHOICES]),
                    demographic_points=demo, behavioral_points=behav,
                    reason=random.choice(REASONS),
                    scored_on=today - timedelta(days=random.randint(0, 30)),
                )

        # --- Lead conversions (children of leads; auto-numbered CNV-) -------
        if not LeadConversion.objects.filter(tenant=tenant).exists() and leads:
            qualified = [lead for lead in leads
                         if lead.status in (Lead.STATUS_QUALIFIED, Lead.STATUS_CONVERTED)]
            pool = qualified or leads
            for lead in random.sample(pool, min(len(pool), random.randint(3, 6))):
                status = random.choice([s for s, _ in LeadConversion.STATUS_CHOICES])
                LeadConversion.objects.create(
                    tenant=tenant, lead=lead, status=status,
                    outcome=random.choice([o for o, _ in LeadConversion.OUTCOME_CHOICES]),
                    assigned_to=random.choice(OWNERS),
                    deal_value=Decimal(str(random.choice([5000, 15000, 40000, 90000]))),
                    handoff_notes="Routed to sales for follow-up.",
                )

        self.stdout.write(
            f"  seeded Module 1 data for '{tenant.slug}': "
            f"{len(sources)} sources, {len(campaigns)} campaigns, {len(leads)} leads")
