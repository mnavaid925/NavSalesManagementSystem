from django.contrib import admin

from .models import (
    BackupJob, ComplianceItem, DataPrivacyRule, SecurityPolicy, SystemHealthMetric,
)


@admin.register(SecurityPolicy)
class SecurityPolicyAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "policy_type", "status", "scope", "severity", "last_reviewed")
    list_filter = ("tenant", "policy_type", "status", "severity")
    search_fields = ("name", "description")


@admin.register(DataPrivacyRule)
class DataPrivacyRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "regulation", "data_category", "action", "status", "retention_days")
    list_filter = ("tenant", "regulation", "data_category", "action", "status")
    search_fields = ("name", "notes")


@admin.register(ComplianceItem)
class ComplianceItemAdmin(admin.ModelAdmin):
    list_display = ("title", "tenant", "framework", "status", "owner", "severity", "due_date")
    list_filter = ("tenant", "framework", "status", "severity")
    search_fields = ("title", "owner", "notes")


@admin.register(BackupJob)
class BackupJobAdmin(admin.ModelAdmin):
    list_display = ("number", "tenant", "name", "backup_type", "status", "size_mb", "scheduled_on")
    list_filter = ("tenant", "backup_type", "status")
    search_fields = ("number", "name", "storage_location")
    readonly_fields = ("number", "started_at", "completed_at")


@admin.register(SystemHealthMetric)
class SystemHealthMetricAdmin(admin.ModelAdmin):
    list_display = ("metric_name", "tenant", "category", "status", "value", "unit", "recorded_on")
    list_filter = ("tenant", "category", "status")
    search_fields = ("metric_name", "notes")
