"""Tests for leads.forms: required fields, exclusions, and tenant-scoped FK querysets."""
import pytest
from django.utils import timezone

from apps.leads.forms import (
    LeadConversionForm, LeadForm, LeadScoreForm, LeadSourceForm, NurtureCampaignForm,
)
from apps.leads.models import Lead, LeadConversion, LeadScore, LeadSource, NurtureCampaign


# ======================================================== LeadSourceForm
@pytest.mark.django_db
class TestLeadSourceForm:
    def test_valid_form(self):
        form = LeadSourceForm(data={
            "name": "My Web Form",
            "source_type": "web_form",
            "routing_rule": "round_robin",
            "status": "active",
            "default_owner": "",
            "cost_per_lead": "0.00",
            "description": "",
        })
        assert form.is_valid(), form.errors

    def test_missing_name_is_invalid(self):
        form = LeadSourceForm(data={
            "source_type": "web_form",
            "routing_rule": "round_robin",
            "status": "active",
        })
        assert not form.is_valid()
        assert "name" in form.errors

    def test_invalid_source_type_is_invalid(self):
        form = LeadSourceForm(data={
            "name": "Bad Type",
            "source_type": "not_real",
            "routing_rule": "round_robin",
            "status": "active",
        })
        assert not form.is_valid()

    def test_tenant_not_in_form_fields(self):
        form = LeadSourceForm()
        assert "tenant" not in form.fields

    def test_created_at_not_in_form_fields(self):
        form = LeadSourceForm()
        assert "created_at" not in form.fields

    def test_updated_at_not_in_form_fields(self):
        form = LeadSourceForm()
        assert "updated_at" not in form.fields


# ======================================================== NurtureCampaignForm
@pytest.mark.django_db
class TestNurtureCampaignForm:
    def test_valid_form(self):
        form = NurtureCampaignForm(data={
            "name": "Email Drip",
            "channel": "email",
            "status": "draft",
            "step_count": 5,
            "cadence_days": 3,
            "enrolled_count": 0,
            "start_on": "",
            "end_on": "",
            "goal": "",
        })
        assert form.is_valid(), form.errors

    def test_missing_name_is_invalid(self):
        form = NurtureCampaignForm(data={
            "channel": "email",
            "status": "draft",
            "step_count": 3,
            "cadence_days": 7,
        })
        assert not form.is_valid()
        assert "name" in form.errors

    def test_invalid_channel_is_invalid(self):
        form = NurtureCampaignForm(data={
            "name": "Bad Channel",
            "channel": "fax",
            "status": "draft",
            "step_count": 1,
            "cadence_days": 3,
        })
        assert not form.is_valid()

    def test_tenant_not_in_form_fields(self):
        form = NurtureCampaignForm()
        assert "tenant" not in form.fields

    def test_created_at_not_in_form_fields(self):
        form = NurtureCampaignForm()
        assert "created_at" not in form.fields


# ======================================================== LeadForm
@pytest.mark.django_db
class TestLeadForm:
    def test_valid_form(self, tenant_a):
        today = timezone.localdate().isoformat()
        form = LeadForm(data={
            "source": "",
            "campaign": "",
            "first_name": "Jane",
            "last_name": "Doe",
            "company": "Acme",
            "job_title": "CTO",
            "email": "jane@acme.com",
            "phone": "555-1234",
            "status": "new",
            "rating": "warm",
            "owner": "",
            "estimated_value": "0.00",
            "captured_on": today,
            "notes": "",
        }, tenant=tenant_a)
        assert form.is_valid(), form.errors

    def test_missing_first_name_is_invalid(self, tenant_a):
        today = timezone.localdate().isoformat()
        form = LeadForm(data={
            "last_name": "Doe",
            "status": "new",
            "rating": "warm",
            "captured_on": today,
        }, tenant=tenant_a)
        assert not form.is_valid()
        assert "first_name" in form.errors

    def test_missing_last_name_is_invalid(self, tenant_a):
        today = timezone.localdate().isoformat()
        form = LeadForm(data={
            "first_name": "Jane",
            "status": "new",
            "rating": "warm",
            "captured_on": today,
        }, tenant=tenant_a)
        assert not form.is_valid()
        assert "last_name" in form.errors

    def test_number_not_in_form_fields(self, tenant_a):
        """number is auto-generated, not a form field."""
        form = LeadForm(tenant=tenant_a)
        assert "number" not in form.fields

    def test_tenant_not_in_form_fields(self, tenant_a):
        form = LeadForm(tenant=tenant_a)
        assert "tenant" not in form.fields

    def test_created_at_not_in_form_fields(self, tenant_a):
        form = LeadForm(tenant=tenant_a)
        assert "created_at" not in form.fields

    def test_source_queryset_scoped_to_tenant(self, tenant_a, tenant_b, leadsource_a, leadsource_b):
        form = LeadForm(tenant=tenant_a)
        source_pks = [s.pk for s in form.fields["source"].queryset]
        assert leadsource_a.pk in source_pks
        assert leadsource_b.pk not in source_pks

    def test_campaign_queryset_scoped_to_tenant(self, tenant_a, tenant_b, campaign_a, campaign_b):
        form = LeadForm(tenant=tenant_a)
        campaign_pks = [c.pk for c in form.fields["campaign"].queryset]
        assert campaign_a.pk in campaign_pks
        assert campaign_b.pk not in campaign_pks

    def test_source_queryset_empty_without_tenant(self):
        form = LeadForm(tenant=None)
        assert form.fields["source"].queryset.count() == 0

    def test_campaign_queryset_empty_without_tenant(self):
        form = LeadForm(tenant=None)
        assert form.fields["campaign"].queryset.count() == 0

    def test_source_field_not_required(self, tenant_a):
        form = LeadForm(tenant=tenant_a)
        assert not form.fields["source"].required

    def test_campaign_field_not_required(self, tenant_a):
        form = LeadForm(tenant=tenant_a)
        assert not form.fields["campaign"].required


# ======================================================== LeadScoreForm
@pytest.mark.django_db
class TestLeadScoreForm:
    def test_valid_form(self, tenant_a, lead_a):
        today = timezone.localdate().isoformat()
        form = LeadScoreForm(data={
            "lead": lead_a.pk,
            "score": 80,
            "grade": "A",
            "scoring_model": "rules",
            "demographic_points": 40,
            "behavioral_points": 40,
            "reason": "Strong fit",
            "scored_on": today,
        }, tenant=tenant_a)
        assert form.is_valid(), form.errors

    def test_missing_lead_is_invalid(self, tenant_a):
        today = timezone.localdate().isoformat()
        form = LeadScoreForm(data={
            "score": 80,
            "grade": "A",
            "scoring_model": "rules",
            "scored_on": today,
        }, tenant=tenant_a)
        assert not form.is_valid()
        assert "lead" in form.errors

    def test_tenant_not_in_form_fields(self, tenant_a):
        form = LeadScoreForm(tenant=tenant_a)
        assert "tenant" not in form.fields

    def test_lead_queryset_scoped_to_tenant(self, tenant_a, tenant_b, lead_a, lead_b):
        form = LeadScoreForm(tenant=tenant_a)
        lead_pks = [l.pk for l in form.fields["lead"].queryset]
        assert lead_a.pk in lead_pks
        assert lead_b.pk not in lead_pks

    def test_lead_queryset_empty_without_tenant(self):
        form = LeadScoreForm(tenant=None)
        assert form.fields["lead"].queryset.count() == 0

    def test_created_at_not_in_form_fields(self, tenant_a):
        form = LeadScoreForm(tenant=tenant_a)
        assert "created_at" not in form.fields


# ======================================================== LeadConversionForm
@pytest.mark.django_db
class TestLeadConversionForm:
    def test_valid_form(self, tenant_a, lead_a):
        form = LeadConversionForm(data={
            "lead": lead_a.pk,
            "status": "pending",
            "outcome": "opportunity",
            "assigned_to": "John",
            "deal_value": "5000.00",
            "handoff_notes": "Ready to convert",
        }, tenant=tenant_a)
        assert form.is_valid(), form.errors

    def test_missing_lead_is_invalid(self, tenant_a):
        form = LeadConversionForm(data={
            "status": "pending",
            "outcome": "opportunity",
        }, tenant=tenant_a)
        assert not form.is_valid()
        assert "lead" in form.errors

    def test_number_not_in_form_fields(self, tenant_a):
        """number is auto-generated, not a form field."""
        form = LeadConversionForm(tenant=tenant_a)
        assert "number" not in form.fields

    def test_converted_at_not_in_form_fields(self, tenant_a):
        """converted_at is system-set, not a form field."""
        form = LeadConversionForm(tenant=tenant_a)
        assert "converted_at" not in form.fields

    def test_tenant_not_in_form_fields(self, tenant_a):
        form = LeadConversionForm(tenant=tenant_a)
        assert "tenant" not in form.fields

    def test_lead_queryset_scoped_to_tenant(self, tenant_a, tenant_b, lead_a, lead_b):
        form = LeadConversionForm(tenant=tenant_a)
        lead_pks = [l.pk for l in form.fields["lead"].queryset]
        assert lead_a.pk in lead_pks
        assert lead_b.pk not in lead_pks

    def test_lead_queryset_empty_without_tenant(self):
        form = LeadConversionForm(tenant=None)
        assert form.fields["lead"].queryset.count() == 0

    def test_created_at_not_in_form_fields(self, tenant_a):
        form = LeadConversionForm(tenant=tenant_a)
        assert "created_at" not in form.fields
