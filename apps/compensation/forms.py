from django import forms

from apps.core.forms import StyledFormMixin

from .models import (
    Clawback, CommissionPlan, Earning, GlobalPlanVariation, Payout,
)

DATE = forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")


class CommissionPlanForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = CommissionPlan
        fields = ["name", "code", "plan_type", "status", "base_rate",
                  "target_quota", "effective_from", "effective_to", "description"]
        widgets = {"effective_from": DATE, "effective_to": DATE}


class EarningForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Earning
        # `number` is auto-generated; `approved_at` is system-set (off the form).
        fields = ["plan", "rep_name", "deal_reference", "deal_amount",
                  "commission_amount", "status", "earned_on", "notes"]
        widgets = {"earned_on": DATE}

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Always scope to the tenant; never fall back to .all() (no cross-tenant leak).
        self.fields["plan"].queryset = (
            CommissionPlan.objects.filter(tenant=tenant) if tenant is not None
            else CommissionPlan.objects.none()
        )
        self.fields["plan"].required = False


class ClawbackForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Clawback
        # `applied_at` is system-set (off the form).
        fields = ["earning", "rep_name", "reason", "status",
                  "amount", "effective_on", "notes"]
        widgets = {"effective_on": DATE}

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["earning"].queryset = (
            Earning.objects.filter(tenant=tenant) if tenant is not None
            else Earning.objects.none()
        )
        self.fields["earning"].required = False


class GlobalPlanVariationForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = GlobalPlanVariation
        fields = ["plan", "region", "currency", "status", "fx_rate",
                  "local_quota", "rate_adjustment", "effective_from", "notes"]
        widgets = {"effective_from": DATE}

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["plan"].queryset = (
            CommissionPlan.objects.filter(tenant=tenant) if tenant is not None
            else CommissionPlan.objects.none()
        )
        self.fields["plan"].required = False


class PayoutForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Payout
        # `number` is auto-generated; `paid_at` is system-set (off the form).
        fields = ["rep_name", "method", "status", "gross_amount", "deductions",
                  "net_amount", "period_label", "scheduled_on", "reference", "notes"]
        widgets = {"scheduled_on": DATE}
