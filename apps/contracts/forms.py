from django import forms

from apps.core.forms import StyledFormMixin

from .models import (
    Contract, ContractClause, ContractObligation, RenewalSchedule, UsageRecord,
)

DATE = forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")


class ContractForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Contract
        # `number` is auto-generated (off the form).
        fields = ["title", "account_name", "contract_type", "status", "value",
                  "start_date", "end_date", "owner", "notes"]
        widgets = {"start_date": DATE, "end_date": DATE}


class ContractClauseForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ContractClause
        fields = ["contract", "title", "clause_type", "status",
                  "risk_level", "body", "notes"]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Always scope to the tenant; never fall back to .all() (no cross-tenant leak).
        self.fields["contract"].queryset = (
            Contract.objects.filter(tenant=tenant) if tenant is not None
            else Contract.objects.none()
        )
        self.fields["contract"].required = False


class RenewalScheduleForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = RenewalSchedule
        fields = ["contract", "account_name", "status", "renewal_date",
                  "current_value", "proposed_value", "auto_renew", "notice_days", "notes"]
        widgets = {"renewal_date": DATE}

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["contract"].queryset = (
            Contract.objects.filter(tenant=tenant) if tenant is not None
            else Contract.objects.none()
        )
        self.fields["contract"].required = False


class UsageRecordForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = UsageRecord
        fields = ["contract", "account_name", "metric_name", "quantity",
                  "unit", "rate", "amount", "period_label", "recorded_on"]
        widgets = {"recorded_on": DATE}

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["contract"].queryset = (
            Contract.objects.filter(tenant=tenant) if tenant is not None
            else Contract.objects.none()
        )
        self.fields["contract"].required = False


class ContractObligationForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ContractObligation
        fields = ["contract", "title", "obligation_type", "status",
                  "due_date", "owner", "notes"]
        widgets = {"due_date": DATE}

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["contract"].queryset = (
            Contract.objects.filter(tenant=tenant) if tenant is not None
            else Contract.objects.none()
        )
        self.fields["contract"].required = False
