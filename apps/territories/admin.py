from django.contrib import admin

from .models import (
    CoverageModel, QuotaPlan, Territory, TerritoryAssignment, TerritoryPerformance,
)


@admin.register(Territory)
class TerritoryAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "code", "territory_type", "status",
                    "region", "account_count", "annual_potential")
    list_filter = ("tenant", "territory_type", "status")
    search_fields = ("name", "code", "region", "country", "description")


@admin.register(TerritoryAssignment)
class TerritoryAssignmentAdmin(admin.ModelAdmin):
    list_display = ("rep_name", "tenant", "territory", "assignment_role", "status",
                    "workload_percent", "effective_date")
    list_filter = ("tenant", "assignment_role", "status")
    search_fields = ("rep_name", "rep_email", "territory__name", "notes")


@admin.register(QuotaPlan)
class QuotaPlanAdmin(admin.ModelAdmin):
    list_display = ("number", "tenant", "name", "territory", "period_type",
                    "fiscal_year", "status", "target_amount")
    list_filter = ("tenant", "period_type", "status")
    search_fields = ("number", "name", "territory__name", "notes")
    readonly_fields = ("number", "approved_at")


@admin.register(CoverageModel)
class CoverageModelAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "model_type", "status", "target_ratio",
                    "rep_capacity", "coverage_score")
    list_filter = ("tenant", "model_type", "status")
    search_fields = ("name", "description")


@admin.register(TerritoryPerformance)
class TerritoryPerformanceAdmin(admin.ModelAdmin):
    list_display = ("territory", "tenant", "period_type", "period_label", "rating",
                    "quota_amount", "actual_amount", "attainment_percent")
    list_filter = ("tenant", "period_type", "rating")
    search_fields = ("period_label", "territory__name")
    readonly_fields = ("attainment_percent",)
