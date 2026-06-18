"""Tests for crm.models: AccountTier, Account, Contact, RelationshipMap, AccountPlan."""
import pytest
from django.utils import timezone

from apps.crm.models import Account, AccountPlan, AccountTier, Contact, RelationshipMap


# ============================================================ AccountTier
@pytest.mark.django_db
class TestAccountTierModel:
    def test_str_returns_name(self, tier_a):
        assert str(tier_a) == "Strategic"

    def test_default_segment_is_midmarket(self, tenant_a):
        t = AccountTier.objects.create(tenant=tenant_a, name="Default Tier")
        assert t.segment == AccountTier.SEGMENT_MIDMARKET

    def test_default_rank_is_zero(self, tenant_a):
        t = AccountTier.objects.create(tenant=tenant_a, name="Rank Zero")
        assert t.rank == 0

    def test_default_is_active_true(self, tenant_a):
        t = AccountTier.objects.create(tenant=tenant_a, name="Active Tier")
        assert t.is_active is True

    def test_segment_choices_contain_all_five(self):
        choices = dict(AccountTier.SEGMENT_CHOICES)
        assert AccountTier.SEGMENT_STRATEGIC in choices
        assert AccountTier.SEGMENT_ENTERPRISE in choices
        assert AccountTier.SEGMENT_MIDMARKET in choices
        assert AccountTier.SEGMENT_SMB in choices
        assert AccountTier.SEGMENT_STARTUP in choices

    def test_ordering_by_rank_then_name(self, tenant_a):
        AccountTier.objects.create(tenant=tenant_a, name="B Tier", rank=2)
        AccountTier.objects.create(tenant=tenant_a, name="A Tier", rank=1)
        tiers = list(AccountTier.objects.filter(tenant=tenant_a).values_list("rank", flat=True))
        assert tiers == sorted(tiers)

    def test_created_at_auto_set(self, tier_a):
        assert tier_a.created_at is not None

    def test_updated_at_auto_set(self, tier_a):
        assert tier_a.updated_at is not None


# ============================================================ Account
@pytest.mark.django_db
class TestAccountModel:
    def test_str_returns_name(self, account_a):
        assert str(account_a) == "Acme Corp"

    def test_auto_number_generated_on_save(self, tenant_a):
        acc = Account.objects.create(tenant=tenant_a, name="New Account")
        assert acc.number.startswith("ACC-")

    def test_auto_number_format_five_digits(self, tenant_a):
        acc = Account.objects.create(tenant=tenant_a, name="Format Test")
        parts = acc.number.split("-")
        assert len(parts) == 2
        assert len(parts[1]) == 5
        assert parts[1].isdigit()

    def test_auto_number_first_account_is_ACC_00001(self, tenant_a):
        acc = Account.objects.create(tenant=tenant_a, name="First Account")
        assert acc.number == "ACC-00001"

    def test_auto_number_increments_per_tenant(self, tenant_a):
        acc1 = Account.objects.create(tenant=tenant_a, name="Acct 1")
        acc2 = Account.objects.create(tenant=tenant_a, name="Acct 2")
        assert acc1.number == "ACC-00001"
        assert acc2.number == "ACC-00002"

    def test_auto_number_isolated_per_tenant(self, tenant_a, tenant_b):
        acc_a = Account.objects.create(tenant=tenant_a, name="A Corp")
        acc_b = Account.objects.create(tenant=tenant_b, name="B Corp")
        assert acc_a.number == "ACC-00001"
        assert acc_b.number == "ACC-00001"

    def test_unique_together_tenant_number(self, tenant_a):
        Account.objects.create(tenant=tenant_a, name="Unique Test")  # gets ACC-00001
        import django.db.utils as db_utils
        with pytest.raises(db_utils.IntegrityError):
            Account.objects.create(tenant=tenant_a, name="Dupe Num", number="ACC-00001")

    def test_default_account_type_is_prospect(self, tenant_a):
        acc = Account.objects.create(tenant=tenant_a, name="Default Type")
        assert acc.account_type == Account.TYPE_PROSPECT

    def test_default_status_is_active(self, tenant_a):
        acc = Account.objects.create(tenant=tenant_a, name="Default Status")
        assert acc.status == Account.STATUS_ACTIVE

    def test_type_choices_contain_all_five(self):
        choices = dict(Account.TYPE_CHOICES)
        assert Account.TYPE_PROSPECT in choices
        assert Account.TYPE_CUSTOMER in choices
        assert Account.TYPE_PARTNER in choices
        assert Account.TYPE_RESELLER in choices
        assert Account.TYPE_COMPETITOR in choices

    def test_status_choices_contain_all_three(self):
        choices = dict(Account.STATUS_CHOICES)
        assert Account.STATUS_ACTIVE in choices
        assert Account.STATUS_INACTIVE in choices
        assert Account.STATUS_CHURNED in choices

    def test_parent_child_relationship(self, tenant_a):
        parent = Account.objects.create(tenant=tenant_a, name="Parent Corp")
        child = Account.objects.create(tenant=tenant_a, name="Child Corp", parent=parent)
        assert child.parent == parent
        assert child in parent.children.all()

    def test_tier_relationship(self, account_a, tier_a):
        assert account_a.tier == tier_a
        assert account_a in tier_a.accounts.all()

    def test_number_not_overwritten_on_resave(self, account_a):
        original_number = account_a.number
        account_a.industry = "Technology"
        account_a.save()
        account_a.refresh_from_db()
        assert account_a.number == original_number


# ============================================================ Contact
@pytest.mark.django_db
class TestContactModel:
    def test_str_returns_full_name(self, contact_a):
        assert str(contact_a) == "Alice Smith"

    def test_full_name_property(self, contact_a):
        assert contact_a.full_name == "Alice Smith"

    def test_full_name_strips_whitespace(self, tenant_a):
        c = Contact.objects.create(tenant=tenant_a, first_name="Bob", last_name="")
        assert c.full_name == "Bob"

    def test_default_status_is_active(self, tenant_a):
        c = Contact.objects.create(tenant=tenant_a, first_name="Test", last_name="User")
        assert c.status == Contact.STATUS_ACTIVE

    def test_default_enrichment_status_is_none(self, tenant_a):
        c = Contact.objects.create(tenant=tenant_a, first_name="Test", last_name="User")
        assert c.enrichment_status == Contact.ENRICH_NONE

    def test_default_is_primary_is_false(self, tenant_a):
        c = Contact.objects.create(tenant=tenant_a, first_name="Test", last_name="User")
        assert c.is_primary is False

    def test_status_choices_contain_all_three(self):
        choices = dict(Contact.STATUS_CHOICES)
        assert Contact.STATUS_ACTIVE in choices
        assert Contact.STATUS_INACTIVE in choices
        assert Contact.STATUS_BOUNCED in choices

    def test_enrich_choices_contain_all_three(self):
        choices = dict(Contact.ENRICH_CHOICES)
        assert Contact.ENRICH_NONE in choices
        assert Contact.ENRICH_PARTIAL in choices
        assert Contact.ENRICH_VERIFIED in choices

    def test_contact_links_to_account(self, contact_a, account_a):
        assert contact_a.account == account_a
        assert contact_a in account_a.contacts.all()

    def test_ordering_by_last_name_first_name(self, tenant_a, account_a):
        Contact.objects.create(tenant=tenant_a, first_name="Zara", last_name="Brown")
        Contact.objects.create(tenant=tenant_a, first_name="Alice", last_name="Adams")
        contacts = list(
            Contact.objects.filter(tenant=tenant_a).values_list("last_name", flat=True)
        )
        assert contacts == sorted(contacts)


# ============================================================ RelationshipMap
@pytest.mark.django_db
class TestRelationshipMapModel:
    def test_str_includes_arrow_and_type(self, relmap_a):
        result = str(relmap_a)
        assert "→" in result
        assert "Reports to" in result

    def test_default_relationship_type_is_reports_to(self, tenant_a, contact_a, contact_a2):
        rm = RelationshipMap.objects.create(
            tenant=tenant_a, from_contact=contact_a, to_contact=contact_a2
        )
        assert rm.relationship_type == RelationshipMap.TYPE_REPORTS_TO

    def test_default_strength_is_moderate(self, tenant_a, contact_a, contact_a2):
        rm = RelationshipMap.objects.create(
            tenant=tenant_a, from_contact=contact_a, to_contact=contact_a2
        )
        assert rm.strength == RelationshipMap.STRENGTH_MODERATE

    def test_type_choices_contain_all_five(self):
        choices = dict(RelationshipMap.TYPE_CHOICES)
        assert RelationshipMap.TYPE_REPORTS_TO in choices
        assert RelationshipMap.TYPE_INFLUENCES in choices
        assert RelationshipMap.TYPE_SPONSOR in choices
        assert RelationshipMap.TYPE_BLOCKER in choices
        assert RelationshipMap.TYPE_PEER in choices

    def test_strength_choices_contain_all_three(self):
        choices = dict(RelationshipMap.STRENGTH_CHOICES)
        assert RelationshipMap.STRENGTH_STRONG in choices
        assert RelationshipMap.STRENGTH_MODERATE in choices
        assert RelationshipMap.STRENGTH_WEAK in choices

    def test_ordering_is_newest_first(self, tenant_a, contact_a, contact_a2):
        rm1 = RelationshipMap.objects.create(
            tenant=tenant_a, from_contact=contact_a, to_contact=contact_a2,
            relationship_type=RelationshipMap.TYPE_PEER,
        )
        rm2 = RelationshipMap.objects.create(
            tenant=tenant_a, from_contact=contact_a2, to_contact=contact_a,
            relationship_type=RelationshipMap.TYPE_INFLUENCES,
        )
        pks = list(RelationshipMap.objects.filter(tenant=tenant_a).values_list("pk", flat=True))
        assert pks[0] == rm2.pk  # most recent first

    def test_from_contact_to_contact_links(self, relmap_a, contact_a, contact_a2):
        assert relmap_a.from_contact == contact_a
        assert relmap_a.to_contact == contact_a2


# ============================================================ AccountPlan
@pytest.mark.django_db
class TestAccountPlanModel:
    def test_str_returns_number_when_set(self, plan_a):
        assert str(plan_a) == plan_a.number

    def test_str_falls_back_to_title_when_no_number(self, tenant_a, account_a):
        plan = AccountPlan(tenant=tenant_a, account=account_a, title="Fallback Title")
        assert str(plan) == "Fallback Title"

    def test_auto_number_generated_on_save(self, plan_a):
        assert plan_a.number.startswith("PLAN-")

    def test_auto_number_format_five_digits(self, tenant_a, account_a):
        plan = AccountPlan.objects.create(
            tenant=tenant_a, account=account_a, title="Format Check"
        )
        parts = plan.number.split("-")
        assert len(parts) == 2
        assert len(parts[1]) == 5
        assert parts[1].isdigit()

    def test_auto_number_first_plan_is_PLAN_00001(self, tenant_a, account_a):
        plan = AccountPlan.objects.create(
            tenant=tenant_a, account=account_a, title="First Plan"
        )
        assert plan.number == "PLAN-00001"

    def test_auto_number_increments_per_tenant(self, tenant_a, account_a):
        p1 = AccountPlan.objects.create(tenant=tenant_a, account=account_a, title="Plan 1")
        p2 = AccountPlan.objects.create(tenant=tenant_a, account=account_a, title="Plan 2")
        assert p1.number == "PLAN-00001"
        assert p2.number == "PLAN-00002"

    def test_auto_number_isolated_per_tenant(self, tenant_a, tenant_b, account_a, account_b):
        p_a = AccountPlan.objects.create(tenant=tenant_a, account=account_a, title="Plan A")
        p_b = AccountPlan.objects.create(tenant=tenant_b, account=account_b, title="Plan B")
        assert p_a.number == "PLAN-00001"
        assert p_b.number == "PLAN-00001"

    def test_unique_together_tenant_number(self, tenant_a, account_a):
        AccountPlan.objects.create(tenant=tenant_a, account=account_a, title="First")
        import django.db.utils as db_utils
        with pytest.raises(db_utils.IntegrityError):
            AccountPlan.objects.create(
                tenant=tenant_a, account=account_a,
                title="Dupe", number="PLAN-00001"
            )

    def test_default_status_is_draft(self, tenant_a, account_a):
        plan = AccountPlan.objects.create(tenant=tenant_a, account=account_a, title="Draft Plan")
        assert plan.status == AccountPlan.STATUS_DRAFT

    def test_default_priority_is_medium(self, tenant_a, account_a):
        plan = AccountPlan.objects.create(tenant=tenant_a, account=account_a, title="Priority Plan")
        assert plan.priority == AccountPlan.PRIORITY_MEDIUM

    def test_status_choices_contain_all_five(self):
        choices = dict(AccountPlan.STATUS_CHOICES)
        assert AccountPlan.STATUS_DRAFT in choices
        assert AccountPlan.STATUS_ACTIVE in choices
        assert AccountPlan.STATUS_ON_TRACK in choices
        assert AccountPlan.STATUS_AT_RISK in choices
        assert AccountPlan.STATUS_COMPLETED in choices

    def test_priority_choices_contain_all_three(self):
        choices = dict(AccountPlan.PRIORITY_CHOICES)
        assert AccountPlan.PRIORITY_LOW in choices
        assert AccountPlan.PRIORITY_MEDIUM in choices
        assert AccountPlan.PRIORITY_HIGH in choices

    def test_approved_at_set_when_status_active(self, plan_a):
        plan_a.status = AccountPlan.STATUS_ACTIVE
        plan_a.save()
        plan_a.refresh_from_db()
        assert plan_a.approved_at is not None

    def test_approved_at_set_when_status_on_track(self, plan_a):
        plan_a.status = AccountPlan.STATUS_ON_TRACK
        plan_a.save()
        plan_a.refresh_from_db()
        assert plan_a.approved_at is not None

    def test_approved_at_set_when_status_completed(self, plan_a):
        plan_a.status = AccountPlan.STATUS_COMPLETED
        plan_a.save()
        plan_a.refresh_from_db()
        assert plan_a.approved_at is not None

    def test_approved_at_not_set_for_draft(self, tenant_a, account_a):
        plan = AccountPlan.objects.create(
            tenant=tenant_a, account=account_a, title="Draft Only",
            status=AccountPlan.STATUS_DRAFT
        )
        assert plan.approved_at is None

    def test_approved_at_not_set_for_at_risk(self, tenant_a, account_a):
        plan = AccountPlan.objects.create(
            tenant=tenant_a, account=account_a, title="At Risk Plan",
            status=AccountPlan.STATUS_AT_RISK
        )
        assert plan.approved_at is None

    def test_approved_at_not_overwritten_on_resave(self, tenant_a, account_a):
        plan = AccountPlan.objects.create(
            tenant=tenant_a, account=account_a, title="Approved Plan",
            status=AccountPlan.STATUS_ACTIVE
        )
        original_approved_at = plan.approved_at
        plan.priority = AccountPlan.PRIORITY_HIGH
        plan.save()
        plan.refresh_from_db()
        assert plan.approved_at == original_approved_at

    def test_fiscal_year_defaults_to_current_year(self, tenant_a, account_a):
        plan = AccountPlan.objects.create(tenant=tenant_a, account=account_a, title="FY Plan")
        assert plan.fiscal_year == timezone.localdate().year

    def test_number_not_overwritten_on_resave(self, plan_a):
        original_number = plan_a.number
        plan_a.title = "Updated Title"
        plan_a.save()
        plan_a.refresh_from_db()
        assert plan_a.number == original_number
