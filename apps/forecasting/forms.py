from django import forms

from apps.core.forms import StyledFormMixin

from .models import (
    Forecast, ForecastAccuracy, ForecastAdjustment, ForecastCategory, Quota,
)

DATE = forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")


class ForecastCategoryForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ForecastCategory
        fields = ["name", "commitment", "probability", "weight", "is_active", "description"]


class ForecastForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Forecast
        # `number` is auto-generated; `submitted_at` is system-set (off the form).
        fields = [
            "category", "name", "owner_name", "period_type", "period_label",
            "period_start", "period_end", "pipeline_amount", "commit_amount",
            "best_case_amount", "ai_predicted_amount", "ai_confidence", "status", "notes",
        ]
        widgets = {"period_start": DATE, "period_end": DATE}

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Always scope to the tenant; never fall back to .all() (no cross-tenant leak).
        self.fields["category"].queryset = (
            ForecastCategory.objects.filter(tenant=tenant) if tenant is not None
            else ForecastCategory.objects.none()
        )
        self.fields["category"].required = False


class QuotaForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Quota
        fields = [
            "owner_name", "period_type", "period_label", "period_start", "period_end",
            "target_amount", "attained_amount", "status", "notes",
        ]
        widgets = {"period_start": DATE, "period_end": DATE}


class ForecastAdjustmentForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ForecastAdjustment
        # `approved_at` is system-set (off the form).
        fields = ["forecast", "adjustment_type", "amount", "adjusted_by", "status", "reason"]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Always scope to the tenant; never fall back to .all() (no cross-tenant leak).
        self.fields["forecast"].queryset = (
            Forecast.objects.filter(tenant=tenant) if tenant is not None
            else Forecast.objects.none()
        )


class ForecastAccuracyForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ForecastAccuracy
        # `variance_amount` is system-computed (off the form).
        fields = [
            "forecast", "period_label", "forecasted_amount", "actual_amount",
            "accuracy_pct", "grade", "analyzed_on", "notes",
        ]
        widgets = {"analyzed_on": DATE}

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Always scope to the tenant; never fall back to .all() (no cross-tenant leak).
        self.fields["forecast"].queryset = (
            Forecast.objects.filter(tenant=tenant) if tenant is not None
            else Forecast.objects.none()
        )
        self.fields["forecast"].required = False
