from django.contrib import admin

from .models import (
    CallActivity, FieldVisit, MobileAlert, MobileDevice, MobileQuote,
)


@admin.register(MobileDevice)
class MobileDeviceAdmin(admin.ModelAdmin):
    list_display = ("device_name", "tenant", "user_name", "platform", "status", "push_enabled", "last_sync")
    list_filter = ("tenant", "platform", "status")
    search_fields = ("device_name", "user_name", "app_version")
    readonly_fields = ("last_sync",)


@admin.register(FieldVisit)
class FieldVisitAdmin(admin.ModelAdmin):
    list_display = ("number", "tenant", "rep_name", "account_name", "visit_type", "status", "scheduled_on")
    list_filter = ("tenant", "visit_type", "status")
    search_fields = ("number", "rep_name", "account_name", "location")
    readonly_fields = ("number",)


@admin.register(MobileQuote)
class MobileQuoteAdmin(admin.ModelAdmin):
    list_display = ("number", "tenant", "rep_name", "customer_name", "amount", "status", "submitted_on")
    list_filter = ("tenant", "status")
    search_fields = ("number", "rep_name", "customer_name")
    readonly_fields = ("number",)


@admin.register(CallActivity)
class CallActivityAdmin(admin.ModelAdmin):
    list_display = ("contact_name", "tenant", "rep_name", "direction", "call_type", "outcome", "call_date")
    list_filter = ("tenant", "direction", "call_type", "outcome")
    search_fields = ("rep_name", "contact_name")


@admin.register(MobileAlert)
class MobileAlertAdmin(admin.ModelAdmin):
    list_display = ("title", "tenant", "alert_type", "priority", "status", "recipient", "created_at")
    list_filter = ("tenant", "alert_type", "priority", "status")
    search_fields = ("title", "recipient", "body")
