from django.contrib import admin

from .models import (
    Competitor, DealCollaborator, Opportunity, OpportunityActivity, PipelineStage,
)


@admin.register(PipelineStage)
class PipelineStageAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "order", "probability", "stage_type", "is_active")
    list_filter = ("tenant", "stage_type", "is_active")
    search_fields = ("name", "description")


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ("number", "name", "tenant", "account_name", "stage",
                    "status", "priority", "amount", "expected_close_date")
    list_filter = ("tenant", "status", "priority", "forecast_category", "stage")
    search_fields = ("number", "name", "account_name", "owner_name")
    readonly_fields = ("number", "closed_at")


@admin.register(OpportunityActivity)
class OpportunityActivityAdmin(admin.ModelAdmin):
    list_display = ("subject", "tenant", "opportunity", "activity_type",
                    "outcome", "performed_by", "activity_date")
    list_filter = ("tenant", "activity_type", "outcome")
    search_fields = ("subject", "performed_by", "notes")


@admin.register(Competitor)
class CompetitorAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "opportunity", "threat_level", "status")
    list_filter = ("tenant", "threat_level", "status")
    search_fields = ("name", "strengths", "weaknesses")


@admin.register(DealCollaborator)
class DealCollaboratorAdmin(admin.ModelAdmin):
    list_display = ("member_name", "tenant", "opportunity", "team_role", "status", "email")
    list_filter = ("tenant", "team_role", "status")
    search_fields = ("member_name", "email", "contribution")
