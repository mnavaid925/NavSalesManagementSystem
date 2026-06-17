from django.contrib import admin

from .models import Activity, EmailLog, Meeting, SalesPlan, SalesTask


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("subject", "tenant", "activity_type", "direction", "outcome", "activity_date")
    list_filter = ("tenant", "activity_type", "direction", "outcome")
    search_fields = ("subject", "contact_name", "company_name", "notes")


@admin.register(SalesTask)
class SalesTaskAdmin(admin.ModelAdmin):
    list_display = ("title", "tenant", "priority", "status", "assigned_to", "due_date", "completed_at")
    list_filter = ("tenant", "priority", "status")
    search_fields = ("title", "description", "assigned_to", "related_to")
    readonly_fields = ("completed_at",)


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ("title", "tenant", "meeting_type", "location_type", "status", "scheduled_date")
    list_filter = ("tenant", "meeting_type", "location_type", "status")
    search_fields = ("title", "attendees", "location", "organizer_name")


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ("subject", "tenant", "direction", "status", "to_email", "sent_at", "opened_at")
    list_filter = ("tenant", "direction", "status")
    search_fields = ("subject", "from_email", "to_email", "body")
    readonly_fields = ("sent_at", "opened_at")


@admin.register(SalesPlan)
class SalesPlanAdmin(admin.ModelAdmin):
    list_display = ("number", "tenant", "title", "period_type", "status", "start_date", "revenue_goal")
    list_filter = ("tenant", "period_type", "status")
    search_fields = ("number", "title", "owner_name", "objectives")
    readonly_fields = ("number",)
