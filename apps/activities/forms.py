from django import forms

from apps.core.forms import StyledFormMixin

from .models import Activity, EmailLog, Meeting, SalesPlan, SalesTask

DATE = forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")
TIME = forms.TimeInput(attrs={"type": "time"}, format="%H:%M")


class ActivityForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Activity
        fields = [
            "subject", "activity_type", "direction", "outcome",
            "contact_name", "company_name", "owner_name",
            "duration_minutes", "activity_date", "notes",
        ]
        widgets = {"activity_date": DATE}


class SalesTaskForm(StyledFormMixin, forms.ModelForm):
    # `completed_at` is system-set (off the form).
    class Meta:
        model = SalesTask
        fields = [
            "activity", "title", "description", "priority", "status",
            "assigned_to", "related_to", "due_date", "reminder_date",
        ]
        widgets = {"due_date": DATE, "reminder_date": DATE}

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Always scope to the tenant; never fall back to .all() (no cross-tenant leak).
        self.fields["activity"].queryset = (
            Activity.objects.filter(tenant=tenant) if tenant is not None
            else Activity.objects.none()
        )
        self.fields["activity"].required = False


class MeetingForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Meeting
        fields = [
            "title", "meeting_type", "location_type", "status",
            "attendees", "location", "organizer_name",
            "scheduled_date", "start_time", "end_time", "agenda",
        ]
        widgets = {"scheduled_date": DATE, "start_time": TIME, "end_time": TIME}


class EmailLogForm(StyledFormMixin, forms.ModelForm):
    # `sent_at` / `opened_at` are system-set (off the form).
    class Meta:
        model = EmailLog
        fields = [
            "activity", "subject", "direction", "status",
            "from_email", "to_email", "open_count", "click_count", "body",
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Always scope to the tenant; never fall back to .all() (no cross-tenant leak).
        self.fields["activity"].queryset = (
            Activity.objects.filter(tenant=tenant) if tenant is not None
            else Activity.objects.none()
        )
        self.fields["activity"].required = False


class SalesPlanForm(StyledFormMixin, forms.ModelForm):
    # `number` is auto-generated (off the form).
    class Meta:
        model = SalesPlan
        fields = [
            "title", "owner_name", "period_type", "status",
            "start_date", "end_date", "target_calls", "target_meetings",
            "revenue_goal", "objectives",
        ]
        widgets = {"start_date": DATE, "end_date": DATE}
