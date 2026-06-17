from django import forms

from apps.core.forms import StyledFormMixin

from .models import (
    CallRecording, CompetitiveCard, ContentAsset, Playbook, TrainingRecord,
)

DATE = forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")


class ContentAssetForm(StyledFormMixin, forms.ModelForm):
    # `published_at` and `view_count` are system-managed (off the form).
    class Meta:
        model = ContentAsset
        fields = ["title", "asset_type", "status", "description",
                  "tags", "file_url", "owner"]


class PlaybookForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Playbook
        fields = ["title", "stage", "status", "persona",
                  "summary", "guidance", "owner", "version"]


class TrainingRecordForm(StyledFormMixin, forms.ModelForm):
    # `completed_at` is system-set (off the form).
    class Meta:
        model = TrainingRecord
        fields = ["course_name", "rep_name", "kind", "status", "provider",
                  "score", "enrolled_on", "due_on", "expires_on", "notes"]
        widgets = {"enrolled_on": DATE, "due_on": DATE, "expires_on": DATE}


class CallRecordingForm(StyledFormMixin, forms.ModelForm):
    # `reviewed_at` is system-set (off the form).
    class Meta:
        model = CallRecording
        fields = ["title", "rep_name", "coach_name", "call_type", "status",
                  "duration_minutes", "recording_url", "score", "coaching_notes", "call_date"]
        widgets = {"call_date": DATE}


class CompetitiveCardForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = CompetitiveCard
        fields = ["competitor_name", "category", "threat_level", "status", "overview",
                  "our_strengths", "their_strengths", "objection_handling",
                  "owner", "last_updated_on"]
        widgets = {"last_updated_on": DATE}
