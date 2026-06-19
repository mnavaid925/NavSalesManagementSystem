from django import forms

from apps.core.forms import StyledFormMixin

from .models import (
    Advocacy, HealthScore, OnboardingPlan, QBR, Renewal,
)

DATE = forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")


class HealthScoreForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = HealthScore
        fields = ["account_name", "owner", "score", "risk_level", "trend",
                  "arr", "last_reviewed", "notes"]
        widgets = {"last_reviewed": DATE}


class RenewalForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Renewal
        # `number` is auto-generated (off the form).
        fields = ["account_name", "owner", "renewal_type", "status", "arr_current",
                  "arr_proposed", "probability", "renewal_date", "notes"]
        widgets = {"renewal_date": DATE}


class OnboardingPlanForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = OnboardingPlan
        fields = ["account_name", "plan_name", "owner", "status", "progress_pct",
                  "start_date", "target_go_live", "notes"]
        widgets = {"start_date": DATE, "target_go_live": DATE}


class AdvocacyForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Advocacy
        fields = ["account_name", "contact_name", "advocacy_type", "status",
                  "nps_score", "last_engaged", "notes"]
        widgets = {"last_engaged": DATE}


class QBRForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = QBR
        fields = ["account_name", "period_label", "owner", "status", "sentiment",
                  "scheduled_on", "health_summary", "notes"]
        widgets = {"scheduled_on": DATE}
