"""Seed Module 18 (Integration & API Hub) demo data per tenant.

Idempotent — each model is skipped if data already exists for the tenant.
Depends on `seed_demo` having created the tenants first. Safe to re-run.
"""
import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.models import Tenant
from apps.integrations.models import (
    ApiKey, Connector, SyncJob, SyncLog, Webhook,
)

CONNECTORS = [
    ("NetSuite ERP", Connector.CATEGORY_ERP, "Oracle NetSuite"),
    ("SAP S/4HANA", Connector.CATEGORY_ERP, "SAP"),
    ("HubSpot Marketing", Connector.CATEGORY_MARKETING, "HubSpot"),
    ("Marketo Engage", Connector.CATEGORY_MARKETING, "Adobe"),
    ("Slack Workspace", Connector.CATEGORY_COMMUNICATION, "Slack"),
    ("Microsoft Teams", Connector.CATEGORY_COMMUNICATION, "Microsoft"),
    ("Power BI", Connector.CATEGORY_BI, "Microsoft"),
    ("Tableau Cloud", Connector.CATEGORY_BI, "Salesforce"),
    ("DocuSign", Connector.CATEGORY_ESIGNATURE, "DocuSign"),
    ("Google Drive", Connector.CATEGORY_STORAGE, "Google"),
]

JOB_NAMES = [
    "Nightly account sync", "Contact upsert", "Deal pipeline export",
    "Lead enrichment pull", "Invoice push to ERP", "Campaign metrics import",
    "Document status sync", "Order fulfilment feed", "Inventory snapshot",
    "Activity timeline export",
]

LOG_MESSAGES = [
    "Run completed without errors.",
    "Rate limit reached — retrying with backoff.",
    "Upstream returned 502, will retry next cycle.",
    "Mapped 1,240 records successfully.",
    "Skipped 3 malformed rows during import.",
    "Authentication token refreshed.",
    "Partial sync: connection reset by peer.",
    "Delta sync finished, no changes detected.",
]

WEBHOOKS = [
    ("Deal won notifier", "https://hooks.example.com/deal-won"),
    ("CRM record sync", "https://api.partner.example.com/ingest"),
    ("Slack alert relay", "https://hooks.slack.com/services/T000/B000"),
    ("Billing event push", "https://billing.example.com/webhook"),
    ("Audit stream", "https://siem.example.com/collect"),
    ("Document signed callback", "https://docs.example.com/callback"),
]

API_KEYS = [
    ("Reporting service", "read:deals read:accounts"),
    ("Mobile app key", "read:contacts write:activities"),
    ("Partner portal", "read:quotes read:invoices"),
    ("CI pipeline", "read:* write:webhooks"),
    ("Analytics ingest", "read:reports"),
    ("Zapier integration", "read:leads write:leads"),
]


class Command(BaseCommand):
    help = "Seed Module 18 data (connectors, sync jobs, logs, webhooks, API keys)."

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.WARNING("No tenants found — run `seed_demo` first."))
            return
        for tenant in tenants:
            self._seed(tenant)
        self.stdout.write(self.style.SUCCESS(
            "\nModule 18 data ready. Log in as a tenant admin to view it."))

    def _seed(self, tenant):
        now = timezone.now()
        today = timezone.localdate()

        # --- Connectors (parent) ---
        connectors = []
        if not Connector.objects.filter(tenant=tenant).exists():
            statuses = [Connector.STATUS_CONNECTED, Connector.STATUS_CONNECTED,
                        Connector.STATUS_DISCONNECTED, Connector.STATUS_ERROR,
                        Connector.STATUS_CONFIGURING]
            auth_types = [c[0] for c in Connector.AUTH_CHOICES]
            chosen = random.sample(CONNECTORS, k=random.randint(6, len(CONNECTORS)))
            for name, category, provider in chosen:
                status = random.choice(statuses)
                connector = Connector.objects.create(
                    tenant=tenant, name=name, category=category, provider=provider,
                    status=status, auth_type=random.choice(auth_types),
                    last_sync=(now - timedelta(hours=random.randint(1, 240))
                               if status == Connector.STATUS_CONNECTED else None),
                    notes=f"{provider} {name} integration for the workspace.",
                )
                connectors.append(connector)
        else:
            connectors = list(Connector.objects.filter(tenant=tenant))

        # --- Sync jobs ---
        jobs = []
        if not SyncJob.objects.filter(tenant=tenant).exists() and connectors:
            directions = [c[0] for c in SyncJob.DIRECTION_CHOICES]
            schedules = [c[0] for c in SyncJob.SCHEDULE_CHOICES]
            statuses = [SyncJob.STATUS_SCHEDULED, SyncJob.STATUS_SUCCESS,
                        SyncJob.STATUS_SUCCESS, SyncJob.STATUS_RUNNING,
                        SyncJob.STATUS_FAILED, SyncJob.STATUS_PAUSED]
            for name in random.sample(JOB_NAMES, k=random.randint(6, len(JOB_NAMES))):
                status = random.choice(statuses)
                job = SyncJob.objects.create(
                    tenant=tenant, connector=random.choice(connectors), name=name,
                    direction=random.choice(directions), status=status,
                    schedule=random.choice(schedules),
                    records_synced=random.randint(0, 25000),
                    last_run=(now - timedelta(hours=random.randint(1, 72))
                              if status != SyncJob.STATUS_SCHEDULED else None),
                    notes="Automated data exchange task.",
                )
                jobs.append(job)
        else:
            jobs = list(SyncJob.objects.filter(tenant=tenant))

        # --- Sync logs ---
        if not SyncLog.objects.filter(tenant=tenant).exists() and jobs:
            levels = [SyncLog.LEVEL_INFO, SyncLog.LEVEL_INFO, SyncLog.LEVEL_SUCCESS,
                      SyncLog.LEVEL_WARNING, SyncLog.LEVEL_ERROR]
            for i in range(random.randint(8, 12)):
                SyncLog.objects.create(
                    tenant=tenant, job=random.choice(jobs),
                    level=random.choice(levels), message=random.choice(LOG_MESSAGES),
                    records_affected=random.randint(0, 5000),
                    duration_ms=random.randint(80, 45000),
                    occurred_at=now - timedelta(hours=random.randint(1, 200)),
                )

        # --- Webhooks ---
        if not Webhook.objects.filter(tenant=tenant).exists():
            events = [c[0] for c in Webhook.EVENT_CHOICES]
            methods = [c[0] for c in Webhook.METHOD_CHOICES]
            statuses = [Webhook.STATUS_ACTIVE, Webhook.STATUS_ACTIVE,
                        Webhook.STATUS_INACTIVE, Webhook.STATUS_FAILED]
            for name, url in random.sample(WEBHOOKS, k=random.randint(4, len(WEBHOOKS))):
                status = random.choice(statuses)
                Webhook.objects.create(
                    tenant=tenant, name=name, target_url=url,
                    event_type=random.choice(events), http_method=random.choice(methods),
                    status=status,
                    secret=f"whsec_{random.randint(10**11, 10**12 - 1)}",
                    failure_count=random.randint(0, 7) if status == Webhook.STATUS_FAILED else 0,
                    last_triggered=(now - timedelta(hours=random.randint(1, 120))
                                    if status != Webhook.STATUS_INACTIVE else None),
                    notes="Outbound event subscription.",
                )

        # --- API keys ---
        if not ApiKey.objects.filter(tenant=tenant).exists():
            environments = [c[0] for c in ApiKey.ENVIRONMENT_CHOICES]
            statuses = [ApiKey.STATUS_ACTIVE, ApiKey.STATUS_ACTIVE,
                        ApiKey.STATUS_REVOKED, ApiKey.STATUS_EXPIRED]
            for name, scopes in random.sample(API_KEYS, k=random.randint(4, len(API_KEYS))):
                status = random.choice(statuses)
                ApiKey.objects.create(
                    tenant=tenant, name=name, environment=random.choice(environments),
                    scopes=scopes, status=status,
                    last_used=(now - timedelta(hours=random.randint(1, 300))
                               if status == ApiKey.STATUS_ACTIVE else None),
                    expires_on=today + timedelta(days=random.randint(30, 365)),
                    notes="Programmatic access credential.",
                )

        self.stdout.write(f"  seeded Module 18 data for '{tenant.slug}'")
