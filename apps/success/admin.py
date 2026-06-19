from django.contrib import admin

from .models import (
    Advocacy, HealthScore, OnboardingPlan, QBR, Renewal,
)


@admin.register(HealthScore)
class HealthScoreAdmin(admin.ModelAdmin):
    list_display = ("account_name", "tenant", "owner", "score", "risk_level", "trend", "last_reviewed")
    list_filter = ("tenant", "risk_level", "trend")
    search_fields = ("account_name", "owner", "notes")


@admin.register(Renewal)
class RenewalAdmin(admin.ModelAdmin):
    list_display = ("number", "tenant", "account_name", "renewal_type", "status",
                    "arr_proposed", "probability", "renewal_date")
    list_filter = ("tenant", "renewal_type", "status")
    search_fields = ("number", "account_name", "owner")
    readonly_fields = ("number",)


@admin.register(OnboardingPlan)
class OnboardingPlanAdmin(admin.ModelAdmin):
    list_display = ("plan_name", "tenant", "account_name", "owner", "status", "progress_pct", "start_date")
    list_filter = ("tenant", "status")
    search_fields = ("plan_name", "account_name", "owner")


@admin.register(Advocacy)
class AdvocacyAdmin(admin.ModelAdmin):
    list_display = ("contact_name", "tenant", "account_name", "advocacy_type", "status", "nps_score")
    list_filter = ("tenant", "advocacy_type", "status")
    search_fields = ("account_name", "contact_name", "notes")


@admin.register(QBR)
class QBRAdmin(admin.ModelAdmin):
    list_display = ("account_name", "tenant", "period_label", "owner", "status", "sentiment", "scheduled_on")
    list_filter = ("tenant", "status", "sentiment")
    search_fields = ("account_name", "period_label", "owner")
