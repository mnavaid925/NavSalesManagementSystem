from django import forms

from apps.core.forms import StyledFormMixin

from .models import (
    Lead, LeadConversion, LeadScore, LeadSource, NurtureCampaign,
)

DATE = forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")


class LeadSourceForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = LeadSource
        fields = ["name", "source_type", "routing_rule", "status",
                  "default_owner", "cost_per_lead", "description"]


class NurtureCampaignForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = NurtureCampaign
        fields = ["name", "channel", "status", "step_count", "cadence_days",
                  "enrolled_count", "start_on", "end_on", "goal"]
        widgets = {"start_on": DATE, "end_on": DATE}


class LeadForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Lead
        # `number` is auto-generated (off the form).
        fields = ["source", "campaign", "first_name", "last_name", "company",
                  "job_title", "email", "phone", "status", "rating", "owner",
                  "estimated_value", "captured_on", "notes"]
        widgets = {"captured_on": DATE}

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Always scope FK choices to the tenant; never fall back to .all() (no leak).
        self.fields["source"].queryset = (
            LeadSource.objects.filter(tenant=tenant) if tenant is not None
            else LeadSource.objects.none()
        )
        self.fields["campaign"].queryset = (
            NurtureCampaign.objects.filter(tenant=tenant) if tenant is not None
            else NurtureCampaign.objects.none()
        )
        self.fields["source"].required = False
        self.fields["campaign"].required = False


class LeadScoreForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = LeadScore
        fields = ["lead", "score", "grade", "scoring_model",
                  "demographic_points", "behavioral_points", "reason", "scored_on"]
        widgets = {"scored_on": DATE}

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["lead"].queryset = (
            Lead.objects.filter(tenant=tenant) if tenant is not None
            else Lead.objects.none()
        )


class LeadConversionForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = LeadConversion
        # `number` is auto-generated; `converted_at` is system-set (off the form).
        fields = ["lead", "status", "outcome", "assigned_to", "deal_value", "handoff_notes"]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["lead"].queryset = (
            Lead.objects.filter(tenant=tenant) if tenant is not None
            else Lead.objects.none()
        )
