"""Seed Module 9 (Sales Enablement) demo data per tenant.

Idempotent — each model is skipped if data already exists for the tenant.
Depends on `seed_demo` having created the tenants first.
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.models import Tenant
from apps.enablement.models import (
    CallRecording, CompetitiveCard, ContentAsset, Playbook, TrainingRecord,
)

OWNERS = ["Sarah Connor", "James Miller", "Olivia Brown", "Noah Smith", "Enablement Team"]
REPS = ["Olivia Brown", "Noah Smith", "Liam Johnson", "Emma Davis", "Mason Lee"]
COACHES = ["Sarah Connor", "James Miller"]

CONTENT_ASSETS = [
    ("Platform Overview Deck", ContentAsset.TYPE_DECK, "intro,overview,pitch"),
    ("ROI One-Pager", ContentAsset.TYPE_ONE_PAGER, "roi,value,pricing"),
    ("Manufacturing Case Study", ContentAsset.TYPE_CASE_STUDY, "case-study,manufacturing"),
    ("Security & Compliance Whitepaper", ContentAsset.TYPE_WHITEPAPER, "security,compliance"),
    ("Product Demo Walkthrough", ContentAsset.TYPE_VIDEO, "demo,video,product"),
    ("Discovery Call Email Template", ContentAsset.TYPE_TEMPLATE, "email,discovery,template"),
    ("Executive Briefing Deck", ContentAsset.TYPE_DECK, "executive,c-level,pitch"),
    ("Integration Datasheet", ContentAsset.TYPE_ONE_PAGER, "integration,technical"),
]

PLAYBOOKS = [
    ("Cold Outreach Sequence", Playbook.STAGE_PROSPECTING, "VP of Sales"),
    ("Discovery Question Framework", Playbook.STAGE_DISCOVERY, "Economic Buyer"),
    ("Demo Best Practices", Playbook.STAGE_DEMO, "Technical Evaluator"),
    ("Negotiation & Pricing Plays", Playbook.STAGE_NEGOTIATION, "Procurement"),
    ("Closing & Mutual Action Plan", Playbook.STAGE_CLOSING, "Economic Buyer"),
    ("New Customer Onboarding", Playbook.STAGE_ONBOARDING, "Champion"),
]

COURSES = [
    ("Sales Methodology Foundations", TrainingRecord.KIND_COURSE, "Internal Academy"),
    ("Solution Selling Certification", TrainingRecord.KIND_CERTIFICATION, "MEDDIC Academy"),
    ("Negotiation Mastery Workshop", TrainingRecord.KIND_WORKSHOP, "SalesLabs"),
    ("New Hire Onboarding", TrainingRecord.KIND_ONBOARDING, "Internal Academy"),
    ("Product Deep Dive", TrainingRecord.KIND_COURSE, "Internal Academy"),
    ("Discovery Skills Bootcamp", TrainingRecord.KIND_WORKSHOP, "SalesLabs"),
]

CALL_TITLES = [
    ("Acme — Discovery Call", CallRecording.TYPE_DISCOVERY),
    ("Globex — Product Demo", CallRecording.TYPE_DEMO),
    ("Initech — Pricing Negotiation", CallRecording.TYPE_NEGOTIATION),
    ("Umbrella — Quarterly Check-in", CallRecording.TYPE_CHECK_IN),
    ("Hooli — Closing Call", CallRecording.TYPE_CLOSING),
    ("Stark — Discovery Call", CallRecording.TYPE_DISCOVERY),
    ("Wayne — Demo Follow-up", CallRecording.TYPE_DEMO),
]

COMPETITORS = [
    ("Rival CRM Co", "CRM Suite", CompetitiveCard.THREAT_HIGH),
    ("LegacySoft", "On-Prem Systems", CompetitiveCard.THREAT_LOW),
    ("CloudSell Inc", "Cloud SaaS", CompetitiveCard.THREAT_HIGH),
    ("StartScale", "Emerging SaaS", CompetitiveCard.THREAT_MEDIUM),
    ("Enterprise Giant", "Enterprise Suite", CompetitiveCard.THREAT_MEDIUM),
    ("BudgetTool", "Low-Cost Tools", CompetitiveCard.THREAT_LOW),
]


class Command(BaseCommand):
    help = "Seed Module 9 data (content, playbooks, training, call recordings, competitive cards)."

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.WARNING("No tenants found — run `seed_demo` first."))
            return
        for tenant in tenants:
            self._seed(tenant)
        self.stdout.write(self.style.SUCCESS("\nModule 9 data ready. Log in as a tenant admin to view it."))

    def _seed(self, tenant):
        today = timezone.localdate()
        counts = {}

        if not ContentAsset.objects.filter(tenant=tenant).exists():
            n = 0
            for title, asset_type, tags in CONTENT_ASSETS:
                status = random.choice([
                    ContentAsset.STATUS_PUBLISHED, ContentAsset.STATUS_PUBLISHED,
                    ContentAsset.STATUS_DRAFT, ContentAsset.STATUS_ARCHIVED,
                ])
                ContentAsset.objects.create(
                    tenant=tenant, title=title, asset_type=asset_type, status=status,
                    description=f"{title} for sales enablement.", tags=tags,
                    file_url="https://example.com/assets/" + title.lower().replace(" ", "-"),
                    owner=random.choice(OWNERS), view_count=random.randint(0, 350),
                )
                n += 1
            counts["content"] = n

        if not Playbook.objects.filter(tenant=tenant).exists():
            n = 0
            for title, stage, persona in PLAYBOOKS:
                status = random.choice([
                    Playbook.STATUS_ACTIVE, Playbook.STATUS_ACTIVE, Playbook.STATUS_DRAFT,
                ])
                Playbook.objects.create(
                    tenant=tenant, title=title, stage=stage, status=status, persona=persona,
                    summary=f"Guidance for the {stage} stage targeting {persona}.",
                    guidance="1. Set the agenda. 2. Ask the key questions. 3. Confirm next steps.",
                    owner=random.choice(OWNERS), version=f"{random.randint(1, 3)}.{random.randint(0, 5)}",
                )
                n += 1
            counts["playbooks"] = n

        if not TrainingRecord.objects.filter(tenant=tenant).exists():
            n = 0
            for course, kind, provider in COURSES:
                for rep in random.sample(REPS, k=random.randint(1, 2)):
                    status = random.choice([
                        TrainingRecord.STATUS_COMPLETED, TrainingRecord.STATUS_IN_PROGRESS,
                        TrainingRecord.STATUS_NOT_STARTED, TrainingRecord.STATUS_EXPIRED,
                    ])
                    score = None
                    if status == TrainingRecord.STATUS_COMPLETED:
                        score = Decimal(str(random.randint(70, 100)))
                    enrolled = today - timedelta(days=random.randint(10, 200))
                    TrainingRecord.objects.create(
                        tenant=tenant, course_name=course, rep_name=rep, kind=kind, status=status,
                        provider=provider, score=score, enrolled_on=enrolled,
                        due_on=enrolled + timedelta(days=30),
                        expires_on=enrolled + timedelta(days=365),
                        notes="Seed training record.",
                    )
                    n += 1
            counts["training"] = n

        if not CallRecording.objects.filter(tenant=tenant).exists():
            n = 0
            for title, call_type in CALL_TITLES:
                status = random.choice([
                    CallRecording.STATUS_PENDING, CallRecording.STATUS_REVIEWED,
                    CallRecording.STATUS_COACHED, CallRecording.STATUS_FLAGGED,
                ])
                score = None
                coach = ""
                notes = ""
                if status in (CallRecording.STATUS_REVIEWED, CallRecording.STATUS_COACHED):
                    score = Decimal(str(random.randint(60, 98)))
                    coach = random.choice(COACHES)
                    notes = "Strong rapport; tighten the discovery questions."
                CallRecording.objects.create(
                    tenant=tenant, title=title, rep_name=random.choice(REPS), coach_name=coach,
                    call_type=call_type, status=status,
                    duration_minutes=random.randint(15, 75),
                    recording_url="https://example.com/calls/" + title.lower().replace(" ", "-"),
                    score=score, coaching_notes=notes,
                    call_date=today - timedelta(days=random.randint(1, 90)),
                )
                n += 1
            counts["calls"] = n

        if not CompetitiveCard.objects.filter(tenant=tenant).exists():
            n = 0
            for competitor, category, threat in COMPETITORS:
                status = random.choice([
                    CompetitiveCard.STATUS_PUBLISHED, CompetitiveCard.STATUS_PUBLISHED,
                    CompetitiveCard.STATUS_DRAFT,
                ])
                CompetitiveCard.objects.create(
                    tenant=tenant, competitor_name=competitor, category=category,
                    threat_level=threat, status=status,
                    overview=f"{competitor} competes in the {category} space.",
                    our_strengths="Faster onboarding, deeper analytics, better support.",
                    their_strengths="Lower entry price, established brand recognition.",
                    objection_handling="Emphasise total cost of ownership and time-to-value.",
                    owner=random.choice(OWNERS),
                    last_updated_on=today - timedelta(days=random.randint(0, 120)),
                )
                n += 1
            counts["cards"] = n

        summary = ", ".join(f"{k}={v}" for k, v in counts.items()) or "already seeded"
        self.stdout.write(f"  seeded Module 9 data for '{tenant.slug}': {summary}")
