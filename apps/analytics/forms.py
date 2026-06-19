from django import forms

from apps.core.forms import StyledFormMixin

from .models import (
    Benchmark, ConversionFunnel, RepScorecard, SalesVelocity, WinLossAnalysis,
)

DATE = forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")


class WinLossAnalysisForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = WinLossAnalysis
        fields = ["deal_name", "rep_name", "outcome", "amount", "competitor",
                  "reason_category", "closed_on", "notes"]
        widgets = {"closed_on": DATE}


class SalesVelocityForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = SalesVelocity
        fields = ["period_label", "segment", "avg_deal_size", "win_rate",
                  "sales_cycle_days", "pipeline_value", "velocity_score", "recorded_on"]
        widgets = {"recorded_on": DATE}


class ConversionFunnelForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ConversionFunnel
        fields = ["stage_name", "segment", "period_label", "entered_count",
                  "converted_count", "conversion_rate", "avg_days_in_stage", "recorded_on"]
        widgets = {"recorded_on": DATE}


class RepScorecardForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = RepScorecard
        fields = ["rep_name", "period_label", "quota", "attainment", "deals_won",
                  "deals_lost", "activities", "ranking", "grade", "notes"]


class BenchmarkForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Benchmark
        fields = ["metric_name", "category", "our_value", "peer_median",
                  "top_quartile", "period_label", "status", "recorded_on"]
        widgets = {"recorded_on": DATE}
