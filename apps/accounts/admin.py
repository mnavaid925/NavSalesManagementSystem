from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Role, User, UserInvite


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "tenant", "role", "is_tenant_admin", "is_active")
    list_filter = ("tenant", "is_tenant_admin", "is_active", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Sales Management System", {
            "fields": ("tenant", "role", "phone", "job_title", "avatar_url", "is_tenant_admin"),
        }),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "level", "is_active")
    list_filter = ("tenant", "level", "is_active")
    search_fields = ("name", "description")


@admin.register(UserInvite)
class UserInviteAdmin(admin.ModelAdmin):
    list_display = ("email", "tenant", "role", "status", "invited_by", "expires_at", "created_at")
    list_filter = ("tenant", "status")
    search_fields = ("email",)
    readonly_fields = ("token", "created_at", "updated_at", "accepted_at")
