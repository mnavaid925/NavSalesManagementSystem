from django.contrib import admin

from .models import (
    AlertRule, ApprovalWorkflow, AssignmentRule, EnrichmentRule, ProcessFlow,
)


@admin.register(ProcessFlow)
class ProcessFlowAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "trigger_event", "object_type", "status", "steps_count", "last_run")
    list_filter = ("tenant", "trigger_event", "object_type", "status")
    search_fields = ("name", "description")
    readonly_fields = ("last_run",)


@admin.register(AssignmentRule)
class AssignmentRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "entity", "assign_strategy", "status", "priority")
    list_filter = ("tenant", "entity", "assign_strategy", "status")
    search_fields = ("name", "criteria", "assignee_pool", "notes")


@admin.register(ApprovalWorkflow)
class ApprovalWorkflowAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "approval_type", "status", "threshold_amount", "steps_count", "escalation_hours")
    list_filter = ("tenant", "approval_type", "status")
    search_fields = ("name", "approvers", "notes")


@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "channel", "severity", "status", "frequency")
    list_filter = ("tenant", "channel", "severity", "status")
    search_fields = ("name", "trigger_condition", "recipients", "notes")


@admin.register(EnrichmentRule)
class EnrichmentRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "data_source", "operation", "status", "records_processed", "success_rate", "last_run")
    list_filter = ("tenant", "data_source", "operation", "status")
    search_fields = ("name", "target_field", "notes")
    readonly_fields = ("last_run",)
