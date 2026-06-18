"""Tests for leads.models: LeadSource, NurtureCampaign, Lead, LeadScore, LeadConversion."""
import pytest
from django.utils import timezone

from apps.leads.models import (
    Lead, LeadConversion, LeadScore, LeadSource, NurtureCampaign,
)


# ======================================================== LeadSource
@pytest.mark.django_db
class TestLeadSource:
    def test_str_returns_name(self, leadsource_a):
        assert str(leadsource_a) == "Web Form A"

    def test_default_source_type_is_web_form(self, tenant_a):
        src = LeadSource.objects.create(tenant=tenant_a, name="Default Source")
        assert src.source_type == LeadSource.TYPE_WEB_FORM

    def test_default_routing_rule_is_round_robin(self, tenant_a):
        src = LeadSource.objects.create(tenant=tenant_a, name="RR Source")
        assert src.routing_rule == LeadSource.ROUTING_ROUND_ROBIN

    def test_default_status_is_active(self, tenant_a):
        src = LeadSource.objects.create(tenant=tenant_a, name="Active Source")
        assert src.status == LeadSource.STATUS_ACTIVE

    def test_default_cost_per_lead_is_zero(self, tenant_a):
        src = LeadSource.objects.create(tenant=tenant_a, name="Free Source")
        assert src.cost_per_lead == 0

    def test_type_choices_contain_all_seven(self):
        choices = dict(LeadSource.TYPE_CHOICES)
        assert LeadSource.TYPE_WEB_FORM in choices
        assert LeadSource.TYPE_LANDING_PAGE in choices
        assert LeadSource.TYPE_REFERRAL in choices
        assert LeadSource.TYPE_EVENT in choices
        assert LeadSource.TYPE_PAID_ADS in choices
        assert LeadSource.TYPE_COLD_OUTREACH in choices
        assert LeadSource.TYPE_PARTNER in choices

    def test_routing_choices_contain_all_four(self):
        choices = dict(LeadSource.ROUTING_CHOICES)
        assert LeadSource.ROUTING_ROUND_ROBIN in choices
        assert LeadSource.ROUTING_OWNER in choices
        assert LeadSource.ROUTING_TEAM in choices
        assert LeadSource.ROUTING_MANUAL in choices

    def test_status_choices_contain_all_three(self):
        choices = dict(LeadSource.STATUS_CHOICES)
        assert LeadSource.STATUS_ACTIVE in choices
        assert LeadSource.STATUS_PAUSED in choices
        assert LeadSource.STATUS_ARCHIVED in choices

    def test_ordering_is_by_name(self, tenant_a):
        LeadSource.objects.create(tenant=tenant_a, name="Zebra Source")
        LeadSource.objects.create(tenant=tenant_a, name="Apple Source")
        names = list(LeadSource.objects.filter(tenant=tenant_a).values_list("name", flat=True))
        assert names == sorted(names)


# ======================================================== NurtureCampaign
@pytest.mark.django_db
class TestNurtureCampaign:
    def test_str_returns_name(self, campaign_a):
        assert str(campaign_a) == "Campaign A"

    def test_default_channel_is_email(self, tenant_a):
        camp = NurtureCampaign.objects.create(tenant=tenant_a, name="Email Camp")
        assert camp.channel == NurtureCampaign.CHANNEL_EMAIL

    def test_default_status_is_draft(self, tenant_a):
        camp = NurtureCampaign.objects.create(tenant=tenant_a, name="Draft Camp")
        assert camp.status == NurtureCampaign.STATUS_DRAFT

    def test_default_step_count_is_one(self, tenant_a):
        camp = NurtureCampaign.objects.create(tenant=tenant_a, name="One Step Camp")
        assert camp.step_count == 1

    def test_default_cadence_days_is_three(self, tenant_a):
        camp = NurtureCampaign.objects.create(tenant=tenant_a, name="3-Day Camp")
        assert camp.cadence_days == 3

    def test_default_enrolled_count_is_zero(self, tenant_a):
        camp = NurtureCampaign.objects.create(tenant=tenant_a, name="Zero Enrolled")
        assert camp.enrolled_count == 0

    def test_channel_choices_contain_all_four(self):
        choices = dict(NurtureCampaign.CHANNEL_CHOICES)
        assert NurtureCampaign.CHANNEL_EMAIL in choices
        assert NurtureCampaign.CHANNEL_SMS in choices
        assert NurtureCampaign.CHANNEL_SOCIAL in choices
        assert NurtureCampaign.CHANNEL_MULTI in choices

    def test_status_choices_contain_all_five(self):
        choices = dict(NurtureCampaign.STATUS_CHOICES)
        assert NurtureCampaign.STATUS_DRAFT in choices
        assert NurtureCampaign.STATUS_SCHEDULED in choices
        assert NurtureCampaign.STATUS_RUNNING in choices
        assert NurtureCampaign.STATUS_PAUSED in choices
        assert NurtureCampaign.STATUS_COMPLETED in choices


# ======================================================== Lead
@pytest.mark.django_db
class TestLead:
    def test_auto_number_generated_on_save(self, tenant_a):
        lead = Lead.objects.create(tenant=tenant_a, first_name="Jane", last_name="Doe")
        assert lead.number.startswith("LEAD-")

    def test_auto_number_format_five_digits(self, tenant_a):
        lead = Lead.objects.create(tenant=tenant_a, first_name="Jane", last_name="Doe")
        parts = lead.number.split("-")
        assert len(parts) == 2
        assert len(parts[1]) == 5
        assert parts[1].isdigit()

    def test_auto_number_first_lead_is_LEAD_00001(self, tenant_a):
        lead = Lead.objects.create(tenant=tenant_a, first_name="First", last_name="Lead")
        assert lead.number == "LEAD-00001"

    def test_auto_number_increments_per_tenant(self, tenant_a):
        lead1 = Lead.objects.create(tenant=tenant_a, first_name="A", last_name="One")
        lead2 = Lead.objects.create(tenant=tenant_a, first_name="B", last_name="Two")
        assert lead1.number == "LEAD-00001"
        assert lead2.number == "LEAD-00002"

    def test_auto_number_isolated_per_tenant(self, tenant_a, tenant_b):
        lead_a = Lead.objects.create(tenant=tenant_a, first_name="A", last_name="One")
        lead_b = Lead.objects.create(tenant=tenant_b, first_name="B", last_name="Two")
        assert lead_a.number == "LEAD-00001"
        assert lead_b.number == "LEAD-00001"

    def test_str_includes_number_and_name(self, lead_a):
        result = str(lead_a)
        assert lead_a.number in result
        assert "Alice" in result
        assert "Smith" in result

    def test_str_without_number_shows_name_only(self, tenant_a):
        lead = Lead(tenant=tenant_a, first_name="No", last_name="Number")
        result = str(lead)
        assert "No Number" in result

    def test_full_name_property(self, lead_a):
        assert lead_a.full_name == "Alice Smith"

    def test_full_name_strips_whitespace(self, tenant_a):
        lead = Lead(tenant=tenant_a, first_name="Solo", last_name="")
        assert lead.full_name == "Solo"

    def test_default_status_is_new(self, tenant_a):
        lead = Lead.objects.create(tenant=tenant_a, first_name="New", last_name="Lead")
        assert lead.status == Lead.STATUS_NEW

    def test_default_rating_is_cold(self, tenant_a):
        lead = Lead.objects.create(tenant=tenant_a, first_name="Cold", last_name="Lead")
        assert lead.rating == Lead.RATING_COLD

    def test_default_estimated_value_is_zero(self, tenant_a):
        lead = Lead.objects.create(tenant=tenant_a, first_name="Zero", last_name="Value")
        assert lead.estimated_value == 0

    def test_status_choices_contain_all_seven(self):
        choices = dict(Lead.STATUS_CHOICES)
        for status in (Lead.STATUS_NEW, Lead.STATUS_CONTACTED, Lead.STATUS_WORKING,
                       Lead.STATUS_NURTURING, Lead.STATUS_QUALIFIED,
                       Lead.STATUS_UNQUALIFIED, Lead.STATUS_CONVERTED):
            assert status in choices

    def test_rating_choices_contain_all_three(self):
        choices = dict(Lead.RATING_CHOICES)
        assert Lead.RATING_HOT in choices
        assert Lead.RATING_WARM in choices
        assert Lead.RATING_COLD in choices

    def test_unique_together_tenant_number(self, tenant_a):
        Lead.objects.create(tenant=tenant_a, first_name="First", last_name="Lead")  # gets LEAD-00001
        import django.db.utils as db_utils
        with pytest.raises(db_utils.IntegrityError):
            Lead.objects.create(tenant=tenant_a, number="LEAD-00001",
                                first_name="Dup", last_name="Lead")

    def test_number_not_overwritten_if_already_set(self, tenant_a):
        lead = Lead.objects.create(
            tenant=tenant_a, number="LEAD-99999", first_name="Manual", last_name="Lead"
        )
        lead.first_name = "Updated"
        lead.save()
        lead.refresh_from_db()
        assert lead.number == "LEAD-99999"


# ======================================================== LeadScore
@pytest.mark.django_db
class TestLeadScore:
    def test_str_includes_name_score_and_grade(self, leadscore_a, lead_a):
        result = str(leadscore_a)
        assert "Alice Smith" in result
        assert "75" in result
        assert "B" in result

    def test_default_score_is_zero(self, tenant_a, lead_a):
        score = LeadScore.objects.create(tenant=tenant_a, lead=lead_a)
        assert score.score == 0

    def test_default_grade_is_c(self, tenant_a, lead_a):
        score = LeadScore.objects.create(tenant=tenant_a, lead=lead_a)
        assert score.grade == LeadScore.GRADE_C

    def test_default_scoring_model_is_rules(self, tenant_a, lead_a):
        score = LeadScore.objects.create(tenant=tenant_a, lead=lead_a)
        assert score.scoring_model == LeadScore.MODEL_RULES

    def test_default_demographic_points_is_zero(self, tenant_a, lead_a):
        score = LeadScore.objects.create(tenant=tenant_a, lead=lead_a)
        assert score.demographic_points == 0

    def test_default_behavioral_points_is_zero(self, tenant_a, lead_a):
        score = LeadScore.objects.create(tenant=tenant_a, lead=lead_a)
        assert score.behavioral_points == 0

    def test_grade_choices_contain_all_four(self):
        choices = dict(LeadScore.GRADE_CHOICES)
        assert LeadScore.GRADE_A in choices
        assert LeadScore.GRADE_B in choices
        assert LeadScore.GRADE_C in choices
        assert LeadScore.GRADE_D in choices

    def test_model_choices_contain_all_three(self):
        choices = dict(LeadScore.MODEL_CHOICES)
        assert LeadScore.MODEL_RULES in choices
        assert LeadScore.MODEL_PREDICTIVE in choices
        assert LeadScore.MODEL_MANUAL in choices


# ======================================================== LeadConversion
@pytest.mark.django_db
class TestLeadConversion:
    def test_auto_number_generated_on_save(self, tenant_a, lead_a):
        conv = LeadConversion.objects.create(tenant=tenant_a, lead=lead_a)
        assert conv.number.startswith("CNV-")

    def test_auto_number_format_five_digits(self, tenant_a, lead_a):
        conv = LeadConversion.objects.create(tenant=tenant_a, lead=lead_a)
        parts = conv.number.split("-")
        assert len(parts) == 2
        assert len(parts[1]) == 5
        assert parts[1].isdigit()

    def test_auto_number_first_conversion_is_CNV_00001(self, tenant_a, lead_a):
        conv = LeadConversion.objects.create(tenant=tenant_a, lead=lead_a)
        assert conv.number == "CNV-00001"

    def test_auto_number_increments_per_tenant(self, tenant_a, lead_a):
        conv1 = LeadConversion.objects.create(tenant=tenant_a, lead=lead_a)
        conv2 = LeadConversion.objects.create(tenant=tenant_a, lead=lead_a)
        assert conv1.number == "CNV-00001"
        assert conv2.number == "CNV-00002"

    def test_auto_number_isolated_per_tenant(self, tenant_a, tenant_b, lead_a, lead_b):
        conv_a = LeadConversion.objects.create(tenant=tenant_a, lead=lead_a)
        conv_b = LeadConversion.objects.create(tenant=tenant_b, lead=lead_b)
        assert conv_a.number == "CNV-00001"
        assert conv_b.number == "CNV-00001"

    def test_str_returns_number(self, leadconversion_a):
        result = str(leadconversion_a)
        assert leadconversion_a.number in result

    def test_str_fallback_when_no_number(self, tenant_a, lead_a):
        conv = LeadConversion(tenant=tenant_a, lead=lead_a)
        result = str(conv)
        assert result is not None

    def test_unique_together_tenant_number(self, tenant_a, lead_a):
        LeadConversion.objects.create(tenant=tenant_a, lead=lead_a)  # gets CNV-00001
        import django.db.utils as db_utils
        with pytest.raises(db_utils.IntegrityError):
            LeadConversion.objects.create(tenant=tenant_a, lead=lead_a, number="CNV-00001")

    def test_default_status_is_pending(self, tenant_a, lead_a):
        conv = LeadConversion.objects.create(tenant=tenant_a, lead=lead_a)
        assert conv.status == LeadConversion.STATUS_PENDING

    def test_default_outcome_is_opportunity(self, tenant_a, lead_a):
        conv = LeadConversion.objects.create(tenant=tenant_a, lead=lead_a)
        assert conv.outcome == LeadConversion.OUTCOME_OPPORTUNITY

    def test_default_deal_value_is_zero(self, tenant_a, lead_a):
        conv = LeadConversion.objects.create(tenant=tenant_a, lead=lead_a)
        assert conv.deal_value == 0

    def test_converted_at_set_when_accepted(self, tenant_a, lead_a):
        conv = LeadConversion.objects.create(tenant=tenant_a, lead=lead_a)
        assert conv.converted_at is None
        conv.status = LeadConversion.STATUS_ACCEPTED
        conv.save()
        assert conv.converted_at is not None

    def test_converted_at_set_when_completed(self, tenant_a, lead_a):
        conv = LeadConversion.objects.create(tenant=tenant_a, lead=lead_a)
        conv.status = LeadConversion.STATUS_COMPLETED
        conv.save()
        assert conv.converted_at is not None

    def test_converted_at_not_set_when_rejected(self, tenant_a, lead_a):
        conv = LeadConversion.objects.create(tenant=tenant_a, lead=lead_a)
        conv.status = LeadConversion.STATUS_REJECTED
        conv.save()
        assert conv.converted_at is None

    def test_status_choices_contain_all_four(self):
        choices = dict(LeadConversion.STATUS_CHOICES)
        assert LeadConversion.STATUS_PENDING in choices
        assert LeadConversion.STATUS_ACCEPTED in choices
        assert LeadConversion.STATUS_REJECTED in choices
        assert LeadConversion.STATUS_COMPLETED in choices

    def test_outcome_choices_contain_all_four(self):
        choices = dict(LeadConversion.OUTCOME_CHOICES)
        assert LeadConversion.OUTCOME_OPPORTUNITY in choices
        assert LeadConversion.OUTCOME_ACCOUNT in choices
        assert LeadConversion.OUTCOME_CONTACT in choices
        assert LeadConversion.OUTCOME_DISQUALIFIED in choices
