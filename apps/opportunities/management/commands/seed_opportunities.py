"""Seed Module 2 (Opportunity & Pipeline Management) demo data per tenant.

Idempotent — each model is skipped if data already exists for the tenant.
Depends on `seed_demo` having created the tenants first. Parents (pipeline stages,
opportunities) are created before children (activities, competitors, collaborators).
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.models import Tenant
from apps.opportunities.models import (
    Competitor, DealCollaborator, Opportunity, OpportunityActivity, PipelineStage,
)

# (name, order, probability, stage_type)
STAGES = [
    ("Qualification", 1, 10, PipelineStage.TYPE_OPEN),
    ("Needs Analysis", 2, 25, PipelineStage.TYPE_OPEN),
    ("Proposal", 3, 50, PipelineStage.TYPE_OPEN),
    ("Negotiation", 4, 75, PipelineStage.TYPE_OPEN),
    ("Closed Won", 5, 100, PipelineStage.TYPE_WON),
    ("Closed Lost", 6, 0, PipelineStage.TYPE_LOST),
]

DEAL_NAMES = [
    "Enterprise CRM Rollout", "Cloud Migration Phase 2", "Annual Platform Renewal",
    "Data Warehouse Expansion", "Security Suite Upgrade", "Mobile App Licensing",
    "Analytics Add-on", "Support Tier Upgrade", "Multi-Region Deployment",
    "API Gateway Implementation", "Onboarding Services Package", "Custom Integration Build",
]

ACCOUNTS = [
    "Northwind Traders", "Contoso Ltd", "Fabrikam Inc", "Adventure Works",
    "Tailspin Toys", "Wingtip Toys", "Litware Inc", "Proseware Inc",
]

OWNERS = ["Sarah Connor", "James Miller", "Olivia Brown", "Noah Smith"]
SOURCES = ["Inbound", "Outbound", "Partner referral", "Trade show", "Webinar", "Existing customer"]

ACTIVITY_SUBJECTS = [
    "Discovery call with stakeholders", "Sent pricing proposal", "Technical deep-dive demo",
    "Follow-up email on next steps", "Contract review meeting", "Budget confirmation call",
    "Security questionnaire returned", "Executive alignment session",
]

COMPETITORS = ["Salesforce", "HubSpot", "Microsoft Dynamics", "Zoho", "Pipedrive", "In-house build"]

COLLABORATORS = [
    ("Emma Wilson", DealCollaborator.ROLE_SALES_ENG),
    ("Liam Davis", DealCollaborator.ROLE_EXEC_SPONSOR),
    ("Ava Martinez", DealCollaborator.ROLE_PRODUCT),
    ("Mason Lee", DealCollaborator.ROLE_LEGAL),
    ("Sophia Clark", DealCollaborator.ROLE_SUPPORT),
]


class Command(BaseCommand):
    help = "Seed Module 2 data (pipeline stages, opportunities, activities, competitors, collaborators)."

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.WARNING("No tenants found — run `seed_demo` first."))
            return
        for tenant in tenants:
            self._seed(tenant)
        self.stdout.write(self.style.SUCCESS(
            "\nModule 2 data ready. Log in as a tenant admin to view it."))

    def _seed(self, tenant):
        # ---- Pipeline stages (parents) ----
        if not PipelineStage.objects.filter(tenant=tenant).exists():
            for name, order, prob, stype in STAGES:
                PipelineStage.objects.create(
                    tenant=tenant, name=name, order=order, probability=prob,
                    stage_type=stype, is_active=True,
                    description=f"{name} stage of the sales pipeline.")
        stages = list(PipelineStage.objects.filter(tenant=tenant))
        open_stages = [s for s in stages if s.stage_type == PipelineStage.TYPE_OPEN]

        # ---- Opportunities (parents for activities/competitors/collaborators) ----
        if not Opportunity.objects.filter(tenant=tenant).exists():
            today = timezone.localdate()
            for i in range(random.randint(8, 12)):
                stage = random.choice(stages)
                if stage.stage_type == PipelineStage.TYPE_WON:
                    status = Opportunity.STATUS_WON
                elif stage.stage_type == PipelineStage.TYPE_LOST:
                    status = Opportunity.STATUS_LOST
                else:
                    status = Opportunity.STATUS_OPEN
                Opportunity.objects.create(
                    tenant=tenant,
                    name=random.choice(DEAL_NAMES),
                    account_name=random.choice(ACCOUNTS),
                    stage=stage,
                    status=status,
                    priority=random.choice([c[0] for c in Opportunity.PRIORITY_CHOICES]),
                    forecast_category=random.choice([c[0] for c in Opportunity.FORECAST_CHOICES]),
                    amount=Decimal(str(random.randint(5, 250) * 1000)),
                    probability=stage.probability,
                    owner_name=random.choice(OWNERS),
                    source=random.choice(SOURCES),
                    expected_close_date=today + timedelta(days=random.randint(-30, 120)),
                    description="Auto-seeded opportunity for demo purposes.")
        opportunities = list(Opportunity.objects.filter(tenant=tenant))

        # ---- Opportunity activities (children) ----
        if not OpportunityActivity.objects.filter(tenant=tenant).exists():
            today = timezone.localdate()
            for _ in range(random.randint(8, 12)):
                opp = random.choice(opportunities)
                OpportunityActivity.objects.create(
                    tenant=tenant, opportunity=opp,
                    subject=random.choice(ACTIVITY_SUBJECTS),
                    activity_type=random.choice([c[0] for c in OpportunityActivity.TYPE_CHOICES]),
                    outcome=random.choice([c[0] for c in OpportunityActivity.OUTCOME_CHOICES]),
                    performed_by=opp.owner_name or random.choice(OWNERS),
                    activity_date=today - timedelta(days=random.randint(0, 45)),
                    notes="Logged during the sales process.")

        # ---- Competitors (children) ----
        if not Competitor.objects.filter(tenant=tenant).exists():
            for _ in range(random.randint(6, 10)):
                opp = random.choice(opportunities)
                Competitor.objects.create(
                    tenant=tenant, opportunity=opp,
                    name=random.choice(COMPETITORS),
                    threat_level=random.choice([c[0] for c in Competitor.THREAT_CHOICES]),
                    status=random.choice([c[0] for c in Competitor.STATUS_CHOICES]),
                    strengths="Established brand and broad feature set.",
                    weaknesses="Higher total cost of ownership.",
                    our_strategy="Emphasise faster time-to-value and dedicated support.")

        # ---- Deal collaborators (children) ----
        if not DealCollaborator.objects.filter(tenant=tenant).exists():
            for _ in range(random.randint(6, 10)):
                opp = random.choice(opportunities)
                name, role = random.choice(COLLABORATORS)
                DealCollaborator.objects.create(
                    tenant=tenant, opportunity=opp,
                    member_name=name,
                    email=f"{name.split()[0].lower()}@{tenant.slug}.example.com",
                    team_role=role,
                    status=random.choice([c[0] for c in DealCollaborator.STATUS_CHOICES]),
                    contribution="Supporting the deal team on this opportunity.")

        self.stdout.write(f"  seeded Module 2 data for '{tenant.slug}'")
