from django.contrib import admin

from .models import (
    Forecast, ForecastAccuracy, ForecastAdjustment, ForecastCategory, Quota,
)


@admin.register(ForecastCategory)
class ForecastCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "commitment", "probability", "weight", "is_active")
    list_filter = ("tenant", "commitment", "is_active")
    search_fields = ("name", "description")


@admin.register(Forecast)
class ForecastAdmin(admin.ModelAdmin):
    list_display = ("number", "tenant", "name", "owner_name", "period_type",
                    "period_label", "commit_amount", "ai_predicted_amount", "status")
    list_filter = ("tenant", "status", "period_type", "ai_confidence")
    search_fields = ("number", "name", "owner_name")
    readonly_fields = ("number", "submitted_at")


@admin.register(Quota)
class QuotaAdmin(admin.ModelAdmin):
    list_display = ("owner_name", "tenant", "period_type", "period_label",
                    "target_amount", "attained_amount", "status")
    list_filter = ("tenant", "status", "period_type")
    search_fields = ("owner_name", "period_label")


@admin.register(ForecastAdjustment)
class ForecastAdjustmentAdmin(admin.ModelAdmin):
    list_display = ("forecast", "tenant", "adjustment_type", "amount", "adjusted_by", "status")
    list_filter = ("tenant", "adjustment_type", "status")
    search_fields = ("adjusted_by", "reason")
    readonly_fields = ("approved_at",)


@admin.register(ForecastAccuracy)
class ForecastAccuracyAdmin(admin.ModelAdmin):
    list_display = ("period_label", "tenant", "forecast", "forecasted_amount",
                    "actual_amount", "variance_amount", "accuracy_pct", "grade")
    list_filter = ("tenant", "grade")
    search_fields = ("period_label", "notes")
    readonly_fields = ("variance_amount",)
