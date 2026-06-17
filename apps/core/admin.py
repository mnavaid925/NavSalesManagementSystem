from django.contrib import admin

from .models import AuditLog, Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "status", "is_active", "created_at")
    list_filter = ("status", "is_active")
    search_fields = ("name", "slug", "subdomain")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "tenant", "user", "action", "model_name", "object_repr")
    list_filter = ("action",)
    search_fields = ("model_name", "object_repr", "detail")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
