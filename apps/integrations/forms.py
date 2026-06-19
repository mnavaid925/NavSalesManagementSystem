from django import forms

from apps.core.forms import StyledFormMixin

from .models import ApiKey, Connector, SyncJob, SyncLog, Webhook

DATE = forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")


class ConnectorForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Connector
        # `last_sync` is system-set (off the form).
        fields = ["name", "category", "provider", "status", "auth_type", "notes"]


class SyncJobForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = SyncJob
        # `number` is auto-generated; `last_run` + `records_synced` are system/run-history metrics (off the form).
        fields = ["connector", "name", "direction", "status",
                  "schedule", "notes"]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Always scope to the tenant; never fall back to .all() (no cross-tenant leak).
        self.fields["connector"].queryset = (
            Connector.objects.filter(tenant=tenant) if tenant is not None
            else Connector.objects.none()
        )
        self.fields["connector"].required = False


class SyncLogForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = SyncLog
        # `occurred_at` is system-set (off the form).
        fields = ["job", "level", "message", "records_affected", "duration_ms"]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["job"].queryset = (
            SyncJob.objects.filter(tenant=tenant) if tenant is not None
            else SyncJob.objects.none()
        )
        self.fields["job"].required = False


class WebhookForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Webhook
        # `secret` is a credential (off the form); `last_triggered` is system-set.
        fields = ["name", "target_url", "event_type", "http_method", "status", "notes"]


class ApiKeyForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ApiKey
        # `key`/`key_prefix` are generated (off the form); `last_used` is system-set.
        fields = ["name", "environment", "scopes", "status", "expires_on", "notes"]
        widgets = {"expires_on": DATE}
