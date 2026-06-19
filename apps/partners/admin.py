from django.contrib import admin

from .models import (
    ChannelConflict, DealRegistration, Partner, PartnerCollateral, PartnerPerformance,
)


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "partner_type", "tier", "status", "region", "onboarded_on")
    list_filter = ("tenant", "partner_type", "tier", "status")
    search_fields = ("name", "region", "contact_name", "contact_email")


@admin.register(DealRegistration)
class DealRegistrationAdmin(admin.ModelAdmin):
    list_display = ("number", "tenant", "partner", "deal_name", "customer_name", "amount", "status", "registered_on")
    list_filter = ("tenant", "status", "partner")
    search_fields = ("number", "deal_name", "customer_name")
    readonly_fields = ("number",)


@admin.register(PartnerCollateral)
class PartnerCollateralAdmin(admin.ModelAdmin):
    list_display = ("title", "tenant", "partner", "asset_type", "access_level", "version", "published_on")
    list_filter = ("tenant", "asset_type", "access_level", "partner")
    search_fields = ("title", "notes")


@admin.register(PartnerPerformance)
class PartnerPerformanceAdmin(admin.ModelAdmin):
    list_display = ("period_label", "tenant", "partner", "revenue", "deals_closed", "attainment", "recorded_on")
    list_filter = ("tenant", "partner")
    search_fields = ("period_label",)


@admin.register(ChannelConflict)
class ChannelConflictAdmin(admin.ModelAdmin):
    list_display = ("number", "tenant", "partner", "conflict_type", "severity", "status", "reported_on")
    list_filter = ("tenant", "conflict_type", "severity", "status")
    search_fields = ("number", "account_name")
    readonly_fields = ("number",)
