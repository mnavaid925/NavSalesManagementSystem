from django.contrib import admin

from .models import (
    Benchmark, ConversionFunnel, RepScorecard, SalesVelocity, WinLossAnalysis,
)


@admin.register(WinLossAnalysis)
class WinLossAnalysisAdmin(admin.ModelAdmin):
    list_display = ("deal_name", "tenant", "rep_name", "outcome", "amount",
                    "reason_category", "closed_on")
    list_filter = ("tenant", "outcome", "reason_category")
    search_fields = ("deal_name", "rep_name", "competitor")


@admin.register(SalesVelocity)
class SalesVelocityAdmin(admin.ModelAdmin):
    list_display = ("period_label", "tenant", "segment", "avg_deal_size", "win_rate",
                    "sales_cycle_days", "velocity_score", "recorded_on")
    list_filter = ("tenant", "segment")
    search_fields = ("period_label",)


@admin.register(ConversionFunnel)
class ConversionFunnelAdmin(admin.ModelAdmin):
    list_display = ("stage_name", "tenant", "segment", "period_label", "entered_count",
                    "converted_count", "conversion_rate", "recorded_on")
    list_filter = ("tenant", "segment")
    search_fields = ("stage_name", "period_label")


@admin.register(RepScorecard)
class RepScorecardAdmin(admin.ModelAdmin):
    list_display = ("rep_name", "tenant", "period_label", "quota", "attainment",
                    "deals_won", "deals_lost", "grade", "ranking")
    list_filter = ("tenant", "grade")
    search_fields = ("rep_name", "period_label")


@admin.register(Benchmark)
class BenchmarkAdmin(admin.ModelAdmin):
    list_display = ("metric_name", "tenant", "category", "our_value", "peer_median",
                    "top_quartile", "status", "recorded_on")
    list_filter = ("tenant", "category", "status")
    search_fields = ("metric_name", "period_label")
