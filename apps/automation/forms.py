from django import forms

from apps.core.forms import StyledFormMixin

from .models import (
    AlertRule, ApprovalWorkflow, AssignmentRule, EnrichmentRule, ProcessFlow,
)


class ProcessFlowForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ProcessFlow
        # `last_run` is system-set (off the form).
        fields = ["name", "trigger_event", "object_type", "status",
                  "steps_count", "description"]


class AssignmentRuleForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = AssignmentRule
        fields = ["name", "entity", "assign_strategy", "status",
                  "priority", "criteria", "assignee_pool", "notes"]


class ApprovalWorkflowForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ApprovalWorkflow
        fields = ["name", "approval_type", "status", "threshold_amount",
                  "steps_count", "escalation_hours", "approvers", "notes"]


class AlertRuleForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = AlertRule
        fields = ["name", "channel", "severity", "status",
                  "trigger_condition", "recipients", "frequency", "notes"]


class EnrichmentRuleForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = EnrichmentRule
        # `last_run`, `records_processed`, `success_rate` are system/run-history metrics (off the form).
        fields = ["name", "data_source", "operation", "status", "target_field", "notes"]
