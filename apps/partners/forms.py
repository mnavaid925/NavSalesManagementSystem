from django import forms

from apps.core.forms import StyledFormMixin

from .models import (
    ChannelConflict, DealRegistration, Partner, PartnerCollateral, PartnerPerformance,
)

DATE = forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")


class PartnerForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Partner
        fields = ["name", "partner_type", "tier", "status", "region",
                  "contact_name", "contact_email", "onboarded_on", "notes"]
        widgets = {"onboarded_on": DATE}


class DealRegistrationForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = DealRegistration
        # `number` is auto-generated (off the form).
        fields = ["partner", "deal_name", "customer_name", "amount",
                  "status", "registered_on", "expires_on", "notes"]
        widgets = {"registered_on": DATE, "expires_on": DATE}

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Always scope to the tenant; never fall back to .all() (no cross-tenant leak).
        self.fields["partner"].queryset = (
            Partner.objects.filter(tenant=tenant) if tenant is not None
            else Partner.objects.none()
        )
        self.fields["partner"].required = False


class PartnerCollateralForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = PartnerCollateral
        fields = ["partner", "title", "asset_type", "access_level",
                  "version", "published_on", "notes"]
        widgets = {"published_on": DATE}

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["partner"].queryset = (
            Partner.objects.filter(tenant=tenant) if tenant is not None
            else Partner.objects.none()
        )
        self.fields["partner"].required = False


class PartnerPerformanceForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = PartnerPerformance
        fields = ["partner", "period_label", "revenue", "deals_closed", "quota",
                  "attainment", "certification_count", "satisfaction_score", "recorded_on"]
        widgets = {"recorded_on": DATE}

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["partner"].queryset = (
            Partner.objects.filter(tenant=tenant) if tenant is not None
            else Partner.objects.none()
        )
        self.fields["partner"].required = False


class ChannelConflictForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ChannelConflict
        # `number` is auto-generated (off the form).
        fields = ["partner", "conflict_type", "severity", "status",
                  "account_name", "reported_on", "resolution", "notes"]
        widgets = {"reported_on": DATE}

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["partner"].queryset = (
            Partner.objects.filter(tenant=tenant) if tenant is not None
            else Partner.objects.none()
        )
        self.fields["partner"].required = False
