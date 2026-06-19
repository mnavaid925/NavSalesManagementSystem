from django import forms

from apps.core.forms import StyledFormMixin

from .models import (
    CampaignInfluence, CampaignPerformance, ContentEngagement, MarketingEvent, MQLHandoff,
)

DATE = forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")


class CampaignInfluenceForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = CampaignInfluence
        fields = ["campaign_name", "model_type", "influenced_amount", "opportunities_count",
                  "attribution_pct", "period_label", "recorded_on", "notes"]
        widgets = {"recorded_on": DATE}


class MQLHandoffForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = MQLHandoff
        # `number` is auto-generated (off the form).
        fields = ["lead_name", "company", "mql_score", "status",
                  "source", "handed_to", "handoff_date", "notes"]
        widgets = {"handoff_date": DATE}


class CampaignPerformanceForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = CampaignPerformance
        fields = ["campaign_name", "channel", "status", "spend", "leads_generated",
                  "revenue_influenced", "roi", "start_date", "notes"]
        widgets = {"start_date": DATE}


class ContentEngagementForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ContentEngagement
        fields = ["content_title", "content_type", "views", "downloads",
                  "avg_time_seconds", "conversions", "engagement_score", "published_on"]
        widgets = {"published_on": DATE}


class MarketingEventForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = MarketingEvent
        # `number` is auto-generated (off the form).
        fields = ["name", "event_type", "status", "event_date", "registrations",
                  "attendees", "leads_captured", "location", "notes"]
        widgets = {"event_date": DATE}
