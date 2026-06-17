from django.contrib import admin

from .models import (
    Lead, LeadConversion, LeadScore, LeadSource, NurtureCampaign,
)


@admin.register(LeadSource)
class LeadSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "source_type", "routing_rule", "status", "cost_per_lead")
    list_filter = ("tenant", "source_type", "routing_rule", "status")
    search_fields = ("name", "default_owner", "description")


@admin.register(NurtureCampaign)
class NurtureCampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "channel", "status", "step_count", "enrolled_count", "start_on")
    list_filter = ("tenant", "channel", "status")
    search_fields = ("name", "goal")


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("number", "tenant", "first_name", "last_name", "company",
                    "status", "rating", "owner", "captured_on")
    list_filter = ("tenant", "status", "rating", "source")
    search_fields = ("number", "first_name", "last_name", "company", "email", "owner")
    readonly_fields = ("number",)


@admin.register(LeadScore)
class LeadScoreAdmin(admin.ModelAdmin):
    list_display = ("lead", "tenant", "score", "grade", "scoring_model", "scored_on")
    list_filter = ("tenant", "grade", "scoring_model")
    search_fields = ("lead__first_name", "lead__last_name", "lead__number", "reason")


@admin.register(LeadConversion)
class LeadConversionAdmin(admin.ModelAdmin):
    list_display = ("number", "tenant", "lead", "status", "outcome", "deal_value", "converted_at")
    list_filter = ("tenant", "status", "outcome")
    search_fields = ("number", "lead__first_name", "lead__last_name", "assigned_to")
    readonly_fields = ("number", "converted_at")
