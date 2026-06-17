from django.contrib import admin

from .models import (
    Clawback, CommissionPlan, Earning, GlobalPlanVariation, Payout,
)


@admin.register(CommissionPlan)
class CommissionPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "code", "plan_type", "status", "base_rate", "effective_from")
    list_filter = ("tenant", "plan_type", "status")
    search_fields = ("name", "code", "description")


@admin.register(Earning)
class EarningAdmin(admin.ModelAdmin):
    list_display = ("number", "tenant", "rep_name", "plan", "commission_amount", "status", "earned_on")
    list_filter = ("tenant", "status", "plan")
    search_fields = ("number", "rep_name", "deal_reference")
    readonly_fields = ("number", "approved_at")


@admin.register(Clawback)
class ClawbackAdmin(admin.ModelAdmin):
    list_display = ("rep_name", "tenant", "earning", "reason", "status", "amount", "effective_on")
    list_filter = ("tenant", "reason", "status")
    search_fields = ("rep_name", "notes")
    readonly_fields = ("applied_at",)


@admin.register(GlobalPlanVariation)
class GlobalPlanVariationAdmin(admin.ModelAdmin):
    list_display = ("region", "tenant", "plan", "currency", "status", "fx_rate", "effective_from")
    list_filter = ("tenant", "currency", "status")
    search_fields = ("region", "notes")


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ("number", "tenant", "rep_name", "method", "status", "net_amount", "scheduled_on")
    list_filter = ("tenant", "method", "status")
    search_fields = ("number", "rep_name", "reference", "period_label")
    readonly_fields = ("number", "paid_at")
