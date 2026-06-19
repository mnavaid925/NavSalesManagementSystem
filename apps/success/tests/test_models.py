"""Tests for success models: HealthScore, Renewal, OnboardingPlan, Advocacy, QBR."""
import pytest
from django.utils import timezone

from apps.success.models import (
    HealthScore, Renewal, OnboardingPlan, Advocacy, QBR,
)


# ============================================================ HealthScore
@pytest.mark.django_db
class TestHealthScore:
    def test_str_returns_account_name(self, healthscore_a):
        assert str(healthscore_a) == "Acme Corp"

    def test_default_score_is_50(self, tenant_a):
        hs = HealthScore.objects.create(
            tenant=tenant_a, account_name="Default Score Acct",
            last_reviewed=timezone.localdate()
        )
        assert hs.score == 50

    def test_default_risk_level_is_medium(self, tenant_a):
        hs = HealthScore.objects.create(
            tenant=tenant_a, account_name="Default Risk Acct",
            last_reviewed=timezone.localdate()
        )
        assert hs.risk_level == HealthScore.RISK_MEDIUM

    def test_default_trend_is_stable(self, tenant_a):
        hs = HealthScore.objects.create(
            tenant=tenant_a, account_name="Default Trend Acct",
            last_reviewed=timezone.localdate()
        )
        assert hs.trend == HealthScore.TREND_STABLE

    def test_default_arr_is_zero(self, tenant_a):
        hs = HealthScore.objects.create(
            tenant=tenant_a, account_name="Default ARR Acct",
            last_reviewed=timezone.localdate()
        )
        assert hs.arr == 0

    def test_default_last_reviewed_is_today(self, tenant_a):
        hs = HealthScore.objects.create(
            tenant=tenant_a, account_name="Today Reviewed Acct"
        )
        assert hs.last_reviewed == timezone.localdate()

    def test_risk_level_choices_contain_all_four(self):
        choices = dict(HealthScore.RISK_LEVEL_CHOICES)
        assert HealthScore.RISK_LOW in choices
        assert HealthScore.RISK_MEDIUM in choices
        assert HealthScore.RISK_HIGH in choices
        assert HealthScore.RISK_CRITICAL in choices

    def test_trend_choices_contain_all_three(self):
        choices = dict(HealthScore.TREND_CHOICES)
        assert HealthScore.TREND_IMPROVING in choices
        assert HealthScore.TREND_STABLE in choices
        assert HealthScore.TREND_DECLINING in choices

    def test_owner_is_optional(self, tenant_a):
        hs = HealthScore.objects.create(
            tenant=tenant_a, account_name="No Owner Acct",
            last_reviewed=timezone.localdate()
        )
        assert hs.owner == ""

    def test_notes_is_optional(self, tenant_a):
        hs = HealthScore.objects.create(
            tenant=tenant_a, account_name="No Notes Acct",
            last_reviewed=timezone.localdate()
        )
        assert hs.notes == ""

    def test_tenant_fk_set(self, healthscore_a, tenant_a):
        assert healthscore_a.tenant == tenant_a

    def test_created_at_set_automatically(self, healthscore_a):
        assert healthscore_a.created_at is not None

    def test_updated_at_set_automatically(self, healthscore_a):
        assert healthscore_a.updated_at is not None


# ============================================================ Renewal
@pytest.mark.django_db
class TestRenewal:
    def test_auto_number_generated_on_save(self, renewal_a):
        assert renewal_a.number.startswith("REN-")

    def test_auto_number_format_five_digits(self, renewal_a):
        parts = renewal_a.number.split("-")
        assert len(parts) == 2
        assert len(parts[1]) == 5
        assert parts[1].isdigit()

    def test_first_renewal_is_REN_00001(self, tenant_a):
        Renewal.objects.filter(tenant=tenant_a).delete()
        r = Renewal.objects.create(
            tenant=tenant_a,
            account_name="First Renewal Acct",
            renewal_date=timezone.localdate(),
        )
        assert r.number == "REN-00001"

    def test_auto_number_increments_per_tenant(self, tenant_a):
        Renewal.objects.filter(tenant=tenant_a).delete()
        r1 = Renewal.objects.create(
            tenant=tenant_a, account_name="Acct 1", renewal_date=timezone.localdate()
        )
        r2 = Renewal.objects.create(
            tenant=tenant_a, account_name="Acct 2", renewal_date=timezone.localdate()
        )
        assert r1.number == "REN-00001"
        assert r2.number == "REN-00002"

    def test_auto_number_isolated_per_tenant(self, tenant_a, tenant_b):
        Renewal.objects.filter(tenant=tenant_a).delete()
        Renewal.objects.filter(tenant=tenant_b).delete()
        ra = Renewal.objects.create(
            tenant=tenant_a, account_name="Tenant A Acct", renewal_date=timezone.localdate()
        )
        rb = Renewal.objects.create(
            tenant=tenant_b, account_name="Tenant B Acct", renewal_date=timezone.localdate()
        )
        assert ra.number == "REN-00001"
        assert rb.number == "REN-00001"

    def test_str_returns_number(self, renewal_a):
        assert renewal_a.number in str(renewal_a)

    def test_str_fallback_when_no_number(self, tenant_a):
        r = Renewal(tenant=tenant_a, account_name="Unsaved Acct")
        # not saved — number is blank
        result = str(r)
        assert result is not None

    def test_unique_together_tenant_number(self, tenant_a):
        Renewal.objects.filter(tenant=tenant_a).delete()
        r = Renewal.objects.create(
            tenant=tenant_a, account_name="First Acct", renewal_date=timezone.localdate()
        )
        import django.db.utils as db_utils
        with pytest.raises(db_utils.IntegrityError):
            Renewal.objects.create(
                tenant=tenant_a, number=r.number, account_name="Dup Acct",
                renewal_date=timezone.localdate()
            )

    def test_default_renewal_type_is_renewal(self, tenant_a):
        Renewal.objects.filter(tenant=tenant_a).delete()
        r = Renewal.objects.create(
            tenant=tenant_a, account_name="Default Type Acct",
            renewal_date=timezone.localdate()
        )
        assert r.renewal_type == Renewal.TYPE_RENEWAL

    def test_default_status_is_open(self, tenant_a):
        Renewal.objects.filter(tenant=tenant_a).delete()
        r = Renewal.objects.create(
            tenant=tenant_a, account_name="Default Status Acct",
            renewal_date=timezone.localdate()
        )
        assert r.status == Renewal.STATUS_OPEN

    def test_default_probability_is_50(self, tenant_a):
        Renewal.objects.filter(tenant=tenant_a).delete()
        r = Renewal.objects.create(
            tenant=tenant_a, account_name="Default Prob Acct",
            renewal_date=timezone.localdate()
        )
        assert r.probability == 50

    def test_renewal_type_choices_contain_all_four(self):
        choices = dict(Renewal.RENEWAL_TYPE_CHOICES)
        assert Renewal.TYPE_RENEWAL in choices
        assert Renewal.TYPE_UPSELL in choices
        assert Renewal.TYPE_CROSS_SELL in choices
        assert Renewal.TYPE_EXPANSION in choices

    def test_status_choices_contain_all_five(self):
        choices = dict(Renewal.STATUS_CHOICES)
        assert Renewal.STATUS_OPEN in choices
        assert Renewal.STATUS_AT_RISK in choices
        assert Renewal.STATUS_COMMITTED in choices
        assert Renewal.STATUS_WON in choices
        assert Renewal.STATUS_LOST in choices

    def test_tenant_fk_set(self, renewal_a, tenant_a):
        assert renewal_a.tenant == tenant_a

    def test_created_at_set_automatically(self, renewal_a):
        assert renewal_a.created_at is not None

    def test_updated_at_set_automatically(self, renewal_a):
        assert renewal_a.updated_at is not None


# ============================================================ OnboardingPlan
@pytest.mark.django_db
class TestOnboardingPlan:
    def test_str_returns_plan_name(self, onboardingplan_a):
        assert str(onboardingplan_a) == "Acme Onboarding Q1"

    def test_default_status_is_not_started(self, tenant_a):
        op = OnboardingPlan.objects.create(
            tenant=tenant_a,
            account_name="Default Status Acct",
            plan_name="Default Status Plan",
            start_date=timezone.localdate()
        )
        assert op.status == OnboardingPlan.STATUS_NOT_STARTED

    def test_default_progress_pct_is_zero(self, tenant_a):
        op = OnboardingPlan.objects.create(
            tenant=tenant_a,
            account_name="Default Progress Acct",
            plan_name="Default Progress Plan",
            start_date=timezone.localdate()
        )
        assert op.progress_pct == 0

    def test_default_start_date_is_today(self, tenant_a):
        op = OnboardingPlan.objects.create(
            tenant=tenant_a,
            account_name="Default Date Acct",
            plan_name="Default Date Plan",
        )
        assert op.start_date == timezone.localdate()

    def test_target_go_live_is_nullable(self, tenant_a):
        op = OnboardingPlan.objects.create(
            tenant=tenant_a,
            account_name="Nullable Date Acct",
            plan_name="Nullable Date Plan",
            start_date=timezone.localdate()
        )
        assert op.target_go_live is None

    def test_status_choices_contain_all_four(self):
        choices = dict(OnboardingPlan.STATUS_CHOICES)
        assert OnboardingPlan.STATUS_NOT_STARTED in choices
        assert OnboardingPlan.STATUS_IN_PROGRESS in choices
        assert OnboardingPlan.STATUS_BLOCKED in choices
        assert OnboardingPlan.STATUS_COMPLETED in choices

    def test_owner_is_optional(self, tenant_a):
        op = OnboardingPlan.objects.create(
            tenant=tenant_a,
            account_name="No Owner Acct",
            plan_name="No Owner Plan",
            start_date=timezone.localdate()
        )
        assert op.owner == ""

    def test_notes_is_optional(self, tenant_a):
        op = OnboardingPlan.objects.create(
            tenant=tenant_a,
            account_name="No Notes Acct",
            plan_name="No Notes Plan",
            start_date=timezone.localdate()
        )
        assert op.notes == ""

    def test_tenant_fk_set(self, onboardingplan_a, tenant_a):
        assert onboardingplan_a.tenant == tenant_a

    def test_created_at_set_automatically(self, onboardingplan_a):
        assert onboardingplan_a.created_at is not None

    def test_updated_at_set_automatically(self, onboardingplan_a):
        assert onboardingplan_a.updated_at is not None


# ============================================================ Advocacy
@pytest.mark.django_db
class TestAdvocacy:
    def test_str_shows_contact_and_account(self, advocacy_a):
        result = str(advocacy_a)
        assert "Alice Smith" in result
        assert "Acme Corp" in result

    def test_default_advocacy_type_is_reference(self, tenant_a):
        adv = Advocacy.objects.create(
            tenant=tenant_a,
            account_name="Default Type Acct",
            contact_name="Default Contact"
        )
        assert adv.advocacy_type == Advocacy.TYPE_REFERENCE

    def test_default_status_is_nominated(self, tenant_a):
        adv = Advocacy.objects.create(
            tenant=tenant_a,
            account_name="Default Status Acct",
            contact_name="Default Status Contact"
        )
        assert adv.status == Advocacy.STATUS_NOMINATED

    def test_nps_score_is_nullable(self, tenant_a):
        adv = Advocacy.objects.create(
            tenant=tenant_a,
            account_name="No NPS Acct",
            contact_name="No NPS Contact"
        )
        assert adv.nps_score is None

    def test_last_engaged_is_nullable(self, tenant_a):
        adv = Advocacy.objects.create(
            tenant=tenant_a,
            account_name="No Engaged Acct",
            contact_name="No Engaged Contact"
        )
        assert adv.last_engaged is None

    def test_advocacy_type_choices_contain_all_five(self):
        choices = dict(Advocacy.ADVOCACY_TYPE_CHOICES)
        assert Advocacy.TYPE_REFERENCE in choices
        assert Advocacy.TYPE_CASE_STUDY in choices
        assert Advocacy.TYPE_TESTIMONIAL in choices
        assert Advocacy.TYPE_REVIEW in choices
        assert Advocacy.TYPE_SPEAKER in choices

    def test_status_choices_contain_all_four(self):
        choices = dict(Advocacy.STATUS_CHOICES)
        assert Advocacy.STATUS_NOMINATED in choices
        assert Advocacy.STATUS_ACTIVE in choices
        assert Advocacy.STATUS_DECLINED in choices
        assert Advocacy.STATUS_RETIRED in choices

    def test_notes_is_optional(self, tenant_a):
        adv = Advocacy.objects.create(
            tenant=tenant_a,
            account_name="No Notes Acct",
            contact_name="No Notes Contact"
        )
        assert adv.notes == ""

    def test_tenant_fk_set(self, advocacy_a, tenant_a):
        assert advocacy_a.tenant == tenant_a

    def test_created_at_set_automatically(self, advocacy_a):
        assert advocacy_a.created_at is not None

    def test_updated_at_set_automatically(self, advocacy_a):
        assert advocacy_a.updated_at is not None


# ============================================================ QBR
@pytest.mark.django_db
class TestQBR:
    def test_str_shows_account_and_period(self, qbr_a):
        result = str(qbr_a)
        assert "Acme Corp" in result
        assert "2026-Q1" in result

    def test_default_status_is_scheduled(self, tenant_a):
        qbr = QBR.objects.create(
            tenant=tenant_a,
            account_name="Default Status Acct",
            period_label="2026-Q3",
            scheduled_on=timezone.localdate()
        )
        assert qbr.status == QBR.STATUS_SCHEDULED

    def test_default_sentiment_is_neutral(self, tenant_a):
        qbr = QBR.objects.create(
            tenant=tenant_a,
            account_name="Default Sentiment Acct",
            period_label="2026-Q3",
            scheduled_on=timezone.localdate()
        )
        assert qbr.sentiment == QBR.SENTIMENT_NEUTRAL

    def test_default_scheduled_on_is_today(self, tenant_a):
        qbr = QBR.objects.create(
            tenant=tenant_a,
            account_name="Default Date Acct",
            period_label="2026-Q3",
        )
        assert qbr.scheduled_on == timezone.localdate()

    def test_status_choices_contain_all_three(self):
        choices = dict(QBR.STATUS_CHOICES)
        assert QBR.STATUS_SCHEDULED in choices
        assert QBR.STATUS_COMPLETED in choices
        assert QBR.STATUS_CANCELED in choices

    def test_sentiment_choices_contain_all_three(self):
        choices = dict(QBR.SENTIMENT_CHOICES)
        assert QBR.SENTIMENT_POSITIVE in choices
        assert QBR.SENTIMENT_NEUTRAL in choices
        assert QBR.SENTIMENT_NEGATIVE in choices

    def test_owner_is_optional(self, tenant_a):
        qbr = QBR.objects.create(
            tenant=tenant_a,
            account_name="No Owner Acct",
            period_label="2026-Q4",
            scheduled_on=timezone.localdate()
        )
        assert qbr.owner == ""

    def test_health_summary_is_optional(self, tenant_a):
        qbr = QBR.objects.create(
            tenant=tenant_a,
            account_name="No Summary Acct",
            period_label="2026-Q4",
            scheduled_on=timezone.localdate()
        )
        assert qbr.health_summary == ""

    def test_notes_is_optional(self, tenant_a):
        qbr = QBR.objects.create(
            tenant=tenant_a,
            account_name="No Notes Acct",
            period_label="2026-Q4",
            scheduled_on=timezone.localdate()
        )
        assert qbr.notes == ""

    def test_tenant_fk_set(self, qbr_a, tenant_a):
        assert qbr_a.tenant == tenant_a

    def test_created_at_set_automatically(self, qbr_a):
        assert qbr_a.created_at is not None

    def test_updated_at_set_automatically(self, qbr_a):
        assert qbr_a.updated_at is not None
