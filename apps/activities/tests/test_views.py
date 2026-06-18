"""Tests for activities views: CRUD for Activity, SalesTask, Meeting, EmailLog, SalesPlan."""
import pytest
from django.urls import reverse
from django.test import Client
from django.utils import timezone

from apps.activities.models import Activity, SalesTask, Meeting, EmailLog, SalesPlan


# ============================================================ Activity CRUD
@pytest.mark.django_db
class TestActivityListView:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("activities:activity_list"))
        assert resp.status_code == 200

    def test_list_context_has_activities(self, client_a, activity_a):
        resp = client_a.get(reverse("activities:activity_list"))
        assert "activities" in resp.context
        pks = [a.pk for a in resp.context["activities"]]
        assert activity_a.pk in pks

    def test_list_context_has_type_choices(self, client_a):
        resp = client_a.get(reverse("activities:activity_list"))
        assert "type_choices" in resp.context

    def test_list_context_has_outcome_choices(self, client_a):
        resp = client_a.get(reverse("activities:activity_list"))
        assert "outcome_choices" in resp.context

    def test_list_context_has_total(self, client_a, activity_a):
        resp = client_a.get(reverse("activities:activity_list"))
        assert "total" in resp.context

    def test_list_search_filters_by_subject(self, client_a, activity_a, tenant_a):
        other = Activity.objects.create(
            tenant=tenant_a, subject="Unrelated Entry", activity_date=timezone.localdate()
        )
        resp = client_a.get(reverse("activities:activity_list"), {"q": "Call with Acme"})
        pks = [a.pk for a in resp.context["activities"]]
        assert activity_a.pk in pks
        assert other.pk not in pks

    def test_list_filter_by_activity_type(self, client_a, activity_a, tenant_a):
        email_act = Activity.objects.create(
            tenant=tenant_a, subject="Email Act", activity_type=Activity.TYPE_EMAIL,
            activity_date=timezone.localdate()
        )
        resp = client_a.get(reverse("activities:activity_list"), {"activity_type": Activity.TYPE_CALL})
        pks = [a.pk for a in resp.context["activities"]]
        assert activity_a.pk in pks
        assert email_act.pk not in pks

    def test_list_filter_by_outcome(self, client_a, activity_a, tenant_a):
        success_act = Activity.objects.create(
            tenant=tenant_a, subject="Success Act", outcome=Activity.OUTCOME_SUCCESSFUL,
            activity_date=timezone.localdate()
        )
        resp = client_a.get(reverse("activities:activity_list"), {"outcome": Activity.OUTCOME_PENDING})
        pks = [a.pk for a in resp.context["activities"]]
        assert activity_a.pk in pks
        assert success_act.pk not in pks

    def test_list_excludes_other_tenant(self, client_a, activity_a, activity_b):
        resp = client_a.get(reverse("activities:activity_list"))
        pks = [a.pk for a in resp.context["activities"]]
        assert activity_a.pk in pks
        assert activity_b.pk not in pks


@pytest.mark.django_db
class TestActivityDetailView:
    def test_detail_200(self, client_a, activity_a):
        resp = client_a.get(reverse("activities:activity_detail", args=[activity_a.pk]))
        assert resp.status_code == 200

    def test_detail_context_has_obj(self, client_a, activity_a):
        resp = client_a.get(reverse("activities:activity_detail", args=[activity_a.pk]))
        assert resp.context["obj"] == activity_a

    def test_detail_404_for_other_tenant(self, client_a, activity_b):
        resp = client_a.get(reverse("activities:activity_detail", args=[activity_b.pk]))
        assert resp.status_code == 404


@pytest.mark.django_db
class TestActivityCreateView:
    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("activities:activity_create"))
        assert resp.status_code == 200

    def test_create_post_creates_activity(self, client_a, tenant_a):
        before = Activity.objects.filter(tenant=tenant_a).count()
        resp = client_a.post(reverse("activities:activity_create"), {
            "subject": "New Call",
            "activity_type": "call",
            "direction": "outbound",
            "outcome": "pending",
            "contact_name": "",
            "company_name": "",
            "owner_name": "",
            "duration_minutes": 0,
            "activity_date": timezone.localdate().isoformat(),
            "notes": "",
        })
        assert Activity.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_request_tenant(self, client_a, tenant_a):
        client_a.post(reverse("activities:activity_create"), {
            "subject": "Tenant Check Call",
            "activity_type": "call",
            "direction": "outbound",
            "outcome": "pending",
            "duration_minutes": 0,
            "activity_date": timezone.localdate().isoformat(),
        })
        act = Activity.objects.filter(subject="Tenant Check Call").first()
        assert act is not None
        assert act.tenant == tenant_a

    def test_create_redirects_on_success(self, client_a):
        resp = client_a.post(reverse("activities:activity_create"), {
            "subject": "Redirect Test",
            "activity_type": "note",
            "direction": "internal",
            "outcome": "pending",
            "duration_minutes": 0,
            "activity_date": timezone.localdate().isoformat(),
        })
        assert resp.status_code in (301, 302)

    def test_create_invalid_form_does_not_create(self, client_a, tenant_a):
        before = Activity.objects.filter(tenant=tenant_a).count()
        resp = client_a.post(reverse("activities:activity_create"), {
            "subject": "",  # required
            "activity_type": "call",
            "direction": "outbound",
            "outcome": "pending",
            "duration_minutes": 0,
            "activity_date": timezone.localdate().isoformat(),
        })
        assert Activity.objects.filter(tenant=tenant_a).count() == before


@pytest.mark.django_db
class TestActivityEditView:
    def test_edit_get_200(self, client_a, activity_a):
        resp = client_a.get(reverse("activities:activity_edit", args=[activity_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_activity(self, client_a, activity_a):
        resp = client_a.post(reverse("activities:activity_edit", args=[activity_a.pk]), {
            "subject": "Updated Subject",
            "activity_type": "call",
            "direction": "outbound",
            "outcome": "successful",
            "contact_name": "",
            "company_name": "",
            "owner_name": "",
            "duration_minutes": 15,
            "activity_date": timezone.localdate().isoformat(),
            "notes": "",
        })
        activity_a.refresh_from_db()
        assert activity_a.subject == "Updated Subject"
        assert activity_a.outcome == Activity.OUTCOME_SUCCESSFUL

    def test_edit_404_for_other_tenant(self, client_a, activity_b):
        resp = client_a.get(reverse("activities:activity_edit", args=[activity_b.pk]))
        assert resp.status_code == 404


@pytest.mark.django_db
class TestActivityDeleteView:
    def test_delete_post_removes_activity(self, client_a, tenant_a):
        act = Activity.objects.create(
            tenant=tenant_a, subject="ToDelete", activity_date=timezone.localdate()
        )
        resp = client_a.post(reverse("activities:activity_delete", args=[act.pk]))
        assert not Activity.objects.filter(pk=act.pk).exists()

    def test_delete_redirects_to_list(self, client_a, tenant_a):
        act = Activity.objects.create(
            tenant=tenant_a, subject="ToDelete2", activity_date=timezone.localdate()
        )
        resp = client_a.post(reverse("activities:activity_delete", args=[act.pk]))
        assert resp.status_code in (301, 302)

    def test_delete_404_for_other_tenant(self, client_a, activity_b):
        resp = client_a.post(reverse("activities:activity_delete", args=[activity_b.pk]))
        assert resp.status_code == 404


# ============================================================ SalesTask CRUD
@pytest.mark.django_db
class TestSalesTaskListView:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("activities:salestask_list"))
        assert resp.status_code == 200

    def test_list_context_has_tasks(self, client_a, salestask_a):
        resp = client_a.get(reverse("activities:salestask_list"))
        assert "tasks" in resp.context
        pks = [t.pk for t in resp.context["tasks"]]
        assert salestask_a.pk in pks

    def test_list_context_has_status_choices(self, client_a):
        resp = client_a.get(reverse("activities:salestask_list"))
        assert "status_choices" in resp.context

    def test_list_context_has_priority_choices(self, client_a):
        resp = client_a.get(reverse("activities:salestask_list"))
        assert "priority_choices" in resp.context

    def test_list_filter_by_status(self, client_a, salestask_a, tenant_a):
        completed = SalesTask.objects.create(
            tenant=tenant_a, title="Done Task", status=SalesTask.STATUS_COMPLETED
        )
        resp = client_a.get(reverse("activities:salestask_list"), {"status": SalesTask.STATUS_OPEN})
        pks = [t.pk for t in resp.context["tasks"]]
        assert salestask_a.pk in pks
        assert completed.pk not in pks

    def test_list_excludes_other_tenant(self, client_a, salestask_a, salestask_b):
        resp = client_a.get(reverse("activities:salestask_list"))
        pks = [t.pk for t in resp.context["tasks"]]
        assert salestask_a.pk in pks
        assert salestask_b.pk not in pks


@pytest.mark.django_db
class TestSalesTaskDetailView:
    def test_detail_200(self, client_a, salestask_a):
        resp = client_a.get(reverse("activities:salestask_detail", args=[salestask_a.pk]))
        assert resp.status_code == 200

    def test_detail_context_has_obj(self, client_a, salestask_a):
        resp = client_a.get(reverse("activities:salestask_detail", args=[salestask_a.pk]))
        assert resp.context["obj"] == salestask_a

    def test_detail_404_for_other_tenant(self, client_a, salestask_b):
        resp = client_a.get(reverse("activities:salestask_detail", args=[salestask_b.pk]))
        assert resp.status_code == 404


@pytest.mark.django_db
class TestSalesTaskCreateView:
    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("activities:salestask_create"))
        assert resp.status_code == 200

    def test_create_post_creates_task(self, client_a, tenant_a):
        before = SalesTask.objects.filter(tenant=tenant_a).count()
        resp = client_a.post(reverse("activities:salestask_create"), {
            "activity": "",
            "title": "New Follow-Up Task",
            "description": "",
            "priority": "medium",
            "status": "open",
            "assigned_to": "",
            "related_to": "",
            "due_date": "",
            "reminder_date": "",
        })
        assert SalesTask.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_request_tenant(self, client_a, tenant_a):
        client_a.post(reverse("activities:salestask_create"), {
            "activity": "",
            "title": "Tenant Check Task",
            "description": "",
            "priority": "low",
            "status": "open",
            "assigned_to": "",
            "related_to": "",
            "due_date": "",
            "reminder_date": "",
        })
        task = SalesTask.objects.filter(title="Tenant Check Task").first()
        assert task is not None
        assert task.tenant == tenant_a


@pytest.mark.django_db
class TestSalesTaskEditView:
    def test_edit_get_200(self, client_a, salestask_a):
        resp = client_a.get(reverse("activities:salestask_edit", args=[salestask_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_task(self, client_a, salestask_a):
        resp = client_a.post(reverse("activities:salestask_edit", args=[salestask_a.pk]), {
            "activity": "",
            "title": "Updated Task Title",
            "description": "",
            "priority": "urgent",
            "status": "in_progress",
            "assigned_to": "",
            "related_to": "",
            "due_date": "",
            "reminder_date": "",
        })
        salestask_a.refresh_from_db()
        assert salestask_a.title == "Updated Task Title"
        assert salestask_a.priority == SalesTask.PRIORITY_URGENT

    def test_edit_404_for_other_tenant(self, client_a, salestask_b):
        resp = client_a.get(reverse("activities:salestask_edit", args=[salestask_b.pk]))
        assert resp.status_code == 404


@pytest.mark.django_db
class TestSalesTaskDeleteView:
    def test_delete_post_removes_task(self, client_a, tenant_a):
        task = SalesTask.objects.create(tenant=tenant_a, title="ToDelete Task")
        resp = client_a.post(reverse("activities:salestask_delete", args=[task.pk]))
        assert not SalesTask.objects.filter(pk=task.pk).exists()

    def test_delete_redirects_to_list(self, client_a, tenant_a):
        task = SalesTask.objects.create(tenant=tenant_a, title="ToDelete Task 2")
        resp = client_a.post(reverse("activities:salestask_delete", args=[task.pk]))
        assert resp.status_code in (301, 302)

    def test_delete_404_for_other_tenant(self, client_a, salestask_b):
        resp = client_a.post(reverse("activities:salestask_delete", args=[salestask_b.pk]))
        assert resp.status_code == 404


# ============================================================ Meeting CRUD
@pytest.mark.django_db
class TestMeetingListView:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("activities:meeting_list"))
        assert resp.status_code == 200

    def test_list_context_has_meetings(self, client_a, meeting_a):
        resp = client_a.get(reverse("activities:meeting_list"))
        assert "meetings" in resp.context
        pks = [m.pk for m in resp.context["meetings"]]
        assert meeting_a.pk in pks

    def test_list_context_has_type_choices(self, client_a):
        resp = client_a.get(reverse("activities:meeting_list"))
        assert "type_choices" in resp.context

    def test_list_context_has_status_choices(self, client_a):
        resp = client_a.get(reverse("activities:meeting_list"))
        assert "status_choices" in resp.context

    def test_list_filter_by_status(self, client_a, meeting_a, tenant_a):
        confirmed = Meeting.objects.create(
            tenant=tenant_a, title="Confirmed Meeting",
            status=Meeting.STATUS_CONFIRMED, scheduled_date=timezone.localdate()
        )
        resp = client_a.get(reverse("activities:meeting_list"), {"status": Meeting.STATUS_SCHEDULED})
        pks = [m.pk for m in resp.context["meetings"]]
        assert meeting_a.pk in pks
        assert confirmed.pk not in pks

    def test_list_excludes_other_tenant(self, client_a, meeting_a, meeting_b):
        resp = client_a.get(reverse("activities:meeting_list"))
        pks = [m.pk for m in resp.context["meetings"]]
        assert meeting_a.pk in pks
        assert meeting_b.pk not in pks


@pytest.mark.django_db
class TestMeetingDetailView:
    def test_detail_200(self, client_a, meeting_a):
        resp = client_a.get(reverse("activities:meeting_detail", args=[meeting_a.pk]))
        assert resp.status_code == 200

    def test_detail_context_has_obj(self, client_a, meeting_a):
        resp = client_a.get(reverse("activities:meeting_detail", args=[meeting_a.pk]))
        assert resp.context["obj"] == meeting_a

    def test_detail_404_for_other_tenant(self, client_a, meeting_b):
        resp = client_a.get(reverse("activities:meeting_detail", args=[meeting_b.pk]))
        assert resp.status_code == 404


@pytest.mark.django_db
class TestMeetingCreateView:
    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("activities:meeting_create"))
        assert resp.status_code == 200

    def test_create_post_creates_meeting(self, client_a, tenant_a):
        before = Meeting.objects.filter(tenant=tenant_a).count()
        resp = client_a.post(reverse("activities:meeting_create"), {
            "title": "New Discovery Meeting",
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
        assert Meeting.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_request_tenant(self, client_a, tenant_a):
        client_a.post(reverse("activities:meeting_create"), {
            "title": "Tenant Check Meeting",
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
        m = Meeting.objects.filter(title="Tenant Check Meeting").first()
        assert m is not None
        assert m.tenant == tenant_a


@pytest.mark.django_db
class TestMeetingEditView:
    def test_edit_get_200(self, client_a, meeting_a):
        resp = client_a.get(reverse("activities:meeting_edit", args=[meeting_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_meeting(self, client_a, meeting_a):
        resp = client_a.post(reverse("activities:meeting_edit", args=[meeting_a.pk]), {
            "title": "Updated Meeting Title",
            "meeting_type": "proposal",
            "location_type": "phone",
            "status": "confirmed",
            "attendees": "",
            "location": "",
            "organizer_name": "",
            "scheduled_date": timezone.localdate().isoformat(),
            "start_time": "",
            "end_time": "",
            "agenda": "",
        })
        meeting_a.refresh_from_db()
        assert meeting_a.title == "Updated Meeting Title"
        assert meeting_a.status == Meeting.STATUS_CONFIRMED

    def test_edit_404_for_other_tenant(self, client_a, meeting_b):
        resp = client_a.get(reverse("activities:meeting_edit", args=[meeting_b.pk]))
        assert resp.status_code == 404


@pytest.mark.django_db
class TestMeetingDeleteView:
    def test_delete_post_removes_meeting(self, client_a, tenant_a):
        m = Meeting.objects.create(
            tenant=tenant_a, title="ToDelete Meeting", scheduled_date=timezone.localdate()
        )
        resp = client_a.post(reverse("activities:meeting_delete", args=[m.pk]))
        assert not Meeting.objects.filter(pk=m.pk).exists()

    def test_delete_redirects_to_list(self, client_a, tenant_a):
        m = Meeting.objects.create(
            tenant=tenant_a, title="ToDelete Meeting 2", scheduled_date=timezone.localdate()
        )
        resp = client_a.post(reverse("activities:meeting_delete", args=[m.pk]))
        assert resp.status_code in (301, 302)

    def test_delete_404_for_other_tenant(self, client_a, meeting_b):
        resp = client_a.post(reverse("activities:meeting_delete", args=[meeting_b.pk]))
        assert resp.status_code == 404


# ============================================================ EmailLog CRUD
@pytest.mark.django_db
class TestEmailLogListView:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("activities:emaillog_list"))
        assert resp.status_code == 200

    def test_list_context_has_emails(self, client_a, emaillog_a):
        resp = client_a.get(reverse("activities:emaillog_list"))
        assert "emails" in resp.context
        pks = [e.pk for e in resp.context["emails"]]
        assert emaillog_a.pk in pks

    def test_list_context_has_status_choices(self, client_a):
        resp = client_a.get(reverse("activities:emaillog_list"))
        assert "status_choices" in resp.context

    def test_list_context_has_direction_choices(self, client_a):
        resp = client_a.get(reverse("activities:emaillog_list"))
        assert "direction_choices" in resp.context

    def test_list_filter_by_status(self, client_a, emaillog_a, tenant_a):
        sent_email = EmailLog.objects.create(
            tenant=tenant_a, subject="Sent Email", status=EmailLog.STATUS_SENT
        )
        resp = client_a.get(reverse("activities:emaillog_list"), {"status": EmailLog.STATUS_DRAFT})
        pks = [e.pk for e in resp.context["emails"]]
        assert emaillog_a.pk in pks
        assert sent_email.pk not in pks

    def test_list_excludes_other_tenant(self, client_a, emaillog_a, emaillog_b):
        resp = client_a.get(reverse("activities:emaillog_list"))
        pks = [e.pk for e in resp.context["emails"]]
        assert emaillog_a.pk in pks
        assert emaillog_b.pk not in pks


@pytest.mark.django_db
class TestEmailLogDetailView:
    def test_detail_200(self, client_a, emaillog_a):
        resp = client_a.get(reverse("activities:emaillog_detail", args=[emaillog_a.pk]))
        assert resp.status_code == 200

    def test_detail_context_has_obj(self, client_a, emaillog_a):
        resp = client_a.get(reverse("activities:emaillog_detail", args=[emaillog_a.pk]))
        assert resp.context["obj"] == emaillog_a

    def test_detail_404_for_other_tenant(self, client_a, emaillog_b):
        resp = client_a.get(reverse("activities:emaillog_detail", args=[emaillog_b.pk]))
        assert resp.status_code == 404


@pytest.mark.django_db
class TestEmailLogCreateView:
    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("activities:emaillog_create"))
        assert resp.status_code == 200

    def test_create_post_creates_emaillog(self, client_a, tenant_a):
        before = EmailLog.objects.filter(tenant=tenant_a).count()
        resp = client_a.post(reverse("activities:emaillog_create"), {
            "activity": "",
            "subject": "New Proposal Email",
            "direction": "outbound",
            "status": "draft",
            "from_email": "",
            "to_email": "",
            "open_count": 0,
            "click_count": 0,
            "body": "",
        })
        assert EmailLog.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_request_tenant(self, client_a, tenant_a):
        client_a.post(reverse("activities:emaillog_create"), {
            "activity": "",
            "subject": "Tenant Check Email",
            "direction": "outbound",
            "status": "draft",
            "from_email": "",
            "to_email": "",
            "open_count": 0,
            "click_count": 0,
            "body": "",
        })
        e = EmailLog.objects.filter(subject="Tenant Check Email").first()
        assert e is not None
        assert e.tenant == tenant_a


@pytest.mark.django_db
class TestEmailLogEditView:
    def test_edit_get_200(self, client_a, emaillog_a):
        resp = client_a.get(reverse("activities:emaillog_edit", args=[emaillog_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_emaillog(self, client_a, emaillog_a):
        resp = client_a.post(reverse("activities:emaillog_edit", args=[emaillog_a.pk]), {
            "activity": "",
            "subject": "Updated Email Subject",
            "direction": "inbound",
            "status": "sent",
            "from_email": "",
            "to_email": "",
            "open_count": 0,
            "click_count": 0,
            "body": "",
        })
        emaillog_a.refresh_from_db()
        assert emaillog_a.subject == "Updated Email Subject"
        assert emaillog_a.direction == EmailLog.DIRECTION_INBOUND

    def test_edit_404_for_other_tenant(self, client_a, emaillog_b):
        resp = client_a.get(reverse("activities:emaillog_edit", args=[emaillog_b.pk]))
        assert resp.status_code == 404


@pytest.mark.django_db
class TestEmailLogDeleteView:
    def test_delete_post_removes_emaillog(self, client_a, tenant_a):
        e = EmailLog.objects.create(tenant=tenant_a, subject="ToDelete Email")
        resp = client_a.post(reverse("activities:emaillog_delete", args=[e.pk]))
        assert not EmailLog.objects.filter(pk=e.pk).exists()

    def test_delete_redirects_to_list(self, client_a, tenant_a):
        e = EmailLog.objects.create(tenant=tenant_a, subject="ToDelete Email 2")
        resp = client_a.post(reverse("activities:emaillog_delete", args=[e.pk]))
        assert resp.status_code in (301, 302)

    def test_delete_404_for_other_tenant(self, client_a, emaillog_b):
        resp = client_a.post(reverse("activities:emaillog_delete", args=[emaillog_b.pk]))
        assert resp.status_code == 404


# ============================================================ SalesPlan CRUD
@pytest.mark.django_db
class TestSalesPlanListView:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("activities:salesplan_list"))
        assert resp.status_code == 200

    def test_list_context_has_plans(self, client_a, salesplan_a):
        resp = client_a.get(reverse("activities:salesplan_list"))
        assert "plans" in resp.context
        pks = [p.pk for p in resp.context["plans"]]
        assert salesplan_a.pk in pks

    def test_list_context_has_period_choices(self, client_a):
        resp = client_a.get(reverse("activities:salesplan_list"))
        assert "period_choices" in resp.context

    def test_list_context_has_status_choices(self, client_a):
        resp = client_a.get(reverse("activities:salesplan_list"))
        assert "status_choices" in resp.context

    def test_list_filter_by_status(self, client_a, salesplan_a, tenant_a):
        active_plan = SalesPlan.objects.create(
            tenant=tenant_a, title="Active Plan",
            status=SalesPlan.STATUS_ACTIVE, start_date=timezone.localdate()
        )
        resp = client_a.get(reverse("activities:salesplan_list"), {"status": SalesPlan.STATUS_DRAFT})
        pks = [p.pk for p in resp.context["plans"]]
        assert salesplan_a.pk in pks
        assert active_plan.pk not in pks

    def test_list_filter_by_period_type(self, client_a, salesplan_a, tenant_a):
        monthly = SalesPlan.objects.create(
            tenant=tenant_a, title="Monthly Plan",
            period_type=SalesPlan.PERIOD_MONTHLY, start_date=timezone.localdate()
        )
        resp = client_a.get(reverse("activities:salesplan_list"), {"period_type": SalesPlan.PERIOD_WEEKLY})
        pks = [p.pk for p in resp.context["plans"]]
        assert salesplan_a.pk in pks
        assert monthly.pk not in pks

    def test_list_excludes_other_tenant(self, client_a, salesplan_a, salesplan_b):
        resp = client_a.get(reverse("activities:salesplan_list"))
        pks = [p.pk for p in resp.context["plans"]]
        assert salesplan_a.pk in pks
        assert salesplan_b.pk not in pks


@pytest.mark.django_db
class TestSalesPlanDetailView:
    def test_detail_200(self, client_a, salesplan_a):
        resp = client_a.get(reverse("activities:salesplan_detail", args=[salesplan_a.pk]))
        assert resp.status_code == 200

    def test_detail_context_has_obj(self, client_a, salesplan_a):
        resp = client_a.get(reverse("activities:salesplan_detail", args=[salesplan_a.pk]))
        assert resp.context["obj"] == salesplan_a

    def test_detail_404_for_other_tenant(self, client_a, salesplan_b):
        resp = client_a.get(reverse("activities:salesplan_detail", args=[salesplan_b.pk]))
        assert resp.status_code == 404


@pytest.mark.django_db
class TestSalesPlanCreateView:
    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("activities:salesplan_create"))
        assert resp.status_code == 200

    def test_create_post_creates_plan(self, client_a, tenant_a):
        before = SalesPlan.objects.filter(tenant=tenant_a).count()
        resp = client_a.post(reverse("activities:salesplan_create"), {
            "title": "New Weekly Plan",
            "owner_name": "",
            "period_type": "weekly",
            "status": "draft",
            "start_date": timezone.localdate().isoformat(),
            "end_date": "",
            "target_calls": 10,
            "target_meetings": 3,
            "revenue_goal": "5000.00",
            "objectives": "",
        })
        assert SalesPlan.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_request_tenant(self, client_a, tenant_a):
        client_a.post(reverse("activities:salesplan_create"), {
            "title": "Tenant Check Plan",
            "owner_name": "",
            "period_type": "daily",
            "status": "draft",
            "start_date": timezone.localdate().isoformat(),
            "end_date": "",
            "target_calls": 5,
            "target_meetings": 1,
            "revenue_goal": "1000.00",
            "objectives": "",
        })
        p = SalesPlan.objects.filter(title="Tenant Check Plan").first()
        assert p is not None
        assert p.tenant == tenant_a

    def test_create_auto_numbers_plan(self, client_a, tenant_a):
        SalesPlan.objects.filter(tenant=tenant_a).delete()
        client_a.post(reverse("activities:salesplan_create"), {
            "title": "Auto Number Plan",
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
        p = SalesPlan.objects.filter(tenant=tenant_a, title="Auto Number Plan").first()
        assert p is not None
        assert p.number.startswith("PLAN-")


@pytest.mark.django_db
class TestSalesPlanEditView:
    def test_edit_get_200(self, client_a, salesplan_a):
        resp = client_a.get(reverse("activities:salesplan_edit", args=[salesplan_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_plan(self, client_a, salesplan_a):
        resp = client_a.post(reverse("activities:salesplan_edit", args=[salesplan_a.pk]), {
            "title": "Updated Plan Title",
            "owner_name": "",
            "period_type": "monthly",
            "status": "active",
            "start_date": timezone.localdate().isoformat(),
            "end_date": "",
            "target_calls": 50,
            "target_meetings": 10,
            "revenue_goal": "25000.00",
            "objectives": "",
        })
        salesplan_a.refresh_from_db()
        assert salesplan_a.title == "Updated Plan Title"
        assert salesplan_a.status == SalesPlan.STATUS_ACTIVE

    def test_edit_404_for_other_tenant(self, client_a, salesplan_b):
        resp = client_a.get(reverse("activities:salesplan_edit", args=[salesplan_b.pk]))
        assert resp.status_code == 404


@pytest.mark.django_db
class TestSalesPlanDeleteView:
    def test_delete_post_removes_plan(self, client_a, tenant_a):
        p = SalesPlan.objects.create(
            tenant=tenant_a, title="ToDelete Plan", start_date=timezone.localdate()
        )
        resp = client_a.post(reverse("activities:salesplan_delete", args=[p.pk]))
        assert not SalesPlan.objects.filter(pk=p.pk).exists()

    def test_delete_redirects_to_list(self, client_a, tenant_a):
        p = SalesPlan.objects.create(
            tenant=tenant_a, title="ToDelete Plan 2", start_date=timezone.localdate()
        )
        resp = client_a.post(reverse("activities:salesplan_delete", args=[p.pk]))
        assert resp.status_code in (301, 302)

    def test_delete_404_for_other_tenant(self, client_a, salesplan_b):
        resp = client_a.post(reverse("activities:salesplan_delete", args=[salesplan_b.pk]))
        assert resp.status_code == 404
