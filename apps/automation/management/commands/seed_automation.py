"""Seed Module 17 (Workflow & Process Automation) demo data per tenant.

Idempotent — each model is skipped if data already exists for the tenant.
Depends on `seed_demo` having created the tenants first. Safe to re-run.
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.automation.models import (
    AlertRule, ApprovalWorkflow, AssignmentRule, EnrichmentRule, ProcessFlow,
)
from apps.core.models import Tenant

PROCESS_FLOWS = [
    ("New Lead Welcome Sequence", ProcessFlow.TRIGGER_RECORD_CREATED, ProcessFlow.OBJECT_LEAD),
    ("Opportunity Stage Sync", ProcessFlow.TRIGGER_STAGE_CHANGED, ProcessFlow.OBJECT_OPPORTUNITY),
    ("Account Health Refresh", ProcessFlow.TRIGGER_SCHEDULED, ProcessFlow.OBJECT_ACCOUNT),
    ("Quote Approval Kickoff", ProcessFlow.TRIGGER_RECORD_UPDATED, ProcessFlow.OBJECT_QUOTE),
    ("Order Fulfilment Handoff", ProcessFlow.TRIGGER_RECORD_CREATED, ProcessFlow.OBJECT_ORDER),
    ("Lead Score Recalculation", ProcessFlow.TRIGGER_FIELD_CHANGED, ProcessFlow.OBJECT_LEAD),
    ("Manual Deal Review", ProcessFlow.TRIGGER_MANUAL, ProcessFlow.OBJECT_OPPORTUNITY),
]

ASSIGNMENT_RULES = [
    ("Inbound Lead Round Robin", AssignmentRule.ENTITY_LEAD, AssignmentRule.STRATEGY_ROUND_ROBIN),
    ("Enterprise Territory Routing", AssignmentRule.ENTITY_OPPORTUNITY, AssignmentRule.STRATEGY_TERRITORY),
    ("Support Case Load Balancing", AssignmentRule.ENTITY_CASE, AssignmentRule.STRATEGY_LOAD_BALANCED),
    ("Named Account Assignment", AssignmentRule.ENTITY_ACCOUNT, AssignmentRule.STRATEGY_MANUAL),
    ("Skill-Based Lead Routing", AssignmentRule.ENTITY_LEAD, AssignmentRule.STRATEGY_SKILL_BASED),
    ("Renewal Opp Round Robin", AssignmentRule.ENTITY_OPPORTUNITY, AssignmentRule.STRATEGY_ROUND_ROBIN),
]

APPROVAL_WORKFLOWS = [
    ("Volume Discount Approval", ApprovalWorkflow.TYPE_DISCOUNT, Decimal("10000")),
    ("Quote Sign-Off", ApprovalWorkflow.TYPE_QUOTE, Decimal("50000")),
    ("Master Contract Review", ApprovalWorkflow.TYPE_CONTRACT, Decimal("100000")),
    ("Travel Expense Approval", ApprovalWorkflow.TYPE_EXPENSE, Decimal("2500")),
    ("Large Deal Desk Review", ApprovalWorkflow.TYPE_DEAL, Decimal("250000")),
    ("Customer Refund Approval", ApprovalWorkflow.TYPE_REFUND, Decimal("5000")),
]

ALERT_RULES = [
    ("Stalled Deal Warning", AlertRule.CHANNEL_EMAIL, AlertRule.SEVERITY_WARNING),
    ("SLA Breach Critical", AlertRule.CHANNEL_SLACK, AlertRule.SEVERITY_CRITICAL),
    ("New Hot Lead Ping", AlertRule.CHANNEL_PUSH, AlertRule.SEVERITY_INFO),
    ("Quota At Risk", AlertRule.CHANNEL_IN_APP, AlertRule.SEVERITY_WARNING),
    ("Failed Payment Alert", AlertRule.CHANNEL_SMS, AlertRule.SEVERITY_CRITICAL),
    ("Webhook Sync Notice", AlertRule.CHANNEL_WEBHOOK, AlertRule.SEVERITY_INFO),
    ("Renewal Due Reminder", AlertRule.CHANNEL_EMAIL, AlertRule.SEVERITY_INFO),
]

ENRICHMENT_RULES = [
    ("Company Firmographics Enrich", EnrichmentRule.SOURCE_CLEARBIT, EnrichmentRule.OP_ENRICH, "company"),
    ("Contact Title Append", EnrichmentRule.SOURCE_ZOOMINFO, EnrichmentRule.OP_APPEND, "job_title"),
    ("Lead Dedupe by Email", EnrichmentRule.SOURCE_INTERNAL, EnrichmentRule.OP_DEDUPE, "email"),
    ("Phone Number Normalize", EnrichmentRule.SOURCE_INTERNAL, EnrichmentRule.OP_NORMALIZE, "phone"),
    ("Email Validation", EnrichmentRule.SOURCE_INTERNAL, EnrichmentRule.OP_VALIDATE, "email"),
    ("LinkedIn Profile Enrich", EnrichmentRule.SOURCE_LINKEDIN, EnrichmentRule.OP_ENRICH, "linkedin_url"),
    ("Manual Industry Tagging", EnrichmentRule.SOURCE_MANUAL, EnrichmentRule.OP_APPEND, "industry"),
]


class Command(BaseCommand):
    help = "Seed Module 17 data (process flows, assignment rules, approval workflows, alert rules, enrichment rules)."

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.WARNING("No tenants found — run `seed_demo` first."))
            return
        for tenant in tenants:
            self._seed(tenant)
        self.stdout.write(self.style.SUCCESS(
            "\nModule 17 data ready. Log in as a tenant admin to view it."))

    def _seed(self, tenant):
        now = timezone.now()

        # --- Process flows ---
        if not ProcessFlow.objects.filter(tenant=tenant).exists():
            statuses = [ProcessFlow.STATUS_ACTIVE, ProcessFlow.STATUS_ACTIVE,
                        ProcessFlow.STATUS_DRAFT, ProcessFlow.STATUS_PAUSED,
                        ProcessFlow.STATUS_ARCHIVED]
            for name, trigger, obj_type in PROCESS_FLOWS:
                status = random.choice(statuses)
                ProcessFlow.objects.create(
                    tenant=tenant, name=name, trigger_event=trigger, object_type=obj_type,
                    status=status, steps_count=random.randint(2, 9),
                    last_run=(now - timedelta(hours=random.randint(1, 240))
                              if status == ProcessFlow.STATUS_ACTIVE else None),
                    description=f"Automates the {name.lower()} when a {obj_type} is {trigger.replace('_', ' ')}.",
                )

        # --- Assignment rules ---
        if not AssignmentRule.objects.filter(tenant=tenant).exists():
            statuses = [AssignmentRule.STATUS_ACTIVE, AssignmentRule.STATUS_ACTIVE,
                        AssignmentRule.STATUS_INACTIVE, AssignmentRule.STATUS_DRAFT]
            for i, (name, entity, strategy) in enumerate(ASSIGNMENT_RULES):
                AssignmentRule.objects.create(
                    tenant=tenant, name=name, entity=entity, assign_strategy=strategy,
                    status=random.choice(statuses), priority=i + 1,
                    criteria=f"{entity} where region is set and owner is empty.",
                    assignee_pool="Olivia Brown, Noah Smith, Sarah Connor, James Miller",
                    notes=f"Routes new {entity} records using {strategy.replace('_', ' ')}.",
                )

        # --- Approval workflows ---
        if not ApprovalWorkflow.objects.filter(tenant=tenant).exists():
            statuses = [ApprovalWorkflow.STATUS_ACTIVE, ApprovalWorkflow.STATUS_ACTIVE,
                        ApprovalWorkflow.STATUS_INACTIVE, ApprovalWorkflow.STATUS_DRAFT]
            for name, atype, threshold in APPROVAL_WORKFLOWS:
                ApprovalWorkflow.objects.create(
                    tenant=tenant, name=name, approval_type=atype,
                    status=random.choice(statuses), threshold_amount=threshold,
                    steps_count=random.randint(1, 4),
                    escalation_hours=random.choice([12, 24, 48, 72]),
                    approvers="Sales Manager, RevOps Lead, Finance Director",
                    notes=f"Triggered for {atype} requests above ${threshold}.",
                )

        # --- Alert rules ---
        if not AlertRule.objects.filter(tenant=tenant).exists():
            statuses = [AlertRule.STATUS_ACTIVE, AlertRule.STATUS_ACTIVE,
                        AlertRule.STATUS_PAUSED, AlertRule.STATUS_DISABLED]
            frequencies = [c[0] for c in AlertRule.FREQUENCY_CHOICES]
            for name, channel, severity in ALERT_RULES:
                AlertRule.objects.create(
                    tenant=tenant, name=name, channel=channel, severity=severity,
                    status=random.choice(statuses),
                    trigger_condition=f"Fires when the {name.lower()} condition is met.",
                    recipients="owner@example.com, manager@example.com",
                    frequency=random.choice(frequencies),
                    notes=f"{severity.title()} alert delivered via {channel}.",
                )

        # --- Enrichment rules ---
        if not EnrichmentRule.objects.filter(tenant=tenant).exists():
            statuses = [EnrichmentRule.STATUS_ACTIVE, EnrichmentRule.STATUS_ACTIVE,
                        EnrichmentRule.STATUS_INACTIVE, EnrichmentRule.STATUS_DRAFT]
            for name, source, operation, field in ENRICHMENT_RULES:
                status = random.choice(statuses)
                EnrichmentRule.objects.create(
                    tenant=tenant, name=name, data_source=source, operation=operation,
                    status=status, target_field=field,
                    records_processed=random.randint(50, 25000),
                    success_rate=Decimal(str(round(random.uniform(72.0, 99.5), 2))),
                    last_run=(now - timedelta(hours=random.randint(1, 168))
                              if status == EnrichmentRule.STATUS_ACTIVE else None),
                    notes=f"{operation.title()} on {field} via {source}.",
                )

        self.stdout.write(f"  seeded Module 17 data for '{tenant.slug}'")
