from django.contrib import admin

from .models import ApiKey, Connector, SyncJob, SyncLog, Webhook


@admin.register(Connector)
class ConnectorAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "category", "provider", "status", "auth_type", "last_sync")
    list_filter = ("tenant", "category", "status")
    search_fields = ("name", "provider")
    readonly_fields = ("last_sync",)


@admin.register(SyncJob)
class SyncJobAdmin(admin.ModelAdmin):
    list_display = ("number", "tenant", "name", "connector", "direction", "status", "schedule", "last_run")
    list_filter = ("tenant", "status", "direction", "schedule")
    search_fields = ("number", "name")
    readonly_fields = ("number", "last_run")


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ("__str__", "tenant", "job", "level", "records_affected", "duration_ms", "occurred_at")
    list_filter = ("tenant", "level")
    search_fields = ("message",)
    readonly_fields = ("occurred_at",)


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "event_type", "http_method", "status", "failure_count", "last_triggered")
    list_filter = ("tenant", "event_type", "status")
    search_fields = ("name", "target_url")
    readonly_fields = ("secret", "last_triggered")


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "key_prefix", "environment", "status", "expires_on", "last_used")
    list_filter = ("tenant", "environment", "status")
    search_fields = ("name", "key_prefix", "scopes")
    readonly_fields = ("key", "key_prefix", "last_used")
