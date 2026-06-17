from django import forms

from apps.core.forms import StyledFormMixin

from .models import (
    CoverageModel, QuotaPlan, Territory, TerritoryAssignment, TerritoryPerformance,
)

DATE = forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")


class TerritoryForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Territory
        fields = ["name", "code", "territory_type", "status", "region", "country",
                  "description", "account_count", "annual_potential"]


class TerritoryAssignmentForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = TerritoryAssignment
        fields = ["territory", "rep_name", "rep_email", "assignment_role", "status",
                  "workload_percent", "effective_date", "end_date", "notes"]
        widgets = {"effective_date": DATE, "end_date": DATE}

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Always scope the FK to the tenant; never fall back to .all() (no cross-tenant leak).
        self.fields["territory"].queryset = (
            Territory.objects.filter(tenant=tenant) if tenant is not None
            else Territory.objects.none()
        )


class QuotaPlanForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = QuotaPlan
        # `number` is auto-generated; `approved_at` is system-set (off the form).
        fields = ["territory", "name", "period_type", "fiscal_year", "status",
                  "target_amount", "stretch_amount", "start_date", "end_date", "notes"]
        widgets = {"start_date": DATE, "end_date": DATE}

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["territory"].queryset = (
            Territory.objects.filter(tenant=tenant) if tenant is not None
            else Territory.objects.none()
        )
        self.fields["territory"].required = False


class CoverageModelForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = CoverageModel
        fields = ["name", "model_type", "status", "target_ratio", "rep_capacity",
                  "coverage_score", "description"]


class TerritoryPerformanceForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = TerritoryPerformance
        # `attainment_percent` is computed in save() — kept off the form.
        fields = ["territory", "period_type", "period_label", "rating",
                  "quota_amount", "actual_amount", "pipeline_amount", "deals_won", "period_end"]
        widgets = {"period_end": DATE}

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["territory"].queryset = (
            Territory.objects.filter(tenant=tenant) if tenant is not None
            else Territory.objects.none()
        )
