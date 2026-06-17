from django import forms

from apps.core.forms import StyledFormMixin

from .models import (
    BrandingSetting, EncryptionKey, HealthMetric, Invoice, OnboardingStep, Subscription,
)

DATE = forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")


class OnboardingStepForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = OnboardingStep
        fields = ["title", "description", "order", "status"]


class SubscriptionForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ["plan", "status", "seats", "monthly_amount",
                  "started_on", "renews_on", "is_auto_renew"]
        widgets = {"started_on": DATE, "renews_on": DATE}


class InvoiceForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Invoice
        # `number` is auto-generated; `paid_at` is system-set (off the form, L22).
        fields = ["subscription", "amount", "status",
                  "period_start", "period_end", "issued_on", "due_on", "notes"]
        widgets = {
            "period_start": DATE, "period_end": DATE,
            "issued_on": DATE, "due_on": DATE,
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant is not None and "subscription" in self.fields:
            self.fields["subscription"].queryset = Subscription.objects.filter(tenant=tenant)
        self.fields["subscription"].required = False


class EncryptionKeyForm(StyledFormMixin, forms.ModelForm):
    # WARNING: key_prefix + hashed_key are intentionally excluded — the secret is
    # generated server-side in the view and only its prefix + hash are stored (L20).
    class Meta:
        model = EncryptionKey
        fields = ["label", "algorithm", "status"]


class BrandingSettingForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = BrandingSetting
        fields = ["name", "is_default", "logo_url", "primary_color", "accent_color",
                  "login_message", "email_from_name", "email_signature", "theme"]
        widgets = {
            "primary_color": forms.TextInput(attrs={"type": "color"}),
            "accent_color": forms.TextInput(attrs={"type": "color"}),
        }


class HealthMetricForm(StyledFormMixin, forms.ModelForm):
    # `recorded_at` is the system observation time — set automatically, off the form.
    class Meta:
        model = HealthMetric
        fields = ["metric_name", "category", "value", "unit", "threshold", "status"]
