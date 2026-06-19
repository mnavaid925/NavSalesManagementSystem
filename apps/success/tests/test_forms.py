"""Tests for success forms: required fields, exclusions, and mass-assignment guards."""
import pytest
from django.utils import timezone

from apps.success.forms import (
    HealthScoreForm, RenewalForm, OnboardingPlanForm, AdvocacyForm, QBRForm,
)
from apps.success.models import (
    HealthScore, Renewal, OnboardingPlan, Advocacy, QBR,
)


# ============================================================ HealthScoreForm
@pytest.mark.django_db
class TestHealthScoreForm:
    def _valid_data(self):
        return {
            "account_name": "Test Corp",
            "owner": "Alice Smith",
            "score": "80",
            "risk_level": HealthScore.RISK_LOW,
            "trend": HealthScore.TREND_IMPROVING,
            "arr": "150000.00",
            "last_reviewed": timezone.localdate().isoformat(),
            "notes": "",
        }

    def test_valid_form(self):
        form = HealthScoreForm(data=self._valid_data())
        assert form.is_valid(), form.errors

    def test_missing_account_name_invalid(self):
        data = self._valid_data()
        del data["account_name"]
        form = HealthScoreForm(data=data)
        assert not form.is_valid()
        assert "account_name" in form.errors

    def test_missing_last_reviewed_invalid(self):
        data = self._valid_data()
        data["last_reviewed"] = ""
        form = HealthScoreForm(data=data)
        assert not form.is_valid()
        assert "last_reviewed" in form.errors

    def test_invalid_risk_level_invalid(self):
        data = self._valid_data()
        data["risk_level"] = "unknown_risk"
        form = HealthScoreForm(data=data)
        assert not form.is_valid()

    def test_invalid_trend_invalid(self):
        data = self._valid_data()
        data["trend"] = "unknown_trend"
        form = HealthScoreForm(data=data)
        assert not form.is_valid()

    def test_tenant_not_in_form_fields(self):
        form = HealthScoreForm()
        assert "tenant" not in form.fields

    def test_created_at_not_in_form_fields(self):
        form = HealthScoreForm()
        assert "created_at" not in form.fields

    def test_updated_at_not_in_form_fields(self):
        form = HealthScoreForm()
        assert "updated_at" not in form.fields

    def test_owner_field_not_required(self):
        data = self._valid_data()
        data["owner"] = ""
        form = HealthScoreForm(data=data)
        assert form.is_valid(), form.errors


# ============================================================ RenewalForm
@pytest.mark.django_db
class TestRenewalForm:
    def _valid_data(self):
        return {
            "account_name": "Test Corp",
            "owner": "Alice Smith",
            "renewal_type": Renewal.TYPE_RENEWAL,
            "status": Renewal.STATUS_OPEN,
            "arr_current": "100000.00",
            "arr_proposed": "110000.00",
            "probability": "70",
            "renewal_date": timezone.localdate().isoformat(),
            "notes": "",
        }

    def test_valid_form(self):
        form = RenewalForm(data=self._valid_data())
        assert form.is_valid(), form.errors

    def test_missing_account_name_invalid(self):
        data = self._valid_data()
        del data["account_name"]
        form = RenewalForm(data=data)
        assert not form.is_valid()
        assert "account_name" in form.errors

    def test_missing_renewal_date_invalid(self):
        data = self._valid_data()
        data["renewal_date"] = ""
        form = RenewalForm(data=data)
        assert not form.is_valid()
        assert "renewal_date" in form.errors

    def test_invalid_renewal_type_invalid(self):
        data = self._valid_data()
        data["renewal_type"] = "invalid_type"
        form = RenewalForm(data=data)
        assert not form.is_valid()

    def test_invalid_status_invalid(self):
        data = self._valid_data()
        data["status"] = "invalid_status"
        form = RenewalForm(data=data)
        assert not form.is_valid()

    def test_tenant_not_in_form_fields(self):
        """tenant is set server-side; must NOT be a form field."""
        form = RenewalForm()
        assert "tenant" not in form.fields

    def test_number_not_in_form_fields(self):
        """number is auto-generated; must NOT be a form field."""
        form = RenewalForm()
        assert "number" not in form.fields

    def test_created_at_not_in_form_fields(self):
        form = RenewalForm()
        assert "created_at" not in form.fields

    def test_updated_at_not_in_form_fields(self):
        form = RenewalForm()
        assert "updated_at" not in form.fields

    def test_owner_field_not_required(self):
        data = self._valid_data()
        data["owner"] = ""
        form = RenewalForm(data=data)
        assert form.is_valid(), form.errors


# ============================================================ OnboardingPlanForm
@pytest.mark.django_db
class TestOnboardingPlanForm:
    def _valid_data(self):
        return {
            "account_name": "Test Corp",
            "plan_name": "Test Onboarding Plan",
            "owner": "Alice Smith",
            "status": OnboardingPlan.STATUS_IN_PROGRESS,
            "progress_pct": "50",
            "start_date": timezone.localdate().isoformat(),
            "target_go_live": "",
            "notes": "",
        }

    def test_valid_form(self):
        form = OnboardingPlanForm(data=self._valid_data())
        assert form.is_valid(), form.errors

    def test_missing_account_name_invalid(self):
        data = self._valid_data()
        del data["account_name"]
        form = OnboardingPlanForm(data=data)
        assert not form.is_valid()
        assert "account_name" in form.errors

    def test_missing_plan_name_invalid(self):
        data = self._valid_data()
        del data["plan_name"]
        form = OnboardingPlanForm(data=data)
        assert not form.is_valid()
        assert "plan_name" in form.errors

    def test_missing_start_date_invalid(self):
        data = self._valid_data()
        data["start_date"] = ""
        form = OnboardingPlanForm(data=data)
        assert not form.is_valid()
        assert "start_date" in form.errors

    def test_invalid_status_invalid(self):
        data = self._valid_data()
        data["status"] = "invalid_status"
        form = OnboardingPlanForm(data=data)
        assert not form.is_valid()

    def test_tenant_not_in_form_fields(self):
        form = OnboardingPlanForm()
        assert "tenant" not in form.fields

    def test_created_at_not_in_form_fields(self):
        form = OnboardingPlanForm()
        assert "created_at" not in form.fields

    def test_updated_at_not_in_form_fields(self):
        form = OnboardingPlanForm()
        assert "updated_at" not in form.fields

    def test_target_go_live_not_required(self):
        data = self._valid_data()
        data["target_go_live"] = ""
        form = OnboardingPlanForm(data=data)
        assert form.is_valid(), form.errors

    def test_owner_field_not_required(self):
        data = self._valid_data()
        data["owner"] = ""
        form = OnboardingPlanForm(data=data)
        assert form.is_valid(), form.errors


# ============================================================ AdvocacyForm
@pytest.mark.django_db
class TestAdvocacyForm:
    def _valid_data(self):
        return {
            "account_name": "Test Corp",
            "contact_name": "Jane Doe",
            "advocacy_type": Advocacy.TYPE_REFERENCE,
            "status": Advocacy.STATUS_ACTIVE,
            "nps_score": "",
            "last_engaged": "",
            "notes": "",
        }

    def test_valid_form(self):
        form = AdvocacyForm(data=self._valid_data())
        assert form.is_valid(), form.errors

    def test_missing_account_name_invalid(self):
        data = self._valid_data()
        del data["account_name"]
        form = AdvocacyForm(data=data)
        assert not form.is_valid()
        assert "account_name" in form.errors

    def test_missing_contact_name_invalid(self):
        data = self._valid_data()
        del data["contact_name"]
        form = AdvocacyForm(data=data)
        assert not form.is_valid()
        assert "contact_name" in form.errors

    def test_invalid_advocacy_type_invalid(self):
        data = self._valid_data()
        data["advocacy_type"] = "invalid_type"
        form = AdvocacyForm(data=data)
        assert not form.is_valid()

    def test_invalid_status_invalid(self):
        data = self._valid_data()
        data["status"] = "invalid_status"
        form = AdvocacyForm(data=data)
        assert not form.is_valid()

    def test_tenant_not_in_form_fields(self):
        form = AdvocacyForm()
        assert "tenant" not in form.fields

    def test_created_at_not_in_form_fields(self):
        form = AdvocacyForm()
        assert "created_at" not in form.fields

    def test_updated_at_not_in_form_fields(self):
        form = AdvocacyForm()
        assert "updated_at" not in form.fields

    def test_nps_score_not_required(self):
        data = self._valid_data()
        data["nps_score"] = ""
        form = AdvocacyForm(data=data)
        assert form.is_valid(), form.errors

    def test_last_engaged_not_required(self):
        data = self._valid_data()
        data["last_engaged"] = ""
        form = AdvocacyForm(data=data)
        assert form.is_valid(), form.errors


# ============================================================ QBRForm
@pytest.mark.django_db
class TestQBRForm:
    def _valid_data(self):
        return {
            "account_name": "Test Corp",
            "period_label": "2026-Q1",
            "owner": "Alice Smith",
            "status": QBR.STATUS_SCHEDULED,
            "sentiment": QBR.SENTIMENT_POSITIVE,
            "scheduled_on": timezone.localdate().isoformat(),
            "health_summary": "",
            "notes": "",
        }

    def test_valid_form(self):
        form = QBRForm(data=self._valid_data())
        assert form.is_valid(), form.errors

    def test_missing_account_name_invalid(self):
        data = self._valid_data()
        del data["account_name"]
        form = QBRForm(data=data)
        assert not form.is_valid()
        assert "account_name" in form.errors

    def test_missing_period_label_invalid(self):
        data = self._valid_data()
        del data["period_label"]
        form = QBRForm(data=data)
        assert not form.is_valid()
        assert "period_label" in form.errors

    def test_missing_scheduled_on_invalid(self):
        data = self._valid_data()
        data["scheduled_on"] = ""
        form = QBRForm(data=data)
        assert not form.is_valid()
        assert "scheduled_on" in form.errors

    def test_invalid_status_invalid(self):
        data = self._valid_data()
        data["status"] = "invalid_status"
        form = QBRForm(data=data)
        assert not form.is_valid()

    def test_invalid_sentiment_invalid(self):
        data = self._valid_data()
        data["sentiment"] = "invalid_sentiment"
        form = QBRForm(data=data)
        assert not form.is_valid()

    def test_tenant_not_in_form_fields(self):
        form = QBRForm()
        assert "tenant" not in form.fields

    def test_created_at_not_in_form_fields(self):
        form = QBRForm()
        assert "created_at" not in form.fields

    def test_updated_at_not_in_form_fields(self):
        form = QBRForm()
        assert "updated_at" not in form.fields

    def test_owner_field_not_required(self):
        data = self._valid_data()
        data["owner"] = ""
        form = QBRForm(data=data)
        assert form.is_valid(), form.errors

    def test_health_summary_not_required(self):
        data = self._valid_data()
        data["health_summary"] = ""
        form = QBRForm(data=data)
        assert form.is_valid(), form.errors
