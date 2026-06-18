"""Tests for opportunities forms: required fields, exclusions, and tenant-scoped FK querysets."""
import pytest

from apps.opportunities.forms import (
    CompetitorForm,
    DealCollaboratorForm,
    OpportunityActivityForm,
    OpportunityForm,
    PipelineStageForm,
)
from apps.opportunities.models import Opportunity, PipelineStage


# ════════════════════════════════════════════════════════════════
#  PipelineStageForm
# ════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestPipelineStageForm:
    def test_valid_form(self):
        form = PipelineStageForm(data={
            "name": "Qualification",
            "description": "First stage",
            "order": 1,
            "probability": 20,
            "stage_type": "open",
            "is_active": True,
        })
        assert form.is_valid(), form.errors

    def test_missing_name_invalid(self):
        form = PipelineStageForm(data={
            "description": "",
            "order": 1,
            "probability": 10,
            "stage_type": "open",
            "is_active": True,
        })
        assert not form.is_valid()
        assert "name" in form.errors

    def test_tenant_not_in_form_fields(self):
        form = PipelineStageForm()
        assert "tenant" not in form.fields

    def test_created_at_not_in_form_fields(self):
        form = PipelineStageForm()
        assert "created_at" not in form.fields

    def test_updated_at_not_in_form_fields(self):
        form = PipelineStageForm()
        assert "updated_at" not in form.fields

    def test_invalid_stage_type_invalid(self):
        form = PipelineStageForm(data={
            "name": "Bad Type",
            "description": "",
            "order": 1,
            "probability": 10,
            "stage_type": "invalid_type",
            "is_active": True,
        })
        assert not form.is_valid()
        assert "stage_type" in form.errors


# ════════════════════════════════════════════════════════════════
#  OpportunityForm
# ════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestOpportunityForm:
    def test_valid_form(self, tenant_a):
        form = OpportunityForm(data={
            "name": "Test Opportunity",
            "account_name": "Test Account",
            "stage": "",
            "status": "open",
            "priority": "medium",
            "forecast_category": "pipeline",
            "amount": "25000.00",
            "probability": 50,
            "owner_name": "Alice",
            "source": "Inbound",
            "expected_close_date": "",
            "description": "",
        }, tenant=tenant_a)
        assert form.is_valid(), form.errors

    def test_missing_name_invalid(self, tenant_a):
        form = OpportunityForm(data={
            "account_name": "",
            "stage": "",
            "status": "open",
            "priority": "medium",
            "forecast_category": "pipeline",
            "amount": "0",
            "probability": 10,
        }, tenant=tenant_a)
        assert not form.is_valid()
        assert "name" in form.errors

    def test_tenant_not_in_form_fields(self, tenant_a):
        form = OpportunityForm(tenant=tenant_a)
        assert "tenant" not in form.fields

    def test_number_not_in_form_fields(self, tenant_a):
        """number is auto-generated — must not appear in the form."""
        form = OpportunityForm(tenant=tenant_a)
        assert "number" not in form.fields

    def test_closed_at_not_in_form_fields(self, tenant_a):
        """closed_at is a system timestamp — must not appear in the form."""
        form = OpportunityForm(tenant=tenant_a)
        assert "closed_at" not in form.fields

    def test_stage_queryset_scoped_to_tenant(self, tenant_a, tenant_b, stage_a, stage_b):
        """Stage FK queryset must only include stages from the request tenant."""
        form = OpportunityForm(tenant=tenant_a)
        stage_pks = list(form.fields["stage"].queryset.values_list("pk", flat=True))
        assert stage_a.pk in stage_pks
        assert stage_b.pk not in stage_pks

    def test_stage_queryset_empty_without_tenant(self):
        """Without a tenant, stage queryset must be empty (no cross-tenant leak)."""
        form = OpportunityForm(tenant=None)
        assert form.fields["stage"].queryset.count() == 0

    def test_stage_not_required(self, tenant_a):
        form = OpportunityForm(data={
            "name": "No Stage Opp",
            "account_name": "",
            "stage": "",
            "status": "open",
            "priority": "medium",
            "forecast_category": "pipeline",
            "amount": "0",
            "probability": 10,
            "owner_name": "",
            "source": "",
            "expected_close_date": "",
            "description": "",
        }, tenant=tenant_a)
        assert form.is_valid(), form.errors


# ════════════════════════════════════════════════════════════════
#  OpportunityActivityForm
# ════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestOpportunityActivityForm:
    def test_valid_form(self, tenant_a, opportunity_a):
        form = OpportunityActivityForm(data={
            "opportunity": opportunity_a.pk,
            "subject": "Discovery call",
            "activity_type": "call",
            "outcome": "positive",
            "performed_by": "Alice",
            "activity_date": "2026-01-15",
            "notes": "",
        }, tenant=tenant_a)
        assert form.is_valid(), form.errors

    def test_missing_subject_invalid(self, tenant_a, opportunity_a):
        form = OpportunityActivityForm(data={
            "opportunity": opportunity_a.pk,
            "subject": "",
            "activity_type": "call",
            "outcome": "pending",
        }, tenant=tenant_a)
        assert not form.is_valid()
        assert "subject" in form.errors

    def test_tenant_not_in_form_fields(self, tenant_a):
        form = OpportunityActivityForm(tenant=tenant_a)
        assert "tenant" not in form.fields

    def test_opportunity_queryset_scoped_to_tenant(self, tenant_a, tenant_b, opportunity_a, opportunity_b):
        form = OpportunityActivityForm(tenant=tenant_a)
        opp_pks = list(form.fields["opportunity"].queryset.values_list("pk", flat=True))
        assert opportunity_a.pk in opp_pks
        assert opportunity_b.pk not in opp_pks

    def test_opportunity_queryset_empty_without_tenant(self):
        form = OpportunityActivityForm(tenant=None)
        assert form.fields["opportunity"].queryset.count() == 0


# ════════════════════════════════════════════════════════════════
#  CompetitorForm
# ════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestCompetitorForm:
    def test_valid_form(self, tenant_a, opportunity_a):
        form = CompetitorForm(data={
            "opportunity": opportunity_a.pk,
            "name": "CompetitorZ",
            "threat_level": "high",
            "status": "active",
            "strengths": "Good support",
            "weaknesses": "Expensive",
            "our_strategy": "Undercut on price",
        }, tenant=tenant_a)
        assert form.is_valid(), form.errors

    def test_missing_name_invalid(self, tenant_a, opportunity_a):
        form = CompetitorForm(data={
            "opportunity": opportunity_a.pk,
            "name": "",
            "threat_level": "medium",
            "status": "active",
        }, tenant=tenant_a)
        assert not form.is_valid()
        assert "name" in form.errors

    def test_tenant_not_in_form_fields(self, tenant_a):
        form = CompetitorForm(tenant=tenant_a)
        assert "tenant" not in form.fields

    def test_opportunity_queryset_scoped_to_tenant(self, tenant_a, tenant_b, opportunity_a, opportunity_b):
        form = CompetitorForm(tenant=tenant_a)
        opp_pks = list(form.fields["opportunity"].queryset.values_list("pk", flat=True))
        assert opportunity_a.pk in opp_pks
        assert opportunity_b.pk not in opp_pks

    def test_opportunity_queryset_empty_without_tenant(self):
        form = CompetitorForm(tenant=None)
        assert form.fields["opportunity"].queryset.count() == 0


# ════════════════════════════════════════════════════════════════
#  DealCollaboratorForm
# ════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestDealCollaboratorForm:
    def test_valid_form(self, tenant_a, opportunity_a):
        form = DealCollaboratorForm(data={
            "opportunity": opportunity_a.pk,
            "member_name": "Eve Adams",
            "email": "eve@acme.com",
            "team_role": "sales_engineer",
            "status": "active",
            "contribution": "Technical lead",
        }, tenant=tenant_a)
        assert form.is_valid(), form.errors

    def test_missing_member_name_invalid(self, tenant_a, opportunity_a):
        form = DealCollaboratorForm(data={
            "opportunity": opportunity_a.pk,
            "member_name": "",
            "email": "",
            "team_role": "sales_engineer",
            "status": "active",
        }, tenant=tenant_a)
        assert not form.is_valid()
        assert "member_name" in form.errors

    def test_tenant_not_in_form_fields(self, tenant_a):
        form = DealCollaboratorForm(tenant=tenant_a)
        assert "tenant" not in form.fields

    def test_opportunity_queryset_scoped_to_tenant(self, tenant_a, tenant_b, opportunity_a, opportunity_b):
        form = DealCollaboratorForm(tenant=tenant_a)
        opp_pks = list(form.fields["opportunity"].queryset.values_list("pk", flat=True))
        assert opportunity_a.pk in opp_pks
        assert opportunity_b.pk not in opp_pks

    def test_opportunity_queryset_empty_without_tenant(self):
        form = DealCollaboratorForm(tenant=None)
        assert form.fields["opportunity"].queryset.count() == 0

    def test_invalid_email_invalid(self, tenant_a, opportunity_a):
        form = DealCollaboratorForm(data={
            "opportunity": opportunity_a.pk,
            "member_name": "Frank",
            "email": "not-an-email",
            "team_role": "legal",
            "status": "active",
        }, tenant=tenant_a)
        assert not form.is_valid()
        assert "email" in form.errors
