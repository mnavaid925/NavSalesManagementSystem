from django.contrib import admin

from .models import (
    CampaignInfluence, CampaignPerformance, ContentEngagement, MarketingEvent, MQLHandoff,
)


@admin.register(CampaignInfluence)
class CampaignInfluenceAdmin(admin.ModelAdmin):
    list_display = ("campaign_name", "tenant", "model_type", "influenced_amount",
                    "attribution_pct", "period_label", "recorded_on")
    list_filter = ("tenant", "model_type")
    search_fields = ("campaign_name", "period_label", "notes")


@admin.register(MQLHandoff)
class MQLHandoffAdmin(admin.ModelAdmin):
    list_display = ("number", "tenant", "lead_name", "company", "mql_score", "status", "handoff_date")
    list_filter = ("tenant", "status")
    search_fields = ("number", "lead_name", "company", "source")
    readonly_fields = ("number",)


@admin.register(CampaignPerformance)
class CampaignPerformanceAdmin(admin.ModelAdmin):
    list_display = ("campaign_name", "tenant", "channel", "status", "spend",
                    "leads_generated", "roi", "start_date")
    list_filter = ("tenant", "channel", "status")
    search_fields = ("campaign_name", "notes")


@admin.register(ContentEngagement)
class ContentEngagementAdmin(admin.ModelAdmin):
    list_display = ("content_title", "tenant", "content_type", "views",
                    "downloads", "conversions", "engagement_score", "published_on")
    list_filter = ("tenant", "content_type")
    search_fields = ("content_title",)


@admin.register(MarketingEvent)
class MarketingEventAdmin(admin.ModelAdmin):
    list_display = ("number", "tenant", "name", "event_type", "status",
                    "event_date", "registrations", "attendees", "leads_captured")
    list_filter = ("tenant", "event_type", "status")
    search_fields = ("number", "name", "location")
    readonly_fields = ("number",)
