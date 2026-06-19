"""Seed Module 20 (System Administration & Security) demo data per tenant.

Idempotent — each model is skipped if data already exists for the tenant.
Depends on `seed_demo` having created the tenants first. Safe to re-run.
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.administration.models import (
    BackupJob, ComplianceItem, DataPrivacyRule, SecurityPolicy, SystemHealthMetric,
)
from apps.core.models import Tenant

POLICIES = [
    ("Strong Password Requirements", SecurityPolicy.TYPE_PASSWORD, SecurityPolicy.SEVERITY_HIGH),
    ("Mandatory MFA for Admins", SecurityPolicy.TYPE_MFA, SecurityPolicy.SEVERITY_CRITICAL),
    ("Idle Session Timeout", SecurityPolicy.TYPE_SESSION, SecurityPolicy.SEVERITY_MEDIUM),
    ("Office IP Allowlist", SecurityPolicy.TYPE_IP_ALLOWLIST, SecurityPolicy.SEVERITY_HIGH),
    ("Customer Data Retention", SecurityPolicy.TYPE_DATA_RETENTION, SecurityPolicy.SEVERITY_HIGH),
    ("Least-Privilege Access Control", SecurityPolicy.TYPE_ACCESS_CONTROL, SecurityPolicy.SEVERITY_CRITICAL),
    ("Password Rotation Cadence", SecurityPolicy.TYPE_PASSWORD, SecurityPolicy.SEVERITY_LOW),
    ("VPN Access Restriction", SecurityPolicy.TYPE_IP_ALLOWLIST, SecurityPolicy.SEVERITY_MEDIUM),
]

PRIVACY_RULES = [
    ("Lead PII Anonymisation", DataPrivacyRule.REGULATION_GDPR, DataPrivacyRule.CATEGORY_PII, DataPrivacyRule.ACTION_ANONYMIZE, 730),
    ("Payment Data Encryption", DataPrivacyRule.REGULATION_PCI_DSS, DataPrivacyRule.CATEGORY_FINANCIAL, DataPrivacyRule.ACTION_ENCRYPT, 365),
    ("Contact Record Retention", DataPrivacyRule.REGULATION_CCPA, DataPrivacyRule.CATEGORY_CONTACT, DataPrivacyRule.ACTION_RETAIN, 1095),
    ("Behavioral Log Deletion", DataPrivacyRule.REGULATION_GDPR, DataPrivacyRule.CATEGORY_BEHAVIORAL, DataPrivacyRule.ACTION_DELETE, 90),
    ("Health Data Restriction", DataPrivacyRule.REGULATION_HIPAA, DataPrivacyRule.CATEGORY_HEALTH, DataPrivacyRule.ACTION_RESTRICT, 2555),
    ("Financial Audit Retention", DataPrivacyRule.REGULATION_SOX, DataPrivacyRule.CATEGORY_FINANCIAL, DataPrivacyRule.ACTION_RETAIN, 2555),
    ("Internal PII Cleanup", DataPrivacyRule.REGULATION_INTERNAL, DataPrivacyRule.CATEGORY_PII, DataPrivacyRule.ACTION_DELETE, 180),
]

COMPLIANCE = [
    ("Access reviews completed quarterly", ComplianceItem.FRAMEWORK_SOC2),
    ("Encryption at rest for all databases", ComplianceItem.FRAMEWORK_ISO27001),
    ("Right-to-erasure workflow in place", ComplianceItem.FRAMEWORK_GDPR),
    ("Cardholder data scope segmented", ComplianceItem.FRAMEWORK_PCI_DSS),
    ("PHI access logging enabled", ComplianceItem.FRAMEWORK_HIPAA),
    ("Vendor risk assessments current", ComplianceItem.FRAMEWORK_SOC2),
    ("Incident response plan tested", ComplianceItem.FRAMEWORK_ISO27001),
    ("Data processing agreements signed", ComplianceItem.FRAMEWORK_GDPR),
]

OWNERS = ["Olivia Brown", "Noah Smith", "Sarah Connor", "James Miller", "Emma Davis", "Liam Wilson"]

BACKUPS = [
    ("Nightly Full Database", BackupJob.TYPE_FULL, "s3://backups/prod/db-full"),
    ("Hourly Incremental", BackupJob.TYPE_INCREMENTAL, "s3://backups/prod/db-incr"),
    ("Weekly Differential", BackupJob.TYPE_DIFFERENTIAL, "s3://backups/prod/db-diff"),
    ("VM Snapshot", BackupJob.TYPE_SNAPSHOT, "gcs://snapshots/app-vm"),
    ("File Storage Full", BackupJob.TYPE_FULL, "s3://backups/prod/files"),
    ("Config Snapshot", BackupJob.TYPE_SNAPSHOT, "azure://blob/config"),
    ("Audit Log Incremental", BackupJob.TYPE_INCREMENTAL, "s3://backups/prod/audit"),
    ("Disaster Recovery Replica", BackupJob.TYPE_FULL, "s3://dr-region/replica"),
]

METRICS = [
    ("API gateway CPU", SystemHealthMetric.CATEGORY_CPU, SystemHealthMetric.UNIT_PERCENT, Decimal("85")),
    ("Application memory usage", SystemHealthMetric.CATEGORY_MEMORY, SystemHealthMetric.UNIT_PERCENT, Decimal("90")),
    ("Primary disk utilisation", SystemHealthMetric.CATEGORY_DISK, SystemHealthMetric.UNIT_PERCENT, Decimal("80")),
    ("Database query latency", SystemHealthMetric.CATEGORY_DATABASE, SystemHealthMetric.UNIT_MS, Decimal("250")),
    ("API p95 response time", SystemHealthMetric.CATEGORY_API, SystemHealthMetric.UNIT_MS, Decimal("400")),
    ("Service uptime", SystemHealthMetric.CATEGORY_UPTIME, SystemHealthMetric.UNIT_PERCENT, Decimal("99")),
    ("Avg request response time", SystemHealthMetric.CATEGORY_RESPONSE_TIME, SystemHealthMetric.UNIT_MS, Decimal("300")),
    ("Background job backlog", SystemHealthMetric.CATEGORY_API, SystemHealthMetric.UNIT_COUNT, Decimal("500")),
]


class Command(BaseCommand):
    help = "Seed Module 20 data (security policies, privacy rules, compliance, backups, health metrics)."

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.WARNING("No tenants found — run `seed_demo` first."))
            return
        for tenant in tenants:
            self._seed(tenant)
        self.stdout.write(self.style.SUCCESS(
            "\nModule 20 data ready. Log in as a tenant admin to view it."))

    def _seed(self, tenant):
        today = timezone.localdate()

        # --- Security policies ---
        if not SecurityPolicy.objects.filter(tenant=tenant).exists():
            statuses = [SecurityPolicy.STATUS_ENFORCED, SecurityPolicy.STATUS_ENFORCED,
                        SecurityPolicy.STATUS_DRAFT, SecurityPolicy.STATUS_DISABLED]
            scopes = [c[0] for c in SecurityPolicy.SCOPE_CHOICES]
            for name, ptype, severity in POLICIES:
                SecurityPolicy.objects.create(
                    tenant=tenant, name=name, policy_type=ptype,
                    status=random.choice(statuses), scope=random.choice(scopes),
                    severity=severity,
                    last_reviewed=today - timedelta(days=random.randint(10, 200)),
                    description=f"{name} — governs how the workspace enforces security controls.",
                )

        # --- Data privacy rules ---
        if not DataPrivacyRule.objects.filter(tenant=tenant).exists():
            statuses = [DataPrivacyRule.STATUS_ACTIVE, DataPrivacyRule.STATUS_ACTIVE,
                        DataPrivacyRule.STATUS_INACTIVE, DataPrivacyRule.STATUS_DRAFT]
            for name, regulation, category, action, days in PRIVACY_RULES:
                DataPrivacyRule.objects.create(
                    tenant=tenant, name=name, regulation=regulation,
                    data_category=category, action=action,
                    status=random.choice(statuses), retention_days=days,
                    notes=f"{name} — applies a {action} action to {category} data.",
                )

        # --- Compliance items ---
        if not ComplianceItem.objects.filter(tenant=tenant).exists():
            statuses = [ComplianceItem.STATUS_COMPLIANT, ComplianceItem.STATUS_IN_PROGRESS,
                        ComplianceItem.STATUS_NON_COMPLIANT, ComplianceItem.STATUS_NOT_APPLICABLE]
            severities = [c[0] for c in ComplianceItem.SEVERITY_CHOICES]
            for title, framework in COMPLIANCE:
                ComplianceItem.objects.create(
                    tenant=tenant, title=title, framework=framework,
                    status=random.choice(statuses), owner=random.choice(OWNERS),
                    severity=random.choice(severities),
                    due_date=today + timedelta(days=random.randint(15, 180)),
                    last_audited=today - timedelta(days=random.randint(10, 120)),
                    notes="Control tracked for upcoming audit cycle.",
                )

        # --- Backup jobs (auto BKP-) ---
        if not BackupJob.objects.filter(tenant=tenant).exists():
            statuses = [BackupJob.STATUS_SCHEDULED, BackupJob.STATUS_SUCCESS,
                        BackupJob.STATUS_SUCCESS, BackupJob.STATUS_RUNNING,
                        BackupJob.STATUS_FAILED]
            for name, btype, location in BACKUPS:
                BackupJob.objects.create(
                    tenant=tenant, name=name, backup_type=btype,
                    status=random.choice(statuses), storage_location=location,
                    size_mb=(Decimal(random.randint(50, 50000))
                             + Decimal(str(round(random.random(), 2)))),
                    retention_days=random.choice([7, 30, 90, 365]),
                    scheduled_on=today - timedelta(days=random.randint(0, 60)),
                    notes="Automated backup run managed by the platform scheduler.",
                )

        # --- System health metrics ---
        if not SystemHealthMetric.objects.filter(tenant=tenant).exists():
            statuses = [SystemHealthMetric.STATUS_HEALTHY, SystemHealthMetric.STATUS_HEALTHY,
                        SystemHealthMetric.STATUS_WARNING, SystemHealthMetric.STATUS_CRITICAL,
                        SystemHealthMetric.STATUS_UNKNOWN]
            for metric_name, category, unit, threshold in METRICS:
                if unit == SystemHealthMetric.UNIT_PERCENT:
                    value = Decimal(str(round(random.uniform(20, 99), 2)))
                elif unit == SystemHealthMetric.UNIT_MS:
                    value = Decimal(str(round(random.uniform(50, 600), 2)))
                elif unit == SystemHealthMetric.UNIT_GB:
                    value = Decimal(str(round(random.uniform(10, 900), 2)))
                else:
                    value = Decimal(random.randint(0, 1200))
                SystemHealthMetric.objects.create(
                    tenant=tenant, metric_name=metric_name, category=category,
                    status=random.choice(statuses), value=value, unit=unit,
                    threshold=threshold,
                    recorded_on=today - timedelta(days=random.randint(0, 14)),
                    notes="Observed during routine platform monitoring.",
                )

        self.stdout.write(f"  seeded Module 20 data for '{tenant.slug}'")
