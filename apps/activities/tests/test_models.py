"""Tests for activities.models: Activity, SalesTask, Meeting, EmailLog, SalesPlan."""
import pytest
from django.utils import timezone

from apps.activities.models import Activity, SalesTask, Meeting, EmailLog, SalesPlan


# ============================================================ Activity
@pytest.mark.django_db
class TestActivityModel:
    def test_str_returns_subject(self, activity_a):
        assert str(activity_a) == "Call with Acme"

    def test_default_activity_type_is_call(self, tenant_a):
        a = Activity.objects.create(tenant=tenant_a, subject="Test")
        assert a.activity_type == Activity.TYPE_CALL

    def test_default_direction_is_outbound(self, tenant_a):
        a = Activity.objects.create(tenant=tenant_a, subject="Test")
        assert a.direction == Activity.DIRECTION_OUTBOUND

    def test_default_outcome_is_pending(self, tenant_a):
        a = Activity.objects.create(tenant=tenant_a, subject="Test")
        assert a.outcome == Activity.OUTCOME_PENDING

    def test_default_duration_is_zero(self, tenant_a):
        a = Activity.objects.create(tenant=tenant_a, subject="Test")
        assert a.duration_minutes == 0

    def test_type_choices_contain_all_six(self):
        choices = dict(Activity.TYPE_CHOICES)
        assert Activity.TYPE_CALL in choices
        assert Activity.TYPE_EMAIL in choices
        assert Activity.TYPE_MEETING in choices
        assert Activity.TYPE_NOTE in choices
        assert Activity.TYPE_DEMO in choices
        assert Activity.TYPE_VISIT in choices

    def test_direction_choices_contain_all_three(self):
        choices = dict(Activity.DIRECTION_CHOICES)
        assert Activity.DIRECTION_INBOUND in choices
        assert Activity.DIRECTION_OUTBOUND in choices
        assert Activity.DIRECTION_INTERNAL in choices

    def test_outcome_choices_contain_all_five(self):
        choices = dict(Activity.OUTCOME_CHOICES)
        assert Activity.OUTCOME_PENDING in choices
        assert Activity.OUTCOME_SUCCESSFUL in choices
        assert Activity.OUTCOME_NO_ANSWER in choices
        assert Activity.OUTCOME_FOLLOW_UP in choices
        assert Activity.OUTCOME_NOT_INTERESTED in choices

    def test_activity_date_defaults_to_today(self, tenant_a):
        a = Activity.objects.create(tenant=tenant_a, subject="Test")
        assert a.activity_date == timezone.localdate()

    def test_created_at_set_on_save(self, activity_a):
        assert activity_a.created_at is not None

    def test_updated_at_set_on_save(self, activity_a):
        assert activity_a.updated_at is not None

    def test_blank_optional_fields_allowed(self, tenant_a):
        a = Activity.objects.create(
            tenant=tenant_a, subject="Minimal",
            contact_name="", company_name="", owner_name="", notes=""
        )
        assert a.pk is not None

    def test_ordering_by_activity_date_desc(self, tenant_a):
        import datetime
        a1 = Activity.objects.create(
            tenant=tenant_a, subject="Old",
            activity_date=datetime.date(2024, 1, 1)
        )
        a2 = Activity.objects.create(
            tenant=tenant_a, subject="New",
            activity_date=datetime.date(2024, 6, 1)
        )
        qs = list(Activity.objects.filter(tenant=tenant_a))
        assert qs[0].pk == a2.pk  # newest first


# ============================================================ SalesTask
@pytest.mark.django_db
class TestSalesTaskModel:
    def test_str_returns_title(self, salestask_a):
        assert str(salestask_a) == "Follow up with Acme"

    def test_default_priority_is_medium(self, tenant_a):
        t = SalesTask.objects.create(tenant=tenant_a, title="Test Task")
        assert t.priority == SalesTask.PRIORITY_MEDIUM

    def test_default_status_is_open(self, tenant_a):
        t = SalesTask.objects.create(tenant=tenant_a, title="Test Task")
        assert t.status == SalesTask.STATUS_OPEN

    def test_priority_choices_contain_all_four(self):
        choices = dict(SalesTask.PRIORITY_CHOICES)
        assert SalesTask.PRIORITY_LOW in choices
        assert SalesTask.PRIORITY_MEDIUM in choices
        assert SalesTask.PRIORITY_HIGH in choices
        assert SalesTask.PRIORITY_URGENT in choices

    def test_status_choices_contain_all_five(self):
        choices = dict(SalesTask.STATUS_CHOICES)
        assert SalesTask.STATUS_OPEN in choices
        assert SalesTask.STATUS_IN_PROGRESS in choices
        assert SalesTask.STATUS_COMPLETED in choices
        assert SalesTask.STATUS_DEFERRED in choices
        assert SalesTask.STATUS_CANCELLED in choices

    def test_save_sets_completed_at_when_completed(self, tenant_a):
        t = SalesTask.objects.create(tenant=tenant_a, title="Done Task", status=SalesTask.STATUS_OPEN)
        assert t.completed_at is None
        t.status = SalesTask.STATUS_COMPLETED
        t.save()
        assert t.completed_at is not None

    def test_save_clears_completed_at_when_not_completed(self, tenant_a):
        t = SalesTask.objects.create(tenant=tenant_a, title="Done Task", status=SalesTask.STATUS_COMPLETED)
        assert t.completed_at is not None
        t.status = SalesTask.STATUS_OPEN
        t.save()
        assert t.completed_at is None

    def test_completed_at_not_overwritten_if_already_set(self, tenant_a):
        t = SalesTask.objects.create(tenant=tenant_a, title="Already done", status=SalesTask.STATUS_COMPLETED)
        first_completed_at = t.completed_at
        t.save()  # save again without changing status
        assert t.completed_at == first_completed_at

    def test_activity_fk_nullable(self, tenant_a):
        t = SalesTask.objects.create(tenant=tenant_a, title="No Activity Task")
        assert t.activity is None

    def test_activity_fk_set_null_on_delete(self, tenant_a, activity_a, salestask_a):
        assert salestask_a.activity == activity_a
        activity_a.delete()
        salestask_a.refresh_from_db()
        assert salestask_a.activity is None

    def test_due_date_nullable(self, tenant_a):
        t = SalesTask.objects.create(tenant=tenant_a, title="No Due Date")
        assert t.due_date is None

    def test_created_at_set_on_save(self, salestask_a):
        assert salestask_a.created_at is not None


# ============================================================ Meeting
@pytest.mark.django_db
class TestMeetingModel:
    def test_str_returns_title(self, meeting_a):
        assert str(meeting_a) == "Discovery Call with Acme"

    def test_default_meeting_type_is_discovery(self, tenant_a):
        m = Meeting.objects.create(tenant=tenant_a, title="Test Meeting")
        assert m.meeting_type == Meeting.TYPE_DISCOVERY

    def test_default_location_type_is_video(self, tenant_a):
        m = Meeting.objects.create(tenant=tenant_a, title="Test Meeting")
        assert m.location_type == Meeting.LOCATION_VIDEO

    def test_default_status_is_scheduled(self, tenant_a):
        m = Meeting.objects.create(tenant=tenant_a, title="Test Meeting")
        assert m.status == Meeting.STATUS_SCHEDULED

    def test_type_choices_contain_all_six(self):
        choices = dict(Meeting.TYPE_CHOICES)
        assert Meeting.TYPE_DISCOVERY in choices
        assert Meeting.TYPE_DEMO in choices
        assert Meeting.TYPE_PROPOSAL in choices
        assert Meeting.TYPE_NEGOTIATION in choices
        assert Meeting.TYPE_CHECK_IN in choices
        assert Meeting.TYPE_INTERNAL in choices

    def test_location_choices_contain_all_three(self):
        choices = dict(Meeting.LOCATION_CHOICES)
        assert Meeting.LOCATION_ONSITE in choices
        assert Meeting.LOCATION_VIDEO in choices
        assert Meeting.LOCATION_PHONE in choices

    def test_status_choices_contain_all_five(self):
        choices = dict(Meeting.STATUS_CHOICES)
        assert Meeting.STATUS_SCHEDULED in choices
        assert Meeting.STATUS_CONFIRMED in choices
        assert Meeting.STATUS_COMPLETED in choices
        assert Meeting.STATUS_CANCELLED in choices
        assert Meeting.STATUS_NO_SHOW in choices

    def test_scheduled_date_defaults_to_today(self, tenant_a):
        m = Meeting.objects.create(tenant=tenant_a, title="Test Meeting")
        assert m.scheduled_date == timezone.localdate()

    def test_start_time_end_time_nullable(self, tenant_a):
        m = Meeting.objects.create(tenant=tenant_a, title="Test Meeting")
        assert m.start_time is None
        assert m.end_time is None

    def test_optional_fields_blank_allowed(self, tenant_a):
        m = Meeting.objects.create(
            tenant=tenant_a, title="Minimal Meeting",
            attendees="", location="", organizer_name="", agenda=""
        )
        assert m.pk is not None

    def test_created_at_set_on_save(self, meeting_a):
        assert meeting_a.created_at is not None


# ============================================================ EmailLog
@pytest.mark.django_db
class TestEmailLogModel:
    def test_str_returns_subject(self, emaillog_a):
        assert str(emaillog_a) == "Acme Proposal Email"

    def test_default_direction_is_outbound(self, tenant_a):
        e = EmailLog.objects.create(tenant=tenant_a, subject="Test Email")
        assert e.direction == EmailLog.DIRECTION_OUTBOUND

    def test_default_status_is_draft(self, tenant_a):
        e = EmailLog.objects.create(tenant=tenant_a, subject="Test Email")
        assert e.status == EmailLog.STATUS_DRAFT

    def test_direction_choices_contain_both(self):
        choices = dict(EmailLog.DIRECTION_CHOICES)
        assert EmailLog.DIRECTION_OUTBOUND in choices
        assert EmailLog.DIRECTION_INBOUND in choices

    def test_status_choices_contain_all_seven(self):
        choices = dict(EmailLog.STATUS_CHOICES)
        assert EmailLog.STATUS_DRAFT in choices
        assert EmailLog.STATUS_SENT in choices
        assert EmailLog.STATUS_DELIVERED in choices
        assert EmailLog.STATUS_OPENED in choices
        assert EmailLog.STATUS_CLICKED in choices
        assert EmailLog.STATUS_REPLIED in choices
        assert EmailLog.STATUS_BOUNCED in choices

    def test_save_sets_sent_at_when_sent(self, tenant_a):
        e = EmailLog.objects.create(tenant=tenant_a, subject="Send Test", status=EmailLog.STATUS_DRAFT)
        assert e.sent_at is None
        e.status = EmailLog.STATUS_SENT
        e.save()
        assert e.sent_at is not None

    def test_save_sets_sent_at_when_delivered(self, tenant_a):
        e = EmailLog.objects.create(tenant=tenant_a, subject="Delivered Test", status=EmailLog.STATUS_DELIVERED)
        assert e.sent_at is not None

    def test_save_sets_opened_at_when_opened(self, tenant_a):
        e = EmailLog.objects.create(tenant=tenant_a, subject="Opened Test", status=EmailLog.STATUS_OPENED)
        assert e.opened_at is not None

    def test_save_sets_opened_at_when_clicked(self, tenant_a):
        e = EmailLog.objects.create(tenant=tenant_a, subject="Clicked Test", status=EmailLog.STATUS_CLICKED)
        assert e.opened_at is not None

    def test_save_sets_opened_at_when_replied(self, tenant_a):
        e = EmailLog.objects.create(tenant=tenant_a, subject="Replied Test", status=EmailLog.STATUS_REPLIED)
        assert e.opened_at is not None

    def test_save_does_not_set_opened_at_when_only_sent(self, tenant_a):
        e = EmailLog.objects.create(tenant=tenant_a, subject="Sent Only", status=EmailLog.STATUS_SENT)
        assert e.opened_at is None

    def test_save_does_not_overwrite_sent_at_if_already_set(self, tenant_a):
        e = EmailLog.objects.create(tenant=tenant_a, subject="Already Sent", status=EmailLog.STATUS_SENT)
        first_sent_at = e.sent_at
        e.save()
        assert e.sent_at == first_sent_at

    def test_draft_status_no_sent_at(self, tenant_a):
        e = EmailLog.objects.create(tenant=tenant_a, subject="Draft Only")
        assert e.sent_at is None
        assert e.opened_at is None

    def test_activity_fk_nullable(self, tenant_a):
        e = EmailLog.objects.create(tenant=tenant_a, subject="No Activity Email")
        assert e.activity is None

    def test_activity_fk_set_null_on_delete(self, emaillog_a, activity_a):
        assert emaillog_a.activity == activity_a
        activity_a.delete()
        emaillog_a.refresh_from_db()
        assert emaillog_a.activity is None

    def test_default_counts_are_zero(self, tenant_a):
        e = EmailLog.objects.create(tenant=tenant_a, subject="Count Test")
        assert e.open_count == 0
        assert e.click_count == 0

    def test_bounced_sets_sent_at(self, tenant_a):
        e = EmailLog.objects.create(tenant=tenant_a, subject="Bounced", status=EmailLog.STATUS_BOUNCED)
        assert e.sent_at is not None

    def test_created_at_set_on_save(self, emaillog_a):
        assert emaillog_a.created_at is not None


# ============================================================ SalesPlan
@pytest.mark.django_db
class TestSalesPlanModel:
    def test_str_returns_number_when_saved(self, salesplan_a):
        assert str(salesplan_a) == salesplan_a.number

    def test_str_falls_back_to_title_before_save(self, tenant_a):
        p = SalesPlan(tenant=tenant_a, title="Unsaved Plan")
        assert str(p) == "Unsaved Plan"

    def test_auto_number_generated_on_save(self, salesplan_a):
        assert salesplan_a.number.startswith("PLAN-")

    def test_auto_number_first_is_PLAN_00001(self, tenant_a):
        p = SalesPlan.objects.create(tenant=tenant_a, title="First Plan")
        assert p.number == "PLAN-00001"

    def test_auto_number_increments_per_tenant(self, tenant_a):
        p1 = SalesPlan.objects.create(tenant=tenant_a, title="Plan 1")
        p2 = SalesPlan.objects.create(tenant=tenant_a, title="Plan 2")
        assert p1.number == "PLAN-00001"
        assert p2.number == "PLAN-00002"

    def test_auto_number_isolated_per_tenant(self, tenant_a, tenant_b):
        pa = SalesPlan.objects.create(tenant=tenant_a, title="Plan A")
        pb = SalesPlan.objects.create(tenant=tenant_b, title="Plan B")
        assert pa.number == "PLAN-00001"
        assert pb.number == "PLAN-00001"

    def test_auto_number_format_five_digits(self, tenant_a):
        p = SalesPlan.objects.create(tenant=tenant_a, title="Format Test")
        parts = p.number.split("-")
        assert len(parts) == 2
        assert len(parts[1]) == 5
        assert parts[1].isdigit()

    def test_unique_together_tenant_number(self, tenant_a):
        import django.db.utils as db_utils
        SalesPlan.objects.create(tenant=tenant_a, title="First")  # gets PLAN-00001
        with pytest.raises(db_utils.IntegrityError):
            SalesPlan.objects.create(tenant=tenant_a, title="Collision", number="PLAN-00001")

    def test_default_period_type_is_weekly(self, tenant_a):
        p = SalesPlan.objects.create(tenant=tenant_a, title="Test Plan")
        assert p.period_type == SalesPlan.PERIOD_WEEKLY

    def test_default_status_is_draft(self, tenant_a):
        p = SalesPlan.objects.create(tenant=tenant_a, title="Test Plan")
        assert p.status == SalesPlan.STATUS_DRAFT

    def test_period_choices_contain_all_three(self):
        choices = dict(SalesPlan.PERIOD_CHOICES)
        assert SalesPlan.PERIOD_DAILY in choices
        assert SalesPlan.PERIOD_WEEKLY in choices
        assert SalesPlan.PERIOD_MONTHLY in choices

    def test_status_choices_contain_all_four(self):
        choices = dict(SalesPlan.STATUS_CHOICES)
        assert SalesPlan.STATUS_DRAFT in choices
        assert SalesPlan.STATUS_ACTIVE in choices
        assert SalesPlan.STATUS_COMPLETED in choices
        assert SalesPlan.STATUS_ARCHIVED in choices

    def test_default_targets_are_zero(self, tenant_a):
        p = SalesPlan.objects.create(tenant=tenant_a, title="Zero Targets")
        assert p.target_calls == 0
        assert p.target_meetings == 0
        assert p.revenue_goal == 0

    def test_start_date_defaults_to_today(self, tenant_a):
        p = SalesPlan.objects.create(tenant=tenant_a, title="Test Plan")
        assert p.start_date == timezone.localdate()

    def test_end_date_nullable(self, tenant_a):
        p = SalesPlan.objects.create(tenant=tenant_a, title="Test Plan")
        assert p.end_date is None

    def test_created_at_set_on_save(self, salesplan_a):
        assert salesplan_a.created_at is not None

    def test_ordering_by_start_date_desc(self, tenant_a):
        import datetime
        p1 = SalesPlan.objects.create(tenant=tenant_a, title="Old Plan", start_date=datetime.date(2024, 1, 1))
        p2 = SalesPlan.objects.create(tenant=tenant_a, title="New Plan", start_date=datetime.date(2024, 6, 1))
        qs = list(SalesPlan.objects.filter(tenant=tenant_a))
        assert qs[0].pk == p2.pk  # newest first
