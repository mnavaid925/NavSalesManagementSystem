from django import forms

from apps.core.forms import StyledFormMixin

from .models import (
    CallActivity, FieldVisit, MobileAlert, MobileDevice, MobileQuote,
)

DATE = forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")


class MobileDeviceForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = MobileDevice
        # `last_sync` is system-set (off the form).
        fields = ["device_name", "user_name", "platform", "status",
                  "app_version", "push_enabled", "notes"]


class FieldVisitForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = FieldVisit
        # `number` is auto-generated.
        fields = ["rep_name", "account_name", "visit_type", "status",
                  "scheduled_on", "location", "duration_minutes", "notes"]
        widgets = {"scheduled_on": DATE}


class MobileQuoteForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = MobileQuote
        # `number` is auto-generated.
        fields = ["rep_name", "customer_name", "amount", "discount_pct",
                  "status", "submitted_on", "notes"]
        widgets = {"submitted_on": DATE}


class CallActivityForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = CallActivity
        fields = ["rep_name", "contact_name", "direction", "call_type",
                  "outcome", "duration_seconds", "call_date", "notes"]
        widgets = {"call_date": DATE}


class MobileAlertForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = MobileAlert
        fields = ["title", "alert_type", "priority", "status",
                  "recipient", "body", "notes"]
