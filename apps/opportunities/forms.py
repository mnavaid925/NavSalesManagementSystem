from django import forms

from apps.core.forms import StyledFormMixin

from .models import (
    Competitor, DealCollaborator, Opportunity, OpportunityActivity, PipelineStage,
)

DATE = forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")


class PipelineStageForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = PipelineStage
        fields = ["name", "description", "order", "probability", "stage_type", "is_active"]


class OpportunityForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Opportunity
        # `number` is auto-generated; `closed_at` is system-set (off the form).
        fields = [
            "name", "account_name", "stage", "status", "priority", "forecast_category",
            "amount", "probability", "owner_name", "source", "expected_close_date", "description",
        ]
        widgets = {"expected_close_date": DATE}

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Always scope FK choices to the tenant; never fall back to .all() (no cross-tenant leak).
        self.fields["stage"].queryset = (
            PipelineStage.objects.filter(tenant=tenant) if tenant is not None
            else PipelineStage.objects.none()
        )
        self.fields["stage"].required = False


class OpportunityActivityForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = OpportunityActivity
        fields = [
            "opportunity", "subject", "activity_type", "outcome",
            "performed_by", "activity_date", "notes",
        ]
        widgets = {"activity_date": DATE}

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["opportunity"].queryset = (
            Opportunity.objects.filter(tenant=tenant) if tenant is not None
            else Opportunity.objects.none()
        )


class CompetitorForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Competitor
        fields = [
            "opportunity", "name", "threat_level", "status",
            "strengths", "weaknesses", "our_strategy",
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["opportunity"].queryset = (
            Opportunity.objects.filter(tenant=tenant) if tenant is not None
            else Opportunity.objects.none()
        )


class DealCollaboratorForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = DealCollaborator
        fields = [
            "opportunity", "member_name", "email", "team_role", "status", "contribution",
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["opportunity"].queryset = (
            Opportunity.objects.filter(tenant=tenant) if tenant is not None
            else Opportunity.objects.none()
        )
