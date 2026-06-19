from django.db import models


class ProcessFlow(models.Model):
    """Visual Process Designer — an automated process triggered by a record event."""

    TRIGGER_RECORD_CREATED = "record_created"
    TRIGGER_RECORD_UPDATED = "record_updated"
    TRIGGER_STAGE_CHANGED = "stage_changed"
    TRIGGER_FIELD_CHANGED = "field_changed"
    TRIGGER_SCHEDULED = "scheduled"
    TRIGGER_MANUAL = "manual"
    TRIGGER_EVENT_CHOICES = [
        (TRIGGER_RECORD_CREATED, "Record created"),
        (TRIGGER_RECORD_UPDATED, "Record updated"),
        (TRIGGER_STAGE_CHANGED, "Stage changed"),
        (TRIGGER_FIELD_CHANGED, "Field changed"),
        (TRIGGER_SCHEDULED, "Scheduled"),
        (TRIGGER_MANUAL, "Manual"),
    ]

    OBJECT_LEAD = "lead"
    OBJECT_OPPORTUNITY = "opportunity"
    OBJECT_ACCOUNT = "account"
    OBJECT_QUOTE = "quote"
    OBJECT_ORDER = "order"
    OBJECT_TYPE_CHOICES = [
        (OBJECT_LEAD, "Lead"),
        (OBJECT_OPPORTUNITY, "Opportunity"),
        (OBJECT_ACCOUNT, "Account"),
        (OBJECT_QUOTE, "Quote"),
        (OBJECT_ORDER, "Order"),
    ]

    STATUS_DRAFT = "draft"
    STATUS_ACTIVE = "active"
    STATUS_PAUSED = "paused"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_PAUSED, "Paused"),
        (STATUS_ARCHIVED, "Archived"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="automation_processflows")
    name = models.CharField(max_length=150)
    trigger_event = models.CharField(
        max_length=20, choices=TRIGGER_EVENT_CHOICES, default=TRIGGER_RECORD_CREATED)
    object_type = models.CharField(
        max_length=20, choices=OBJECT_TYPE_CHOICES, default=OBJECT_LEAD)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    steps_count = models.IntegerField(default=0)
    last_run = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="pf_tenant_status_idx"),
            models.Index(fields=["tenant", "trigger_event"], name="pf_tenant_trigger_idx"),
            models.Index(fields=["tenant", "object_type"], name="pf_tenant_object_idx"),
        ]

    def __str__(self):
        return self.name


class AssignmentRule(models.Model):
    """Auto-Assignment Rules — routes incoming records to owners automatically."""

    ENTITY_LEAD = "lead"
    ENTITY_OPPORTUNITY = "opportunity"
    ENTITY_CASE = "case"
    ENTITY_ACCOUNT = "account"
    ENTITY_CHOICES = [
        (ENTITY_LEAD, "Lead"),
        (ENTITY_OPPORTUNITY, "Opportunity"),
        (ENTITY_CASE, "Case"),
        (ENTITY_ACCOUNT, "Account"),
    ]

    STRATEGY_ROUND_ROBIN = "round_robin"
    STRATEGY_LOAD_BALANCED = "load_balanced"
    STRATEGY_TERRITORY = "territory"
    STRATEGY_SKILL_BASED = "skill_based"
    STRATEGY_MANUAL = "manual"
    ASSIGN_STRATEGY_CHOICES = [
        (STRATEGY_ROUND_ROBIN, "Round robin"),
        (STRATEGY_LOAD_BALANCED, "Load balanced"),
        (STRATEGY_TERRITORY, "Territory"),
        (STRATEGY_SKILL_BASED, "Skill based"),
        (STRATEGY_MANUAL, "Manual"),
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
        "core.Tenant", on_delete=models.CASCADE, related_name="automation_assignmentrules")
    name = models.CharField(max_length=150)
    entity = models.CharField(max_length=20, choices=ENTITY_CHOICES, default=ENTITY_LEAD)
    assign_strategy = models.CharField(
        max_length=20, choices=ASSIGN_STRATEGY_CHOICES, default=STRATEGY_ROUND_ROBIN)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    priority = models.IntegerField(default=0)
    criteria = models.TextField(blank=True)
    assignee_pool = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["priority", "name"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="ar_tenant_status_idx"),
            models.Index(fields=["tenant", "entity"], name="ar_tenant_entity_idx"),
            models.Index(fields=["tenant", "assign_strategy"], name="ar_tenant_strategy_idx"),
        ]

    def __str__(self):
        return self.name


class ApprovalWorkflow(models.Model):
    """Approval Workflows — a multi-step approval chain for a request type."""

    TYPE_DISCOUNT = "discount"
    TYPE_QUOTE = "quote"
    TYPE_CONTRACT = "contract"
    TYPE_EXPENSE = "expense"
    TYPE_DEAL = "deal"
    TYPE_REFUND = "refund"
    APPROVAL_TYPE_CHOICES = [
        (TYPE_DISCOUNT, "Discount"),
        (TYPE_QUOTE, "Quote"),
        (TYPE_CONTRACT, "Contract"),
        (TYPE_EXPENSE, "Expense"),
        (TYPE_DEAL, "Deal"),
        (TYPE_REFUND, "Refund"),
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
        "core.Tenant", on_delete=models.CASCADE, related_name="automation_approvalworkflows")
    name = models.CharField(max_length=150)
    approval_type = models.CharField(
        max_length=20, choices=APPROVAL_TYPE_CHOICES, default=TYPE_DISCOUNT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    threshold_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    steps_count = models.IntegerField(default=1)
    escalation_hours = models.IntegerField(default=24)
    approvers = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="aw_tenant_status_idx"),
            models.Index(fields=["tenant", "approval_type"], name="aw_tenant_type_idx"),
        ]

    def __str__(self):
        return self.name


class AlertRule(models.Model):
    """Notification & Alert Engine — fires notifications on a trigger condition."""

    CHANNEL_EMAIL = "email"
    CHANNEL_SMS = "sms"
    CHANNEL_PUSH = "push"
    CHANNEL_IN_APP = "in_app"
    CHANNEL_SLACK = "slack"
    CHANNEL_WEBHOOK = "webhook"
    CHANNEL_CHOICES = [
        (CHANNEL_EMAIL, "Email"),
        (CHANNEL_SMS, "SMS"),
        (CHANNEL_PUSH, "Push"),
        (CHANNEL_IN_APP, "In-app"),
        (CHANNEL_SLACK, "Slack"),
        (CHANNEL_WEBHOOK, "Webhook"),
    ]

    SEVERITY_INFO = "info"
    SEVERITY_WARNING = "warning"
    SEVERITY_CRITICAL = "critical"
    SEVERITY_CHOICES = [
        (SEVERITY_INFO, "Info"),
        (SEVERITY_WARNING, "Warning"),
        (SEVERITY_CRITICAL, "Critical"),
    ]

    STATUS_ACTIVE = "active"
    STATUS_PAUSED = "paused"
    STATUS_DISABLED = "disabled"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_PAUSED, "Paused"),
        (STATUS_DISABLED, "Disabled"),
    ]

    FREQUENCY_IMMEDIATE = "immediate"
    FREQUENCY_HOURLY = "hourly"
    FREQUENCY_DAILY = "daily"
    FREQUENCY_WEEKLY = "weekly"
    FREQUENCY_CHOICES = [
        (FREQUENCY_IMMEDIATE, "Immediate"),
        (FREQUENCY_HOURLY, "Hourly"),
        (FREQUENCY_DAILY, "Daily"),
        (FREQUENCY_WEEKLY, "Weekly"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="automation_alertrules")
    name = models.CharField(max_length=150)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default=CHANNEL_EMAIL)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default=SEVERITY_INFO)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    trigger_condition = models.TextField(blank=True)
    recipients = models.TextField(blank=True)
    frequency = models.CharField(
        max_length=20, choices=FREQUENCY_CHOICES, default=FREQUENCY_IMMEDIATE)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="alr_tenant_status_idx"),
            models.Index(fields=["tenant", "channel"], name="alr_tenant_channel_idx"),
            models.Index(fields=["tenant", "severity"], name="alr_tenant_severity_idx"),
        ]

    def __str__(self):
        return self.name


class EnrichmentRule(models.Model):
    """Data Enrichment & Cleansing — enriches/normalizes records from a source."""

    SOURCE_CLEARBIT = "clearbit"
    SOURCE_ZOOMINFO = "zoominfo"
    SOURCE_LINKEDIN = "linkedin"
    SOURCE_INTERNAL = "internal"
    SOURCE_MANUAL = "manual"
    DATA_SOURCE_CHOICES = [
        (SOURCE_CLEARBIT, "Clearbit"),
        (SOURCE_ZOOMINFO, "ZoomInfo"),
        (SOURCE_LINKEDIN, "LinkedIn"),
        (SOURCE_INTERNAL, "Internal"),
        (SOURCE_MANUAL, "Manual"),
    ]

    OP_ENRICH = "enrich"
    OP_DEDUPE = "dedupe"
    OP_NORMALIZE = "normalize"
    OP_VALIDATE = "validate"
    OP_APPEND = "append"
    OPERATION_CHOICES = [
        (OP_ENRICH, "Enrich"),
        (OP_DEDUPE, "Dedupe"),
        (OP_NORMALIZE, "Normalize"),
        (OP_VALIDATE, "Validate"),
        (OP_APPEND, "Append"),
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
        "core.Tenant", on_delete=models.CASCADE, related_name="automation_enrichmentrules")
    name = models.CharField(max_length=150)
    data_source = models.CharField(
        max_length=20, choices=DATA_SOURCE_CHOICES, default=SOURCE_INTERNAL)
    operation = models.CharField(max_length=20, choices=OPERATION_CHOICES, default=OP_ENRICH)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    target_field = models.CharField(max_length=120, blank=True)
    records_processed = models.IntegerField(default=0)
    success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    last_run = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="er_tenant_status_idx"),
            models.Index(fields=["tenant", "data_source"], name="er_tenant_source_idx"),
            models.Index(fields=["tenant", "operation"], name="er_tenant_operation_idx"),
        ]

    def __str__(self):
        return self.name
