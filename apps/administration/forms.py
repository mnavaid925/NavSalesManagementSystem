from django import forms

from apps.core.forms import StyledFormMixin

from .models import (
    BackupJob, ComplianceItem, DataPrivacyRule, SecurityPolicy, SystemHealthMetric,
)

DATE = forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")


class SecurityPolicyForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = SecurityPolicy
        fields = ["name", "policy_type", "status", "scope", "severity",
                  "last_reviewed", "description"]
        widgets = {"last_reviewed": DATE}


class DataPrivacyRuleForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = DataPrivacyRule
        fields = ["name", "regulation", "data_category", "action", "status",
                  "retention_days", "notes"]


class ComplianceItemForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ComplianceItem
        fields = ["title", "framework", "status", "owner", "severity",
                  "due_date", "last_audited", "notes"]
        widgets = {"due_date": DATE, "last_audited": DATE}


class BackupJobForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = BackupJob
        # `number` is auto-generated; `started_at`/`completed_at` are system-set (off the form).
        fields = ["name", "backup_type", "status", "storage_location", "size_mb",
                  "retention_days", "scheduled_on", "notes"]
        widgets = {"scheduled_on": DATE}


class SystemHealthMetricForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = SystemHealthMetric
        fields = ["metric_name", "category", "status", "value", "unit",
                  "threshold", "recorded_on", "notes"]
        widgets = {"recorded_on": DATE}
