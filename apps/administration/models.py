from django.db import models, transaction
from django.utils import timezone


class SecurityPolicy(models.Model):
    """Data Security & Privacy — a security/governance policy enforced across the workspace."""

    TYPE_PASSWORD = "password"
    TYPE_MFA = "mfa"
    TYPE_SESSION = "session"
    TYPE_IP_ALLOWLIST = "ip_allowlist"
    TYPE_DATA_RETENTION = "data_retention"
    TYPE_ACCESS_CONTROL = "access_control"
    POLICY_TYPE_CHOICES = [
        (TYPE_PASSWORD, "Password"),
        (TYPE_MFA, "Multi-factor auth"),
        (TYPE_SESSION, "Session"),
        (TYPE_IP_ALLOWLIST, "IP allowlist"),
        (TYPE_DATA_RETENTION, "Data retention"),
        (TYPE_ACCESS_CONTROL, "Access control"),
    ]

    STATUS_ENFORCED = "enforced"
    STATUS_DRAFT = "draft"
    STATUS_DISABLED = "disabled"
    STATUS_CHOICES = [
        (STATUS_ENFORCED, "Enforced"),
        (STATUS_DRAFT, "Draft"),
        (STATUS_DISABLED, "Disabled"),
    ]

    SCOPE_ALL_USERS = "all_users"
    SCOPE_ADMINS = "admins"
    SCOPE_TENANT = "tenant"
    SCOPE_ROLE = "role"
    SCOPE_CHOICES = [
        (SCOPE_ALL_USERS, "All users"),
        (SCOPE_ADMINS, "Admins"),
        (SCOPE_TENANT, "Tenant"),
        (SCOPE_ROLE, "Role"),
    ]

    SEVERITY_LOW = "low"
    SEVERITY_MEDIUM = "medium"
    SEVERITY_HIGH = "high"
    SEVERITY_CRITICAL = "critical"
    SEVERITY_CHOICES = [
        (SEVERITY_LOW, "Low"),
        (SEVERITY_MEDIUM, "Medium"),
        (SEVERITY_HIGH, "High"),
        (SEVERITY_CRITICAL, "Critical"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="administration_securitypolicys")
    name = models.CharField(max_length=150)
    policy_type = models.CharField(max_length=20, choices=POLICY_TYPE_CHOICES, default=TYPE_PASSWORD)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default=SCOPE_ALL_USERS)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default=SEVERITY_MEDIUM)
    last_reviewed = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="secpol_tenant_status_idx"),
            models.Index(fields=["tenant", "policy_type"], name="secpol_tenant_type_idx"),
            models.Index(fields=["tenant", "severity"], name="secpol_tenant_sev_idx"),
        ]

    def __str__(self):
        return self.name


class DataPrivacyRule(models.Model):
    """A data-privacy rule (retention/anonymisation) tied to a regulation."""

    REGULATION_GDPR = "gdpr"
    REGULATION_CCPA = "ccpa"
    REGULATION_HIPAA = "hipaa"
    REGULATION_SOX = "sox"
    REGULATION_PCI_DSS = "pci_dss"
    REGULATION_INTERNAL = "internal"
    REGULATION_CHOICES = [
        (REGULATION_GDPR, "GDPR"),
        (REGULATION_CCPA, "CCPA"),
        (REGULATION_HIPAA, "HIPAA"),
        (REGULATION_SOX, "SOX"),
        (REGULATION_PCI_DSS, "PCI DSS"),
        (REGULATION_INTERNAL, "Internal"),
    ]

    CATEGORY_PII = "pii"
    CATEGORY_FINANCIAL = "financial"
    CATEGORY_HEALTH = "health"
    CATEGORY_CONTACT = "contact"
    CATEGORY_BEHAVIORAL = "behavioral"
    DATA_CATEGORY_CHOICES = [
        (CATEGORY_PII, "PII"),
        (CATEGORY_FINANCIAL, "Financial"),
        (CATEGORY_HEALTH, "Health"),
        (CATEGORY_CONTACT, "Contact"),
        (CATEGORY_BEHAVIORAL, "Behavioral"),
    ]

    ACTION_RETAIN = "retain"
    ACTION_ANONYMIZE = "anonymize"
    ACTION_DELETE = "delete"
    ACTION_ENCRYPT = "encrypt"
    ACTION_RESTRICT = "restrict"
    ACTION_CHOICES = [
        (ACTION_RETAIN, "Retain"),
        (ACTION_ANONYMIZE, "Anonymize"),
        (ACTION_DELETE, "Delete"),
        (ACTION_ENCRYPT, "Encrypt"),
        (ACTION_RESTRICT, "Restrict"),
    ]

    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_DRAFT = "draft"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_INACTIVE, "Inactive"),
        (STATUS_DRAFT, "Draft"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="administration_dataprivacyrules")
    name = models.CharField(max_length=150)
    regulation = models.CharField(max_length=20, choices=REGULATION_CHOICES, default=REGULATION_GDPR)
    data_category = models.CharField(max_length=20, choices=DATA_CATEGORY_CHOICES, default=CATEGORY_PII)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, default=ACTION_RETAIN)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    retention_days = models.IntegerField(default=365)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="dpr_tenant_status_idx"),
            models.Index(fields=["tenant", "regulation"], name="dpr_tenant_reg_idx"),
            models.Index(fields=["tenant", "data_category"], name="dpr_tenant_cat_idx"),
        ]

    def __str__(self):
        return self.name


class ComplianceItem(models.Model):
    """A compliance control tracked against a framework (audit readiness)."""

    FRAMEWORK_GDPR = "gdpr"
    FRAMEWORK_SOC2 = "soc2"
    FRAMEWORK_ISO27001 = "iso27001"
    FRAMEWORK_HIPAA = "hipaa"
    FRAMEWORK_PCI_DSS = "pci_dss"
    FRAMEWORK_CHOICES = [
        (FRAMEWORK_GDPR, "GDPR"),
        (FRAMEWORK_SOC2, "SOC 2"),
        (FRAMEWORK_ISO27001, "ISO 27001"),
        (FRAMEWORK_HIPAA, "HIPAA"),
        (FRAMEWORK_PCI_DSS, "PCI DSS"),
    ]

    STATUS_COMPLIANT = "compliant"
    STATUS_NON_COMPLIANT = "non_compliant"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_NOT_APPLICABLE = "not_applicable"
    STATUS_CHOICES = [
        (STATUS_COMPLIANT, "Compliant"),
        (STATUS_NON_COMPLIANT, "Non-compliant"),
        (STATUS_IN_PROGRESS, "In progress"),
        (STATUS_NOT_APPLICABLE, "Not applicable"),
    ]

    SEVERITY_LOW = "low"
    SEVERITY_MEDIUM = "medium"
    SEVERITY_HIGH = "high"
    SEVERITY_CRITICAL = "critical"
    SEVERITY_CHOICES = [
        (SEVERITY_LOW, "Low"),
        (SEVERITY_MEDIUM, "Medium"),
        (SEVERITY_HIGH, "High"),
        (SEVERITY_CRITICAL, "Critical"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="administration_complianceitems")
    title = models.CharField(max_length=150)
    framework = models.CharField(max_length=20, choices=FRAMEWORK_CHOICES, default=FRAMEWORK_SOC2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_IN_PROGRESS)
    owner = models.CharField(max_length=120, blank=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default=SEVERITY_MEDIUM)
    due_date = models.DateField(null=True, blank=True)
    last_audited = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="cmpl_tenant_status_idx"),
            models.Index(fields=["tenant", "framework"], name="cmpl_tenant_fw_idx"),
            models.Index(fields=["tenant", "severity"], name="cmpl_tenant_sev_idx"),
        ]

    def __str__(self):
        return self.title


class BackupJob(models.Model):
    """Backup & Disaster Recovery — a backup run (auto BKP-00001)."""

    TYPE_FULL = "full"
    TYPE_INCREMENTAL = "incremental"
    TYPE_DIFFERENTIAL = "differential"
    TYPE_SNAPSHOT = "snapshot"
    BACKUP_TYPE_CHOICES = [
        (TYPE_FULL, "Full"),
        (TYPE_INCREMENTAL, "Incremental"),
        (TYPE_DIFFERENTIAL, "Differential"),
        (TYPE_SNAPSHOT, "Snapshot"),
    ]

    STATUS_SCHEDULED = "scheduled"
    STATUS_RUNNING = "running"
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"
    STATUS_CANCELED = "canceled"
    STATUS_CHOICES = [
        (STATUS_SCHEDULED, "Scheduled"),
        (STATUS_RUNNING, "Running"),
        (STATUS_SUCCESS, "Success"),
        (STATUS_FAILED, "Failed"),
        (STATUS_CANCELED, "Canceled"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="administration_backupjobs")
    number = models.CharField(max_length=20, blank=True)
    name = models.CharField(max_length=150)
    backup_type = models.CharField(max_length=20, choices=BACKUP_TYPE_CHOICES, default=TYPE_FULL)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SCHEDULED)
    storage_location = models.CharField(max_length=200, blank=True)
    size_mb = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    retention_days = models.IntegerField(default=30)
    scheduled_on = models.DateField(default=timezone.localdate)
    started_at = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    completed_at = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-scheduled_on", "-id"]
        unique_together = ("tenant", "number")
        indexes = [
            models.Index(fields=["tenant", "status"], name="bkp_tenant_status_idx"),
            models.Index(fields=["tenant", "backup_type"], name="bkp_tenant_type_idx"),
            models.Index(fields=["tenant", "scheduled_on"], name="bkp_tenant_scheddate_idx"),
        ]

    def __str__(self):
        return self.number or f"Backup #{self.pk}"

    def save(self, *args, **kwargs):
        if not self.number and self.tenant_id:
            # Per-tenant sequence with a row lock to avoid duplicate numbers under
            # concurrent creation (idempotent for seeds).
            with transaction.atomic():
                last = (BackupJob.objects.select_for_update()
                        .filter(tenant_id=self.tenant_id, number__startswith="BKP-")
                        .order_by("-number").first())
                seq = 1
                if last and last.number:
                    try:
                        seq = int(last.number.split("-")[1]) + 1
                    except (IndexError, ValueError):
                        seq = (BackupJob.objects
                               .filter(tenant_id=self.tenant_id, number__startswith="BKP-")
                               .count() + 1)
                self.number = f"BKP-{seq:05d}"
                self._sync_run_timestamps()
                super().save(*args, **kwargs)
                return
        self._sync_run_timestamps()
        super().save(*args, **kwargs)

    def _sync_run_timestamps(self):
        if self.status == self.STATUS_RUNNING and self.started_at is None:
            self.started_at = timezone.now()
        if self.status in (self.STATUS_SUCCESS, self.STATUS_FAILED, self.STATUS_CANCELED):
            if self.started_at is None:
                self.started_at = timezone.now()
            if self.completed_at is None:
                self.completed_at = timezone.now()


class SystemHealthMetric(models.Model):
    """System Health & Performance — an observed health/performance metric."""

    CATEGORY_CPU = "cpu"
    CATEGORY_MEMORY = "memory"
    CATEGORY_DISK = "disk"
    CATEGORY_DATABASE = "database"
    CATEGORY_API = "api"
    CATEGORY_UPTIME = "uptime"
    CATEGORY_RESPONSE_TIME = "response_time"
    CATEGORY_CHOICES = [
        (CATEGORY_CPU, "CPU"),
        (CATEGORY_MEMORY, "Memory"),
        (CATEGORY_DISK, "Disk"),
        (CATEGORY_DATABASE, "Database"),
        (CATEGORY_API, "API"),
        (CATEGORY_UPTIME, "Uptime"),
        (CATEGORY_RESPONSE_TIME, "Response time"),
    ]

    STATUS_HEALTHY = "healthy"
    STATUS_WARNING = "warning"
    STATUS_CRITICAL = "critical"
    STATUS_UNKNOWN = "unknown"
    STATUS_CHOICES = [
        (STATUS_HEALTHY, "Healthy"),
        (STATUS_WARNING, "Warning"),
        (STATUS_CRITICAL, "Critical"),
        (STATUS_UNKNOWN, "Unknown"),
    ]

    UNIT_PERCENT = "percent"
    UNIT_MS = "ms"
    UNIT_GB = "gb"
    UNIT_COUNT = "count"
    UNIT_CHOICES = [
        (UNIT_PERCENT, "Percent"),
        (UNIT_MS, "Milliseconds"),
        (UNIT_GB, "Gigabytes"),
        (UNIT_COUNT, "Count"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="administration_systemhealthmetrics")
    metric_name = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_CPU)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_HEALTHY)
    value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default=UNIT_PERCENT)
    threshold = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    recorded_on = models.DateField(default=timezone.localdate)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-recorded_on", "metric_name"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="shm_tenant_status_idx"),
            models.Index(fields=["tenant", "category"], name="shm_tenant_cat_idx"),
            models.Index(fields=["tenant", "recorded_on"], name="shm_tenant_recdate_idx"),
        ]

    def __str__(self):
        return self.metric_name
