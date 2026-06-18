"""Tests for activities.forms: required fields, field exclusions, and tenant-scoped FK querysets."""
import pytest
from django.utils import timezone

from apps.activities.forms import (
    ActivityForm, SalesTaskForm, MeetingForm, EmailLogForm, SalesPlanForm,
)
from apps.activities.models import Activity


# ============================================================ ActivityForm
@pytest.mark.django_db
class TestActivityForm:
    def test_valid_form(self):
        form = ActivityForm(data={
            "subject": "Demo Call",
            "activity_type": "call",
            "direction": "outbound",
            "outcome": "pending",
            "contact_name": "Alice",
            "company_name": "Acme",
            "owner_name": "rep_a",
            "duration_minutes": 30,
            "activity_date": timezone.localdate().isoformat(),
            "notes": "Went well.",
        })
        assert form.is_valid(), form.errors

    def test_missing_subject_invalid(self):
        form = ActivityForm(data={
            "activity_type": "call",
            "direction": "outbound",
            "outcome": "pending",
            "duration_minutes": 0,
            "activity_date": timezone.localdate().isoformat(),
        })
        assert not form.is_valid()
        assert "subject" in form.errors

    def test_invalid_activity_type_invalid(self):
        form = ActivityForm(data={
            "subject": "Test",
            "activity_type": "unknown_type",
            "direction": "outbound",
            "outcome": "pending",
            "duration_minutes": 0,
            "activity_date": timezone.localdate().isoformat(),
        })
        assert not form.is_valid()

    def test_tenant_not_in_form_fields(self):
        form = ActivityForm()
        assert "tenant" not in form.fields

    def test_created_at_not_in_form_fields(self):
        form = ActivityForm()
        assert "created_at" not in form.fields

    def test_updated_at_not_in_form_fields(self):
        form = ActivityForm()
        assert "updated_at" not in form.fields

    def test_optional_fields_not_required(self):
        form = ActivityForm(data={
            "subject": "Minimal",
            "activity_type": "call",
            "direction": "outbound",
            "outcome": "pending",
            "duration_minutes": 0,
            "activity_date": timezone.localdate().isoformat(),
            "contact_name": "",
            "company_name": "",
            "owner_name": "",
            "notes": "",
        })
        assert form.is_valid(), form.errors


# ============================================================ SalesTaskForm
@pytest.mark.django_db
class TestSalesTaskForm:
    def test_valid_form(self, tenant_a):
        form = SalesTaskForm(data={
            "activity": "",
            "title": "Follow up",
            "description": "Call back tomorrow",
            "priority": "high",
            "status": "open",
            "assigned_to": "rep_a",
            "related_to": "Acme Deal",
            "due_date": timezone.localdate().isoformat(),
            "reminder_date": "",
        }, tenant=tenant_a)
        assert form.is_valid(), form.errors

    def test_missing_title_invalid(self, tenant_a):
        form = SalesTaskForm(data={
            "activity": "",
            "description": "",
            "priority": "medium",
            "status": "open",
        }, tenant=tenant_a)
        assert not form.is_valid()
        assert "title" in form.errors

    def test_tenant_not_in_form_fields(self, tenant_a):
        form = SalesTaskForm(tenant=tenant_a)
        assert "tenant" not in form.fields

    def test_completed_at_not_in_form_fields(self, tenant_a):
        """completed_at is system-set, not a form field."""
        form = SalesTaskForm(tenant=tenant_a)
        assert "completed_at" not in form.fields

    def test_created_at_not_in_form_fields(self, tenant_a):
        form = SalesTaskForm(tenant=tenant_a)
        assert "created_at" not in form.fields

    def test_activity_field_scoped_to_tenant(self, tenant_a, tenant_b, activity_a, activity_b):
        """activity queryset must only include same-tenant activities."""
        form = SalesTaskForm(tenant=tenant_a)
        activity_pks = list(form.fields["activity"].queryset.values_list("pk", flat=True))
        assert activity_a.pk in activity_pks
        assert activity_b.pk not in activity_pks

    def test_activity_field_empty_queryset_when_no_tenant(self):
        """Without a tenant, activity queryset must be empty (not .all())."""
        form = SalesTaskForm(tenant=None)
        assert form.fields["activity"].queryset.count() == 0

    def test_activity_field_not_required(self, tenant_a):
        form = SalesTaskForm(tenant=tenant_a)
        assert not form.fields["activity"].required

    def test_invalid_priority_invalid(self, tenant_a):
        form = SalesTaskForm(data={
            "title": "Test Task",
            "priority": "super_urgent",
            "status": "open",
        }, tenant=tenant_a)
        assert not form.is_valid()

    def test_invalid_status_invalid(self, tenant_a):
        form = SalesTaskForm(data={
            "title": "Test Task",
            "priority": "medium",
            "status": "flying",
        }, tenant=tenant_a)
        assert not form.is_valid()


# ============================================================ MeetingForm
@pytest.mark.django_db
class TestMeetingForm:
    def test_valid_form(self):
        form = MeetingForm(data={
            "title": "Product Demo",
            "meeting_type": "demo",
            "location_type": "video",
            "status": "scheduled",
            "attendees": "alice, bob",
            "location": "",
            "organizer_name": "rep_a",
            "scheduled_date": timezone.localdate().isoformat(),
            "start_time": "10:00",
            "end_time": "11:00",
            "agenda": "Show product.",
        })
        assert form.is_valid(), form.errors

    def test_missing_title_invalid(self):
        form = MeetingForm(data={
            "meeting_type": "demo",
            "location_type": "video",
            "status": "scheduled",
            "scheduled_date": timezone.localdate().isoformat(),
        })
        assert not form.is_valid()
        assert "title" in form.errors

    def test_tenant_not_in_form_fields(self):
        form = MeetingForm()
        assert "tenant" not in form.fields

    def test_created_at_not_in_form_fields(self):
        form = MeetingForm()
        assert "created_at" not in form.fields

    def test_updated_at_not_in_form_fields(self):
        form = MeetingForm()
        assert "updated_at" not in form.fields

    def test_invalid_meeting_type_invalid(self):
        form = MeetingForm(data={
            "title": "Test Meeting",
            "meeting_type": "invalid_type",
            "location_type": "video",
            "status": "scheduled",
            "scheduled_date": timezone.localdate().isoformat(),
        })
        assert not form.is_valid()

    def test_optional_fields_not_required(self):
        form = MeetingForm(data={
            "title": "Minimal Meeting",
            "meeting_type": "discovery",
            "location_type": "video",
            "status": "scheduled",
            "attendees": "",
            "location": "",
            "organizer_name": "",
            "scheduled_date": timezone.localdate().isoformat(),
            "start_time": "",
            "end_time": "",
            "agenda": "",
        })
        assert form.is_valid(), form.errors


# ============================================================ EmailLogForm
@pytest.mark.django_db
class TestEmailLogForm:
    def test_valid_form(self, tenant_a):
        form = EmailLogForm(data={
            "activity": "",
            "subject": "Follow-up Email",
            "direction": "outbound",
            "status": "draft",
            "from_email": "rep@test.com",
            "to_email": "client@acme.com",
            "open_count": 0,
            "click_count": 0,
            "body": "Hello World",
        }, tenant=tenant_a)
        assert form.is_valid(), form.errors

    def test_missing_subject_invalid(self, tenant_a):
        form = EmailLogForm(data={
            "activity": "",
            "direction": "outbound",
            "status": "draft",
        }, tenant=tenant_a)
        assert not form.is_valid()
        assert "subject" in form.errors

    def test_tenant_not_in_form_fields(self, tenant_a):
        form = EmailLogForm(tenant=tenant_a)
        assert "tenant" not in form.fields

    def test_sent_at_not_in_form_fields(self, tenant_a):
        """sent_at is system-set, not a form field."""
        form = EmailLogForm(tenant=tenant_a)
        assert "sent_at" not in form.fields

    def test_opened_at_not_in_form_fields(self, tenant_a):
        """opened_at is system-set, not a form field."""
        form = EmailLogForm(tenant=tenant_a)
        assert "opened_at" not in form.fields

    def test_created_at_not_in_form_fields(self, tenant_a):
        form = EmailLogForm(tenant=tenant_a)
        assert "created_at" not in form.fields

    def test_activity_field_scoped_to_tenant(self, tenant_a, tenant_b, activity_a, activity_b):
        """activity queryset must only include same-tenant activities."""
        form = EmailLogForm(tenant=tenant_a)
        activity_pks = list(form.fields["activity"].queryset.values_list("pk", flat=True))
        assert activity_a.pk in activity_pks
        assert activity_b.pk not in activity_pks

    def test_activity_field_empty_queryset_when_no_tenant(self):
        """Without a tenant, activity queryset must be empty (not .all())."""
        form = EmailLogForm(tenant=None)
        assert form.fields["activity"].queryset.count() == 0

    def test_activity_field_not_required(self, tenant_a):
        form = EmailLogForm(tenant=tenant_a)
        assert not form.fields["activity"].required

    def test_invalid_email_format_rejected(self, tenant_a):
        form = EmailLogForm(data={
            "activity": "",
            "subject": "Test",
            "direction": "outbound",
            "status": "draft",
            "from_email": "not-an-email",
            "to_email": "client@acme.com",
            "open_count": 0,
            "click_count": 0,
            "body": "",
        }, tenant=tenant_a)
        assert not form.is_valid()
        assert "from_email" in form.errors


# ============================================================ SalesPlanForm
@pytest.mark.django_db
class TestSalesPlanForm:
    def test_valid_form(self):
        form = SalesPlanForm(data={
            "title": "Weekly Plan Q1",
            "owner_name": "rep_a",
            "period_type": "weekly",
            "status": "draft",
            "start_date": timezone.localdate().isoformat(),
            "end_date": "",
            "target_calls": 20,
            "target_meetings": 5,
            "revenue_goal": "10000.00",
            "objectives": "Hit quota.",
        })
        assert form.is_valid(), form.errors

    def test_missing_title_invalid(self):
        form = SalesPlanForm(data={
            "period_type": "weekly",
            "status": "draft",
            "start_date": timezone.localdate().isoformat(),
            "target_calls": 10,
            "target_meetings": 2,
            "revenue_goal": "5000.00",
        })
        assert not form.is_valid()
        assert "title" in form.errors

    def test_number_not_in_form_fields(self):
        """number is auto-generated, should not be in the form."""
        form = SalesPlanForm()
        assert "number" not in form.fields

    def test_tenant_not_in_form_fields(self):
        form = SalesPlanForm()
        assert "tenant" not in form.fields

    def test_created_at_not_in_form_fields(self):
        form = SalesPlanForm()
        assert "created_at" not in form.fields

    def test_updated_at_not_in_form_fields(self):
        form = SalesPlanForm()
        assert "updated_at" not in form.fields

    def test_invalid_period_type_invalid(self):
        form = SalesPlanForm(data={
            "title": "Test Plan",
            "period_type": "quarterly",
            "status": "draft",
            "start_date": timezone.localdate().isoformat(),
            "target_calls": 0,
            "target_meetings": 0,
            "revenue_goal": "0.00",
        })
        assert not form.is_valid()

    def test_invalid_status_invalid(self):
        form = SalesPlanForm(data={
            "title": "Test Plan",
            "period_type": "weekly",
            "status": "unknown_status",
            "start_date": timezone.localdate().isoformat(),
            "target_calls": 0,
            "target_meetings": 0,
            "revenue_goal": "0.00",
        })
        assert not form.is_valid()

    def test_optional_fields_not_required(self):
        form = SalesPlanForm(data={
            "title": "Minimal Plan",
            "owner_name": "",
            "period_type": "weekly",
            "status": "draft",
            "start_date": timezone.localdate().isoformat(),
            "end_date": "",
            "target_calls": 0,
            "target_meetings": 0,
            "revenue_goal": "0.00",
            "objectives": "",
        })
        assert form.is_valid(), form.errors
