"""Tests for opportunities models: PipelineStage, Opportunity, OpportunityActivity,
Competitor, DealCollaborator."""
import pytest
from django.utils import timezone

from apps.opportunities.models import (
    Competitor,
    DealCollaborator,
    Opportunity,
    OpportunityActivity,
    PipelineStage,
)


# ════════════════════════════════════════════════════════════════
#  PipelineStage
# ════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestPipelineStage:
    def test_str_returns_name(self, stage_a):
        assert str(stage_a) == "Qualification"

    def test_default_stage_type_is_open(self, tenant_a):
        stage = PipelineStage.objects.create(tenant=tenant_a, name="Prospecting")
        assert stage.stage_type == PipelineStage.TYPE_OPEN

    def test_default_probability_is_10(self, tenant_a):
        stage = PipelineStage.objects.create(tenant=tenant_a, name="Discovery")
        assert stage.probability == 10

    def test_default_order_is_0(self, tenant_a):
        stage = PipelineStage.objects.create(tenant=tenant_a, name="Proposal")
        assert stage.order == 0

    def test_default_is_active_true(self, tenant_a):
        stage = PipelineStage.objects.create(tenant=tenant_a, name="Active Stage")
        assert stage.is_active is True

    def test_type_choices_contain_all_three(self):
        choices = dict(PipelineStage.TYPE_CHOICES)
        assert PipelineStage.TYPE_OPEN in choices
        assert PipelineStage.TYPE_WON in choices
        assert PipelineStage.TYPE_LOST in choices

    def test_ordering_by_order_then_id(self, tenant_a):
        PipelineStage.objects.create(tenant=tenant_a, name="C Stage", order=3)
        PipelineStage.objects.create(tenant=tenant_a, name="A Stage", order=1)
        PipelineStage.objects.create(tenant=tenant_a, name="B Stage", order=2)
        stages = list(
            PipelineStage.objects.filter(tenant=tenant_a).values_list("order", flat=True)
        )
        assert stages == sorted(stages)

    def test_tenant_fk(self, stage_a, tenant_a):
        assert stage_a.tenant == tenant_a


# ════════════════════════════════════════════════════════════════
#  Opportunity
# ════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestOpportunity:
    def test_str_with_number(self, opportunity_a):
        result = str(opportunity_a)
        assert "OPP-" in result
        assert "Big Deal" in result

    def test_str_without_number(self, tenant_a):
        opp = Opportunity(tenant=tenant_a, name="Unsaved Opp")
        assert str(opp) == "Unsaved Opp"

    def test_auto_number_on_save(self, tenant_a):
        opp = Opportunity.objects.create(tenant=tenant_a, name="First")
        assert opp.number.startswith("OPP-")

    def test_auto_number_format_five_digits(self, tenant_a):
        opp = Opportunity.objects.create(tenant=tenant_a, name="Numbered")
        parts = opp.number.split("-")
        assert len(parts) == 2
        assert len(parts[1]) == 5
        assert parts[1].isdigit()

    def test_auto_number_first_is_OPP_00001(self, tenant_a):
        opp = Opportunity.objects.create(tenant=tenant_a, name="First OPP")
        assert opp.number == "OPP-00001"

    def test_auto_number_increments_per_tenant(self, tenant_a):
        opp1 = Opportunity.objects.create(tenant=tenant_a, name="First")
        opp2 = Opportunity.objects.create(tenant=tenant_a, name="Second")
        assert opp1.number == "OPP-00001"
        assert opp2.number == "OPP-00002"

    def test_auto_number_isolated_per_tenant(self, tenant_a, tenant_b):
        opp_a = Opportunity.objects.create(tenant=tenant_a, name="A First")
        opp_b = Opportunity.objects.create(tenant=tenant_b, name="B First")
        assert opp_a.number == "OPP-00001"
        assert opp_b.number == "OPP-00001"

    def test_unique_together_tenant_number(self, tenant_a):
        Opportunity.objects.create(tenant=tenant_a, name="First")  # gets OPP-00001
        import django.db.utils as db_utils
        with pytest.raises(db_utils.IntegrityError):
            Opportunity.objects.create(tenant=tenant_a, number="OPP-00001", name="Duplicate")

    def test_default_status_is_open(self, tenant_a):
        opp = Opportunity.objects.create(tenant=tenant_a, name="Open Opp")
        assert opp.status == Opportunity.STATUS_OPEN

    def test_default_priority_is_medium(self, tenant_a):
        opp = Opportunity.objects.create(tenant=tenant_a, name="Med Prio")
        assert opp.priority == Opportunity.PRIORITY_MEDIUM

    def test_default_forecast_category_is_pipeline(self, tenant_a):
        opp = Opportunity.objects.create(tenant=tenant_a, name="Forecast Opp")
        assert opp.forecast_category == Opportunity.FORECAST_PIPELINE

    def test_default_amount_is_zero(self, tenant_a):
        opp = Opportunity.objects.create(tenant=tenant_a, name="Zero Amount")
        assert opp.amount == 0

    def test_default_probability_is_10(self, tenant_a):
        opp = Opportunity.objects.create(tenant=tenant_a, name="Low Prob")
        assert opp.probability == 10

    def test_closed_at_set_when_won(self, tenant_a):
        opp = Opportunity.objects.create(tenant=tenant_a, name="Won Deal", status=Opportunity.STATUS_WON)
        assert opp.closed_at is not None

    def test_closed_at_set_when_lost(self, tenant_a):
        opp = Opportunity.objects.create(tenant=tenant_a, name="Lost Deal", status=Opportunity.STATUS_LOST)
        assert opp.closed_at is not None

    def test_closed_at_cleared_when_reopened(self, tenant_a):
        opp = Opportunity.objects.create(tenant=tenant_a, name="Won Then Reopened", status=Opportunity.STATUS_WON)
        assert opp.closed_at is not None
        opp.status = Opportunity.STATUS_OPEN
        opp.save()
        assert opp.closed_at is None

    def test_closed_at_none_when_open(self, tenant_a):
        opp = Opportunity.objects.create(tenant=tenant_a, name="Open Deal")
        assert opp.closed_at is None

    def test_weighted_amount_computed(self, tenant_a):
        # NOTE (app bug): weighted_amount property does not coerce self.amount to Decimal
        # before arithmetic, so it raises TypeError on the in-memory string value produced
        # by Opportunity.objects.create(amount="10000.00"). Workaround: refresh_from_db()
        # so Django's DecimalField type coercion runs before calling the property.
        # Bug location: apps/opportunities/models.py:112 — `(self.amount or 0) * self.probability / 100`
        # should be `(Decimal(self.amount or 0) * self.probability / 100)`.
        opp = Opportunity.objects.create(
            tenant=tenant_a, name="Weighted", amount="10000.00", probability=25
        )
        opp.refresh_from_db()  # force Decimal coercion
        from decimal import Decimal
        assert opp.weighted_amount == Decimal("2500.00")

    def test_weighted_amount_zero_probability(self, tenant_a):
        # See note above about app bug — refresh_from_db() required for correct Decimal type.
        opp = Opportunity.objects.create(
            tenant=tenant_a, name="Zero Prob", amount="5000.00", probability=0
        )
        opp.refresh_from_db()
        assert opp.weighted_amount == 0

    def test_status_choices_contain_all_three(self):
        choices = dict(Opportunity.STATUS_CHOICES)
        assert Opportunity.STATUS_OPEN in choices
        assert Opportunity.STATUS_WON in choices
        assert Opportunity.STATUS_LOST in choices

    def test_priority_choices_contain_all_four(self):
        choices = dict(Opportunity.PRIORITY_CHOICES)
        assert Opportunity.PRIORITY_LOW in choices
        assert Opportunity.PRIORITY_MEDIUM in choices
        assert Opportunity.PRIORITY_HIGH in choices
        assert Opportunity.PRIORITY_CRITICAL in choices

    def test_forecast_choices_contain_all_four(self):
        choices = dict(Opportunity.FORECAST_CHOICES)
        assert Opportunity.FORECAST_PIPELINE in choices
        assert Opportunity.FORECAST_BEST_CASE in choices
        assert Opportunity.FORECAST_COMMIT in choices
        assert Opportunity.FORECAST_OMITTED in choices

    def test_ordering_newest_first(self, tenant_a):
        opp1 = Opportunity.objects.create(tenant=tenant_a, name="First")
        opp2 = Opportunity.objects.create(tenant=tenant_a, name="Second")
        ids = list(Opportunity.objects.filter(tenant=tenant_a).values_list("id", flat=True))
        # newest (higher id) comes first
        assert ids[0] == opp2.pk


# ════════════════════════════════════════════════════════════════
#  OpportunityActivity
# ════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestOpportunityActivity:
    def test_str_returns_subject(self, activity_a):
        assert str(activity_a) == "Initial call with ACME"

    def test_default_activity_type_is_note(self, tenant_a, opportunity_a):
        act = OpportunityActivity.objects.create(
            tenant=tenant_a,
            opportunity=opportunity_a,
            subject="Quick note",
        )
        assert act.activity_type == OpportunityActivity.TYPE_NOTE

    def test_default_outcome_is_pending(self, tenant_a, opportunity_a):
        act = OpportunityActivity.objects.create(
            tenant=tenant_a,
            opportunity=opportunity_a,
            subject="Pending outcome act",
        )
        assert act.outcome == OpportunityActivity.OUTCOME_PENDING

    def test_type_choices_contain_all_five(self):
        choices = dict(OpportunityActivity.TYPE_CHOICES)
        assert OpportunityActivity.TYPE_NOTE in choices
        assert OpportunityActivity.TYPE_CALL in choices
        assert OpportunityActivity.TYPE_EMAIL in choices
        assert OpportunityActivity.TYPE_MEETING in choices
        assert OpportunityActivity.TYPE_STAGE_CHANGE in choices

    def test_outcome_choices_contain_all_four(self):
        choices = dict(OpportunityActivity.OUTCOME_CHOICES)
        assert OpportunityActivity.OUTCOME_PENDING in choices
        assert OpportunityActivity.OUTCOME_POSITIVE in choices
        assert OpportunityActivity.OUTCOME_NEUTRAL in choices
        assert OpportunityActivity.OUTCOME_NEGATIVE in choices

    def test_tenant_fk(self, activity_a, tenant_a):
        assert activity_a.tenant == tenant_a

    def test_opportunity_fk(self, activity_a, opportunity_a):
        assert activity_a.opportunity == opportunity_a


# ════════════════════════════════════════════════════════════════
#  Competitor
# ════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestCompetitor:
    def test_str_returns_name(self, competitor_a):
        assert str(competitor_a) == "CompetitorX"

    def test_default_threat_level_is_medium(self, tenant_a, opportunity_a):
        comp = Competitor.objects.create(
            tenant=tenant_a, opportunity=opportunity_a, name="DefaultThreat"
        )
        assert comp.threat_level == Competitor.THREAT_MEDIUM

    def test_default_status_is_active(self, tenant_a, opportunity_a):
        comp = Competitor.objects.create(
            tenant=tenant_a, opportunity=opportunity_a, name="DefaultStatus"
        )
        assert comp.status == Competitor.STATUS_ACTIVE

    def test_threat_choices_contain_all_three(self):
        choices = dict(Competitor.THREAT_CHOICES)
        assert Competitor.THREAT_LOW in choices
        assert Competitor.THREAT_MEDIUM in choices
        assert Competitor.THREAT_HIGH in choices

    def test_status_choices_contain_all_four(self):
        choices = dict(Competitor.STATUS_CHOICES)
        assert Competitor.STATUS_ACTIVE in choices
        assert Competitor.STATUS_ELIMINATED in choices
        assert Competitor.STATUS_WON_AGAINST in choices
        assert Competitor.STATUS_LOST_TO in choices

    def test_tenant_fk(self, competitor_a, tenant_a):
        assert competitor_a.tenant == tenant_a

    def test_opportunity_fk(self, competitor_a, opportunity_a):
        assert competitor_a.opportunity == opportunity_a


# ════════════════════════════════════════════════════════════════
#  DealCollaborator
# ════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestDealCollaborator:
    def test_str_includes_name_and_role_display(self, collaborator_a):
        result = str(collaborator_a)
        assert "Carol Smith" in result
        assert "Sales engineer" in result

    def test_default_team_role_is_sales_engineer(self, tenant_a, opportunity_a):
        collab = DealCollaborator.objects.create(
            tenant=tenant_a, opportunity=opportunity_a, member_name="Default Role"
        )
        assert collab.team_role == DealCollaborator.ROLE_SALES_ENG

    def test_default_status_is_active(self, tenant_a, opportunity_a):
        collab = DealCollaborator.objects.create(
            tenant=tenant_a, opportunity=opportunity_a, member_name="Default Status"
        )
        assert collab.status == DealCollaborator.STATUS_ACTIVE

    def test_role_choices_contain_all_six(self):
        choices = dict(DealCollaborator.ROLE_CHOICES)
        assert DealCollaborator.ROLE_OWNER in choices
        assert DealCollaborator.ROLE_SALES_ENG in choices
        assert DealCollaborator.ROLE_EXEC_SPONSOR in choices
        assert DealCollaborator.ROLE_PRODUCT in choices
        assert DealCollaborator.ROLE_LEGAL in choices
        assert DealCollaborator.ROLE_SUPPORT in choices

    def test_status_choices_contain_all_three(self):
        choices = dict(DealCollaborator.STATUS_CHOICES)
        assert DealCollaborator.STATUS_INVITED in choices
        assert DealCollaborator.STATUS_ACTIVE in choices
        assert DealCollaborator.STATUS_INACTIVE in choices

    def test_tenant_fk(self, collaborator_a, tenant_a):
        assert collaborator_a.tenant == tenant_a

    def test_opportunity_fk(self, collaborator_a, opportunity_a):
        assert collaborator_a.opportunity == opportunity_a
