"""Security tests: multi-tenant isolation and authorization enforcement for activities."""
import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from apps.activities.models import Activity, SalesTask, Meeting, EmailLog, SalesPlan


# ============================================================ anonymous redirects
@pytest.mark.django_db
class TestAnonymousRedirects:
    """Anonymous users must be redirected to login for all activities views."""

    def _anon(self):
        return Client()

    def test_activity_list_redirects_anonymous(self):
        resp = self._anon().get(reverse("activities:activity_list"))
        assert resp.status_code in (301, 302)

    def test_activity_create_redirects_anonymous(self):
        resp = self._anon().get(reverse("activities:activity_create"))
        assert resp.status_code in (301, 302)

    def test_salestask_list_redirects_anonymous(self):
        resp = self._anon().get(reverse("activities:salestask_list"))
        assert resp.status_code in (301, 302)

    def test_salestask_create_redirects_anonymous(self):
        resp = self._anon().get(reverse("activities:salestask_create"))
        assert resp.status_code in (301, 302)

    def test_meeting_list_redirects_anonymous(self):
        resp = self._anon().get(reverse("activities:meeting_list"))
        assert resp.status_code in (301, 302)

    def test_meeting_create_redirects_anonymous(self):
        resp = self._anon().get(reverse("activities:meeting_create"))
        assert resp.status_code in (301, 302)

    def test_emaillog_list_redirects_anonymous(self):
        resp = self._anon().get(reverse("activities:emaillog_list"))
        assert resp.status_code in (301, 302)

    def test_emaillog_create_redirects_anonymous(self):
        resp = self._anon().get(reverse("activities:emaillog_create"))
        assert resp.status_code in (301, 302)

    def test_salesplan_list_redirects_anonymous(self):
        resp = self._anon().get(reverse("activities:salesplan_list"))
        assert resp.status_code in (301, 302)

    def test_salesplan_create_redirects_anonymous(self):
        resp = self._anon().get(reverse("activities:salesplan_create"))
        assert resp.status_code in (301, 302)


# ============================================================ anonymous POST does not mutate
@pytest.mark.django_db
class TestAnonymousPostDoesNotMutate:
    """Anonymous POST to delete/create views must not mutate data."""

    def test_anonymous_cannot_delete_activity(self, activity_a):
        c = Client()
        resp = c.post(reverse("activities:activity_delete", args=[activity_a.pk]))
        assert resp.status_code in (301, 302)
        assert Activity.objects.filter(pk=activity_a.pk).exists()

    def test_anonymous_cannot_delete_salestask(self, salestask_a):
        c = Client()
        resp = c.post(reverse("activities:salestask_delete", args=[salestask_a.pk]))
        assert resp.status_code in (301, 302)
        assert SalesTask.objects.filter(pk=salestask_a.pk).exists()

    def test_anonymous_cannot_delete_meeting(self, meeting_a):
        c = Client()
        resp = c.post(reverse("activities:meeting_delete", args=[meeting_a.pk]))
        assert resp.status_code in (301, 302)
        assert Meeting.objects.filter(pk=meeting_a.pk).exists()

    def test_anonymous_cannot_delete_emaillog(self, emaillog_a):
        c = Client()
        resp = c.post(reverse("activities:emaillog_delete", args=[emaillog_a.pk]))
        assert resp.status_code in (301, 302)
        assert EmailLog.objects.filter(pk=emaillog_a.pk).exists()

    def test_anonymous_cannot_delete_salesplan(self, salesplan_a):
        c = Client()
        resp = c.post(reverse("activities:salesplan_delete", args=[salesplan_a.pk]))
        assert resp.status_code in (301, 302)
        assert SalesPlan.objects.filter(pk=salesplan_a.pk).exists()


# ============================================================ rep (non-admin) blocked on write views
@pytest.mark.django_db
class TestRepBlockedFromWriteViews:
    """Non-admin sales reps are blocked from create/edit/delete (tenant_admin_required decorator)."""

    def test_rep_cannot_access_activity_create(self, rep_client_a):
        resp = rep_client_a.get(reverse("activities:activity_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_access_salestask_create(self, rep_client_a):
        resp = rep_client_a.get(reverse("activities:salestask_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_access_meeting_create(self, rep_client_a):
        resp = rep_client_a.get(reverse("activities:meeting_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_access_emaillog_create(self, rep_client_a):
        resp = rep_client_a.get(reverse("activities:emaillog_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_access_salesplan_create(self, rep_client_a):
        resp = rep_client_a.get(reverse("activities:salesplan_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_edit_activity(self, rep_client_a, activity_a):
        resp = rep_client_a.get(reverse("activities:activity_edit", args=[activity_a.pk]))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_delete_activity(self, rep_client_a, activity_a):
        resp = rep_client_a.post(reverse("activities:activity_delete", args=[activity_a.pk]))
        assert resp.status_code in (301, 302)
        assert Activity.objects.filter(pk=activity_a.pk).exists()

    def test_rep_cannot_delete_salestask(self, rep_client_a, salestask_a):
        resp = rep_client_a.post(reverse("activities:salestask_delete", args=[salestask_a.pk]))
        assert resp.status_code in (301, 302)
        assert SalesTask.objects.filter(pk=salestask_a.pk).exists()

    def test_rep_cannot_delete_meeting(self, rep_client_a, meeting_a):
        resp = rep_client_a.post(reverse("activities:meeting_delete", args=[meeting_a.pk]))
        assert resp.status_code in (301, 302)
        assert Meeting.objects.filter(pk=meeting_a.pk).exists()

    def test_rep_cannot_delete_emaillog(self, rep_client_a, emaillog_a):
        resp = rep_client_a.post(reverse("activities:emaillog_delete", args=[emaillog_a.pk]))
        assert resp.status_code in (301, 302)
        assert EmailLog.objects.filter(pk=emaillog_a.pk).exists()

    def test_rep_cannot_delete_salesplan(self, rep_client_a, salesplan_a):
        resp = rep_client_a.post(reverse("activities:salesplan_delete", args=[salesplan_a.pk]))
        assert resp.status_code in (301, 302)
        assert SalesPlan.objects.filter(pk=salesplan_a.pk).exists()

    def test_rep_can_view_activity_list(self, rep_client_a):
        """Reps CAN view list pages (read-only)."""
        resp = rep_client_a.get(reverse("activities:activity_list"))
        assert resp.status_code == 200

    def test_rep_can_view_salestask_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("activities:salestask_list"))
        assert resp.status_code == 200

    def test_rep_can_view_meeting_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("activities:meeting_list"))
        assert resp.status_code == 200

    def test_rep_can_view_emaillog_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("activities:emaillog_list"))
        assert resp.status_code == 200

    def test_rep_can_view_salesplan_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("activities:salesplan_list"))
        assert resp.status_code == 200


# ============================================================ cross-tenant 404 (IDOR)
@pytest.mark.django_db
class TestCrossTenantIsolation404:
    """Tenant A must receive 404 (not 403/200) on ALL Tenant B resource URLs."""

    # Activity
    def test_activity_detail_cross_tenant_404(self, client_a, activity_b):
        resp = client_a.get(reverse("activities:activity_detail", args=[activity_b.pk]))
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"

    def test_activity_edit_cross_tenant_404(self, client_a, activity_b):
        resp = client_a.get(reverse("activities:activity_edit", args=[activity_b.pk]))
        assert resp.status_code == 404

    def test_activity_delete_cross_tenant_404(self, client_a, activity_b):
        resp = client_a.post(reverse("activities:activity_delete", args=[activity_b.pk]))
        assert resp.status_code == 404
        assert Activity.objects.filter(pk=activity_b.pk).exists()

    # SalesTask
    def test_salestask_detail_cross_tenant_404(self, client_a, salestask_b):
        resp = client_a.get(reverse("activities:salestask_detail", args=[salestask_b.pk]))
        assert resp.status_code == 404

    def test_salestask_edit_cross_tenant_404(self, client_a, salestask_b):
        resp = client_a.get(reverse("activities:salestask_edit", args=[salestask_b.pk]))
        assert resp.status_code == 404

    def test_salestask_delete_cross_tenant_404(self, client_a, salestask_b):
        resp = client_a.post(reverse("activities:salestask_delete", args=[salestask_b.pk]))
        assert resp.status_code == 404
        assert SalesTask.objects.filter(pk=salestask_b.pk).exists()

    # Meeting
    def test_meeting_detail_cross_tenant_404(self, client_a, meeting_b):
        resp = client_a.get(reverse("activities:meeting_detail", args=[meeting_b.pk]))
        assert resp.status_code == 404

    def test_meeting_edit_cross_tenant_404(self, client_a, meeting_b):
        resp = client_a.get(reverse("activities:meeting_edit", args=[meeting_b.pk]))
        assert resp.status_code == 404

    def test_meeting_delete_cross_tenant_404(self, client_a, meeting_b):
        resp = client_a.post(reverse("activities:meeting_delete", args=[meeting_b.pk]))
        assert resp.status_code == 404
        assert Meeting.objects.filter(pk=meeting_b.pk).exists()

    # EmailLog
    def test_emaillog_detail_cross_tenant_404(self, client_a, emaillog_b):
        resp = client_a.get(reverse("activities:emaillog_detail", args=[emaillog_b.pk]))
        assert resp.status_code == 404

    def test_emaillog_edit_cross_tenant_404(self, client_a, emaillog_b):
        resp = client_a.get(reverse("activities:emaillog_edit", args=[emaillog_b.pk]))
        assert resp.status_code == 404

    def test_emaillog_delete_cross_tenant_404(self, client_a, emaillog_b):
        resp = client_a.post(reverse("activities:emaillog_delete", args=[emaillog_b.pk]))
        assert resp.status_code == 404
        assert EmailLog.objects.filter(pk=emaillog_b.pk).exists()

    # SalesPlan
    def test_salesplan_detail_cross_tenant_404(self, client_a, salesplan_b):
        resp = client_a.get(reverse("activities:salesplan_detail", args=[salesplan_b.pk]))
        assert resp.status_code == 404

    def test_salesplan_edit_cross_tenant_404(self, client_a, salesplan_b):
        resp = client_a.get(reverse("activities:salesplan_edit", args=[salesplan_b.pk]))
        assert resp.status_code == 404

    def test_salesplan_delete_cross_tenant_404(self, client_a, salesplan_b):
        resp = client_a.post(reverse("activities:salesplan_delete", args=[salesplan_b.pk]))
        assert resp.status_code == 404
        assert SalesPlan.objects.filter(pk=salesplan_b.pk).exists()


# ============================================================ list isolation
@pytest.mark.django_db
class TestListIsolation:
    """List views for Tenant A should never include Tenant B rows."""

    def test_activity_list_excludes_tenant_b(self, client_a, activity_a, activity_b):
        resp = client_a.get(reverse("activities:activity_list"))
        pks = [a.pk for a in resp.context["activities"]]
        assert activity_a.pk in pks
        assert activity_b.pk not in pks

    def test_salestask_list_excludes_tenant_b(self, client_a, salestask_a, salestask_b):
        resp = client_a.get(reverse("activities:salestask_list"))
        pks = [t.pk for t in resp.context["tasks"]]
        assert salestask_a.pk in pks
        assert salestask_b.pk not in pks

    def test_meeting_list_excludes_tenant_b(self, client_a, meeting_a, meeting_b):
        resp = client_a.get(reverse("activities:meeting_list"))
        pks = [m.pk for m in resp.context["meetings"]]
        assert meeting_a.pk in pks
        assert meeting_b.pk not in pks

    def test_emaillog_list_excludes_tenant_b(self, client_a, emaillog_a, emaillog_b):
        resp = client_a.get(reverse("activities:emaillog_list"))
        pks = [e.pk for e in resp.context["emails"]]
        assert emaillog_a.pk in pks
        assert emaillog_b.pk not in pks

    def test_salesplan_list_excludes_tenant_b(self, client_a, salesplan_a, salesplan_b):
        resp = client_a.get(reverse("activities:salesplan_list"))
        pks = [p.pk for p in resp.context["plans"]]
        assert salesplan_a.pk in pks
        assert salesplan_b.pk not in pks


# ============================================================ CSRF enforcement
@pytest.mark.django_db
class TestCSRFEnforcement:
    """CSRF checks: anonymous clients with enforce_csrf_checks get 302/403."""

    def test_anonymous_activity_create_blocked(self):
        c = Client(enforce_csrf_checks=True)
        resp = c.post(reverse("activities:activity_create"), {
            "subject": "Hack Attempt",
            "activity_type": "call",
            "direction": "outbound",
            "outcome": "pending",
            "duration_minutes": 0,
            "activity_date": timezone.localdate().isoformat(),
        })
        assert resp.status_code in (301, 302, 403)

    def test_anonymous_salesplan_create_blocked(self):
        c = Client(enforce_csrf_checks=True)
        resp = c.post(reverse("activities:salesplan_create"), {
            "title": "Hack Plan",
            "period_type": "weekly",
            "status": "draft",
            "start_date": timezone.localdate().isoformat(),
            "target_calls": 0,
            "target_meetings": 0,
            "revenue_goal": "0.00",
        })
        assert resp.status_code in (301, 302, 403)
