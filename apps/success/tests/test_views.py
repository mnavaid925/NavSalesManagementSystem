"""Tests for success views: CRUD for all 5 success models."""
import pytest
from django.urls import reverse
from django.utils import timezone

from apps.success.models import (
    HealthScore, Renewal, OnboardingPlan, Advocacy, QBR,
)


# ============================================================ HealthScore CRUD
@pytest.mark.django_db
class TestHealthScoreCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("success:healthscore_list"))
        assert resp.status_code == 200

    def test_list_context_has_healthscores(self, client_a, healthscore_a):
        resp = client_a.get(reverse("success:healthscore_list"))
        assert "healthscores" in resp.context

    def test_list_seeded_object_appears(self, client_a, healthscore_a):
        resp = client_a.get(reverse("success:healthscore_list"))
        pks = [h.pk for h in resp.context["healthscores"]]
        assert healthscore_a.pk in pks

    def test_list_has_risk_level_choices(self, client_a):
        resp = client_a.get(reverse("success:healthscore_list"))
        assert "risk_level_choices" in resp.context

    def test_list_has_trend_choices(self, client_a):
        resp = client_a.get(reverse("success:healthscore_list"))
        assert "trend_choices" in resp.context

    def test_list_search_filters_by_account_name(self, client_a, healthscore_a):
        resp = client_a.get(reverse("success:healthscore_list") + "?q=Acme+Corp")
        pks = [h.pk for h in resp.context["healthscores"]]
        assert healthscore_a.pk in pks

    def test_list_search_excludes_non_matches(self, client_a, healthscore_a):
        resp = client_a.get(reverse("success:healthscore_list") + "?q=ZZZNOMATCH")
        pks = [h.pk for h in resp.context["healthscores"]]
        assert healthscore_a.pk not in pks

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("success:healthscore_create"))
        assert resp.status_code == 200

    def test_create_post_creates_healthscore(self, client_a, tenant_a):
        before = HealthScore.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("success:healthscore_create"), {
            "account_name": "New Corp",
            "owner": "New Owner",
            "score": "60",
            "risk_level": "low",
            "trend": "stable",
            "arr": "80000.00",
            "last_reviewed": timezone.localdate().isoformat(),
            "notes": "",
        })
        assert HealthScore.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a):
        client_a.post(reverse("success:healthscore_create"), {
            "account_name": "Tenant Check Corp",
            "owner": "",
            "score": "50",
            "risk_level": "medium",
            "trend": "stable",
            "arr": "0",
            "last_reviewed": timezone.localdate().isoformat(),
            "notes": "hs-tenant-check",
        })
        hs = HealthScore.objects.filter(notes="hs-tenant-check").first()
        assert hs is not None
        assert hs.tenant == tenant_a

    def test_detail_200(self, client_a, healthscore_a):
        resp = client_a.get(reverse("success:healthscore_detail", args=[healthscore_a.pk]))
        assert resp.status_code == 200

    def test_detail_context_has_obj(self, client_a, healthscore_a):
        resp = client_a.get(reverse("success:healthscore_detail", args=[healthscore_a.pk]))
        assert resp.context["obj"] == healthscore_a

    def test_edit_get_200(self, client_a, healthscore_a):
        resp = client_a.get(reverse("success:healthscore_edit", args=[healthscore_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_healthscore(self, client_a, healthscore_a):
        client_a.post(reverse("success:healthscore_edit", args=[healthscore_a.pk]), {
            "account_name": "Acme Corp Updated",
            "owner": "Alice Smith",
            "score": "90",
            "risk_level": "low",
            "trend": "improving",
            "arr": "120000.00",
            "last_reviewed": timezone.localdate().isoformat(),
            "notes": "",
        })
        healthscore_a.refresh_from_db()
        assert healthscore_a.account_name == "Acme Corp Updated"
        assert healthscore_a.score == 90

    def test_delete_post_removes_healthscore(self, client_a, tenant_a):
        hs = HealthScore.objects.create(
            tenant=tenant_a,
            account_name="To Delete Corp",
            last_reviewed=timezone.localdate()
        )
        client_a.post(reverse("success:healthscore_delete", args=[hs.pk]))
        assert not HealthScore.objects.filter(pk=hs.pk).exists()

    def test_delete_redirects_to_list(self, client_a, tenant_a):
        hs = HealthScore.objects.create(
            tenant=tenant_a,
            account_name="Redirect Corp",
            last_reviewed=timezone.localdate()
        )
        resp = client_a.post(reverse("success:healthscore_delete", args=[hs.pk]))
        assert resp.status_code in (301, 302)

    def test_delete_get_does_not_delete(self, client_a, tenant_a):
        hs = HealthScore.objects.create(
            tenant=tenant_a,
            account_name="Get Delete Corp",
            last_reviewed=timezone.localdate()
        )
        client_a.get(reverse("success:healthscore_delete", args=[hs.pk]))
        assert HealthScore.objects.filter(pk=hs.pk).exists()


# ============================================================ Renewal CRUD
@pytest.mark.django_db
class TestRenewalCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("success:renewal_list"))
        assert resp.status_code == 200

    def test_list_context_has_renewals(self, client_a, renewal_a):
        resp = client_a.get(reverse("success:renewal_list"))
        assert "renewals" in resp.context

    def test_list_seeded_object_appears(self, client_a, renewal_a):
        resp = client_a.get(reverse("success:renewal_list"))
        pks = [r.pk for r in resp.context["renewals"]]
        assert renewal_a.pk in pks

    def test_list_has_type_choices(self, client_a):
        resp = client_a.get(reverse("success:renewal_list"))
        assert "type_choices" in resp.context

    def test_list_has_status_choices(self, client_a):
        resp = client_a.get(reverse("success:renewal_list"))
        assert "status_choices" in resp.context

    def test_list_search_filters_by_account_name(self, client_a, renewal_a):
        resp = client_a.get(reverse("success:renewal_list") + "?q=Acme+Corp")
        pks = [r.pk for r in resp.context["renewals"]]
        assert renewal_a.pk in pks

    def test_list_search_excludes_non_matches(self, client_a, renewal_a):
        resp = client_a.get(reverse("success:renewal_list") + "?q=ZZZNOMATCH")
        pks = [r.pk for r in resp.context["renewals"]]
        assert renewal_a.pk not in pks

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("success:renewal_create"))
        assert resp.status_code == 200

    def test_create_post_creates_renewal(self, client_a, tenant_a):
        before = Renewal.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("success:renewal_create"), {
            "account_name": "New Renewal Corp",
            "owner": "Owner",
            "renewal_type": "renewal",
            "status": "open",
            "arr_current": "50000.00",
            "arr_proposed": "55000.00",
            "probability": "60",
            "renewal_date": timezone.localdate().isoformat(),
            "notes": "",
        })
        assert Renewal.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a):
        client_a.post(reverse("success:renewal_create"), {
            "account_name": "Tenant Check Renewal Corp",
            "owner": "",
            "renewal_type": "upsell",
            "status": "open",
            "arr_current": "0",
            "arr_proposed": "0",
            "probability": "50",
            "renewal_date": timezone.localdate().isoformat(),
            "notes": "ren-tenant-check",
        })
        r = Renewal.objects.filter(notes="ren-tenant-check").first()
        assert r is not None
        assert r.tenant == tenant_a

    def test_create_auto_numbers_renewal(self, client_a, tenant_a):
        client_a.post(reverse("success:renewal_create"), {
            "account_name": "Numbered Renewal Corp",
            "owner": "",
            "renewal_type": "renewal",
            "status": "open",
            "arr_current": "0",
            "arr_proposed": "0",
            "probability": "50",
            "renewal_date": timezone.localdate().isoformat(),
            "notes": "ren-auto-number-check",
        })
        r = Renewal.objects.filter(notes="ren-auto-number-check").first()
        assert r is not None
        assert r.number.startswith("REN-")

    def test_detail_200(self, client_a, renewal_a):
        resp = client_a.get(reverse("success:renewal_detail", args=[renewal_a.pk]))
        assert resp.status_code == 200

    def test_detail_context_has_obj(self, client_a, renewal_a):
        resp = client_a.get(reverse("success:renewal_detail", args=[renewal_a.pk]))
        assert resp.context["obj"] == renewal_a

    def test_edit_get_200(self, client_a, renewal_a):
        resp = client_a.get(reverse("success:renewal_edit", args=[renewal_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_renewal(self, client_a, renewal_a):
        client_a.post(reverse("success:renewal_edit", args=[renewal_a.pk]), {
            "account_name": "Acme Corp Updated",
            "owner": "Alice Smith",
            "renewal_type": "upsell",
            "status": "committed",
            "arr_current": "100000.00",
            "arr_proposed": "120000.00",
            "probability": "85",
            "renewal_date": renewal_a.renewal_date.isoformat(),
            "notes": "",
        })
        renewal_a.refresh_from_db()
        assert renewal_a.account_name == "Acme Corp Updated"
        assert renewal_a.renewal_type == Renewal.TYPE_UPSELL

    def test_delete_post_removes_renewal(self, client_a, tenant_a):
        Renewal.objects.filter(tenant=tenant_a).delete()
        r = Renewal.objects.create(
            tenant=tenant_a, account_name="To Delete Renewal",
            renewal_date=timezone.localdate()
        )
        client_a.post(reverse("success:renewal_delete", args=[r.pk]))
        assert not Renewal.objects.filter(pk=r.pk).exists()

    def test_delete_redirects_to_list(self, client_a, tenant_a):
        Renewal.objects.filter(tenant=tenant_a).delete()
        r = Renewal.objects.create(
            tenant=tenant_a, account_name="Redirect Renewal",
            renewal_date=timezone.localdate()
        )
        resp = client_a.post(reverse("success:renewal_delete", args=[r.pk]))
        assert resp.status_code in (301, 302)

    def test_delete_get_does_not_delete(self, client_a, tenant_a):
        Renewal.objects.filter(tenant=tenant_a).delete()
        r = Renewal.objects.create(
            tenant=tenant_a, account_name="Get Delete Renewal",
            renewal_date=timezone.localdate()
        )
        client_a.get(reverse("success:renewal_delete", args=[r.pk]))
        assert Renewal.objects.filter(pk=r.pk).exists()


# ============================================================ OnboardingPlan CRUD
@pytest.mark.django_db
class TestOnboardingPlanCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("success:onboardingplan_list"))
        assert resp.status_code == 200

    def test_list_context_has_onboardingplans(self, client_a, onboardingplan_a):
        resp = client_a.get(reverse("success:onboardingplan_list"))
        assert "onboardingplans" in resp.context

    def test_list_seeded_object_appears(self, client_a, onboardingplan_a):
        resp = client_a.get(reverse("success:onboardingplan_list"))
        pks = [op.pk for op in resp.context["onboardingplans"]]
        assert onboardingplan_a.pk in pks

    def test_list_has_status_choices(self, client_a):
        resp = client_a.get(reverse("success:onboardingplan_list"))
        assert "status_choices" in resp.context

    def test_list_search_filters_by_account_name(self, client_a, onboardingplan_a):
        resp = client_a.get(reverse("success:onboardingplan_list") + "?q=Acme+Corp")
        pks = [op.pk for op in resp.context["onboardingplans"]]
        assert onboardingplan_a.pk in pks

    def test_list_search_excludes_non_matches(self, client_a, onboardingplan_a):
        resp = client_a.get(reverse("success:onboardingplan_list") + "?q=ZZZNOMATCH")
        pks = [op.pk for op in resp.context["onboardingplans"]]
        assert onboardingplan_a.pk not in pks

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("success:onboardingplan_create"))
        assert resp.status_code == 200

    def test_create_post_creates_onboardingplan(self, client_a, tenant_a):
        before = OnboardingPlan.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("success:onboardingplan_create"), {
            "account_name": "New Onboard Corp",
            "plan_name": "New Onboarding Plan",
            "owner": "Owner",
            "status": "not_started",
            "progress_pct": "0",
            "start_date": timezone.localdate().isoformat(),
            "target_go_live": "",
            "notes": "",
        })
        assert OnboardingPlan.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a):
        client_a.post(reverse("success:onboardingplan_create"), {
            "account_name": "Tenant Check Onboard Corp",
            "plan_name": "Tenant Check Onboarding",
            "owner": "",
            "status": "not_started",
            "progress_pct": "0",
            "start_date": timezone.localdate().isoformat(),
            "target_go_live": "",
            "notes": "onb-tenant-check",
        })
        op = OnboardingPlan.objects.filter(notes="onb-tenant-check").first()
        assert op is not None
        assert op.tenant == tenant_a

    def test_detail_200(self, client_a, onboardingplan_a):
        resp = client_a.get(reverse("success:onboardingplan_detail", args=[onboardingplan_a.pk]))
        assert resp.status_code == 200

    def test_detail_context_has_obj(self, client_a, onboardingplan_a):
        resp = client_a.get(reverse("success:onboardingplan_detail", args=[onboardingplan_a.pk]))
        assert resp.context["obj"] == onboardingplan_a

    def test_edit_get_200(self, client_a, onboardingplan_a):
        resp = client_a.get(reverse("success:onboardingplan_edit", args=[onboardingplan_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_onboardingplan(self, client_a, onboardingplan_a):
        client_a.post(reverse("success:onboardingplan_edit", args=[onboardingplan_a.pk]), {
            "account_name": "Acme Corp Updated",
            "plan_name": "Updated Onboarding Plan",
            "owner": "Alice Smith",
            "status": "completed",
            "progress_pct": "100",
            "start_date": onboardingplan_a.start_date.isoformat(),
            "target_go_live": "",
            "notes": "",
        })
        onboardingplan_a.refresh_from_db()
        assert onboardingplan_a.plan_name == "Updated Onboarding Plan"
        assert onboardingplan_a.status == OnboardingPlan.STATUS_COMPLETED

    def test_delete_post_removes_onboardingplan(self, client_a, tenant_a):
        op = OnboardingPlan.objects.create(
            tenant=tenant_a,
            account_name="To Delete Onboard Corp",
            plan_name="To Delete Plan",
            start_date=timezone.localdate()
        )
        client_a.post(reverse("success:onboardingplan_delete", args=[op.pk]))
        assert not OnboardingPlan.objects.filter(pk=op.pk).exists()

    def test_delete_redirects_to_list(self, client_a, tenant_a):
        op = OnboardingPlan.objects.create(
            tenant=tenant_a,
            account_name="Redirect Onboard Corp",
            plan_name="Redirect Plan",
            start_date=timezone.localdate()
        )
        resp = client_a.post(reverse("success:onboardingplan_delete", args=[op.pk]))
        assert resp.status_code in (301, 302)

    def test_delete_get_does_not_delete(self, client_a, tenant_a):
        op = OnboardingPlan.objects.create(
            tenant=tenant_a,
            account_name="Get Delete Onboard Corp",
            plan_name="Get Delete Plan",
            start_date=timezone.localdate()
        )
        client_a.get(reverse("success:onboardingplan_delete", args=[op.pk]))
        assert OnboardingPlan.objects.filter(pk=op.pk).exists()


# ============================================================ Advocacy CRUD
@pytest.mark.django_db
class TestAdvocacyCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("success:advocacy_list"))
        assert resp.status_code == 200

    def test_list_context_has_advocacies(self, client_a, advocacy_a):
        resp = client_a.get(reverse("success:advocacy_list"))
        assert "advocacies" in resp.context

    def test_list_seeded_object_appears(self, client_a, advocacy_a):
        resp = client_a.get(reverse("success:advocacy_list"))
        pks = [a.pk for a in resp.context["advocacies"]]
        assert advocacy_a.pk in pks

    def test_list_has_type_choices(self, client_a):
        resp = client_a.get(reverse("success:advocacy_list"))
        assert "type_choices" in resp.context

    def test_list_has_status_choices(self, client_a):
        resp = client_a.get(reverse("success:advocacy_list"))
        assert "status_choices" in resp.context

    def test_list_search_filters_by_account_name(self, client_a, advocacy_a):
        resp = client_a.get(reverse("success:advocacy_list") + "?q=Acme+Corp")
        pks = [a.pk for a in resp.context["advocacies"]]
        assert advocacy_a.pk in pks

    def test_list_search_excludes_non_matches(self, client_a, advocacy_a):
        resp = client_a.get(reverse("success:advocacy_list") + "?q=ZZZNOMATCH")
        pks = [a.pk for a in resp.context["advocacies"]]
        assert advocacy_a.pk not in pks

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("success:advocacy_create"))
        assert resp.status_code == 200

    def test_create_post_creates_advocacy(self, client_a, tenant_a):
        before = Advocacy.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("success:advocacy_create"), {
            "account_name": "New Advocate Corp",
            "contact_name": "Jane Doe",
            "advocacy_type": "reference",
            "status": "nominated",
            "nps_score": "",
            "last_engaged": "",
            "notes": "",
        })
        assert Advocacy.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a):
        client_a.post(reverse("success:advocacy_create"), {
            "account_name": "Tenant Check Advocate Corp",
            "contact_name": "Jane Check",
            "advocacy_type": "testimonial",
            "status": "nominated",
            "nps_score": "",
            "last_engaged": "",
            "notes": "adv-tenant-check",
        })
        adv = Advocacy.objects.filter(notes="adv-tenant-check").first()
        assert adv is not None
        assert adv.tenant == tenant_a

    def test_detail_200(self, client_a, advocacy_a):
        resp = client_a.get(reverse("success:advocacy_detail", args=[advocacy_a.pk]))
        assert resp.status_code == 200

    def test_detail_context_has_obj(self, client_a, advocacy_a):
        resp = client_a.get(reverse("success:advocacy_detail", args=[advocacy_a.pk]))
        assert resp.context["obj"] == advocacy_a

    def test_edit_get_200(self, client_a, advocacy_a):
        resp = client_a.get(reverse("success:advocacy_edit", args=[advocacy_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_advocacy(self, client_a, advocacy_a):
        client_a.post(reverse("success:advocacy_edit", args=[advocacy_a.pk]), {
            "account_name": "Acme Corp Updated",
            "contact_name": "Alice Updated",
            "advocacy_type": "case_study",
            "status": "active",
            "nps_score": "9",
            "last_engaged": timezone.localdate().isoformat(),
            "notes": "",
        })
        advocacy_a.refresh_from_db()
        assert advocacy_a.contact_name == "Alice Updated"
        assert advocacy_a.advocacy_type == Advocacy.TYPE_CASE_STUDY

    def test_delete_post_removes_advocacy(self, client_a, tenant_a):
        adv = Advocacy.objects.create(
            tenant=tenant_a,
            account_name="To Delete Advocate Corp",
            contact_name="To Delete Contact"
        )
        client_a.post(reverse("success:advocacy_delete", args=[adv.pk]))
        assert not Advocacy.objects.filter(pk=adv.pk).exists()

    def test_delete_redirects_to_list(self, client_a, tenant_a):
        adv = Advocacy.objects.create(
            tenant=tenant_a,
            account_name="Redirect Advocate Corp",
            contact_name="Redirect Contact"
        )
        resp = client_a.post(reverse("success:advocacy_delete", args=[adv.pk]))
        assert resp.status_code in (301, 302)

    def test_delete_get_does_not_delete(self, client_a, tenant_a):
        adv = Advocacy.objects.create(
            tenant=tenant_a,
            account_name="Get Delete Advocate Corp",
            contact_name="Get Delete Contact"
        )
        client_a.get(reverse("success:advocacy_delete", args=[adv.pk]))
        assert Advocacy.objects.filter(pk=adv.pk).exists()


# ============================================================ QBR CRUD
@pytest.mark.django_db
class TestQBRCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("success:qbr_list"))
        assert resp.status_code == 200

    def test_list_context_has_qbrs(self, client_a, qbr_a):
        resp = client_a.get(reverse("success:qbr_list"))
        assert "qbrs" in resp.context

    def test_list_seeded_object_appears(self, client_a, qbr_a):
        resp = client_a.get(reverse("success:qbr_list"))
        pks = [q.pk for q in resp.context["qbrs"]]
        assert qbr_a.pk in pks

    def test_list_has_status_choices(self, client_a):
        resp = client_a.get(reverse("success:qbr_list"))
        assert "status_choices" in resp.context

    def test_list_has_sentiment_choices(self, client_a):
        resp = client_a.get(reverse("success:qbr_list"))
        assert "sentiment_choices" in resp.context

    def test_list_search_filters_by_account_name(self, client_a, qbr_a):
        resp = client_a.get(reverse("success:qbr_list") + "?q=Acme+Corp")
        pks = [q.pk for q in resp.context["qbrs"]]
        assert qbr_a.pk in pks

    def test_list_search_excludes_non_matches(self, client_a, qbr_a):
        resp = client_a.get(reverse("success:qbr_list") + "?q=ZZZNOMATCH")
        pks = [q.pk for q in resp.context["qbrs"]]
        assert qbr_a.pk not in pks

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("success:qbr_create"))
        assert resp.status_code == 200

    def test_create_post_creates_qbr(self, client_a, tenant_a):
        before = QBR.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("success:qbr_create"), {
            "account_name": "New QBR Corp",
            "period_label": "2026-Q3",
            "owner": "Owner",
            "status": "scheduled",
            "sentiment": "neutral",
            "scheduled_on": timezone.localdate().isoformat(),
            "health_summary": "",
            "notes": "",
        })
        assert QBR.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a):
        client_a.post(reverse("success:qbr_create"), {
            "account_name": "Tenant Check QBR Corp",
            "period_label": "2026-Q4",
            "owner": "",
            "status": "scheduled",
            "sentiment": "neutral",
            "scheduled_on": timezone.localdate().isoformat(),
            "health_summary": "",
            "notes": "qbr-tenant-check",
        })
        qbr = QBR.objects.filter(notes="qbr-tenant-check").first()
        assert qbr is not None
        assert qbr.tenant == tenant_a

    def test_detail_200(self, client_a, qbr_a):
        resp = client_a.get(reverse("success:qbr_detail", args=[qbr_a.pk]))
        assert resp.status_code == 200

    def test_detail_context_has_obj(self, client_a, qbr_a):
        resp = client_a.get(reverse("success:qbr_detail", args=[qbr_a.pk]))
        assert resp.context["obj"] == qbr_a

    def test_edit_get_200(self, client_a, qbr_a):
        resp = client_a.get(reverse("success:qbr_edit", args=[qbr_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_qbr(self, client_a, qbr_a):
        client_a.post(reverse("success:qbr_edit", args=[qbr_a.pk]), {
            "account_name": "Acme Corp Updated",
            "period_label": "2026-Q2",
            "owner": "Alice Smith",
            "status": "completed",
            "sentiment": "positive",
            "scheduled_on": qbr_a.scheduled_on.isoformat(),
            "health_summary": "All good",
            "notes": "",
        })
        qbr_a.refresh_from_db()
        assert qbr_a.period_label == "2026-Q2"
        assert qbr_a.status == QBR.STATUS_COMPLETED

    def test_delete_post_removes_qbr(self, client_a, tenant_a):
        qbr = QBR.objects.create(
            tenant=tenant_a,
            account_name="To Delete QBR Corp",
            period_label="2026-Q2",
            scheduled_on=timezone.localdate()
        )
        client_a.post(reverse("success:qbr_delete", args=[qbr.pk]))
        assert not QBR.objects.filter(pk=qbr.pk).exists()

    def test_delete_redirects_to_list(self, client_a, tenant_a):
        qbr = QBR.objects.create(
            tenant=tenant_a,
            account_name="Redirect QBR Corp",
            period_label="2026-Q3",
            scheduled_on=timezone.localdate()
        )
        resp = client_a.post(reverse("success:qbr_delete", args=[qbr.pk]))
        assert resp.status_code in (301, 302)

    def test_delete_get_does_not_delete(self, client_a, tenant_a):
        qbr = QBR.objects.create(
            tenant=tenant_a,
            account_name="Get Delete QBR Corp",
            period_label="2026-Q4",
            scheduled_on=timezone.localdate()
        )
        client_a.get(reverse("success:qbr_delete", args=[qbr.pk]))
        assert QBR.objects.filter(pk=qbr.pk).exists()
