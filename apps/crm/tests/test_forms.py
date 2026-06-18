"""Tests for crm.forms: field exclusions and tenant-scoped FK querysets."""
import pytest

from apps.crm.forms import AccountForm, AccountPlanForm, AccountTierForm, ContactForm, RelationshipMapForm
from apps.crm.models import Account, AccountPlan, AccountTier, Contact


# ============================================================ AccountTierForm
@pytest.mark.django_db
class TestAccountTierForm:
    def test_valid_form(self):
        form = AccountTierForm(data={
            "name": "Enterprise Tier",
            "segment": "enterprise",
            "rank": 1,
            "min_annual_value": "100000.00",
            "color": "#2563eb",
            "description": "Top enterprise clients",
            "is_active": True,
        })
        assert form.is_valid(), form.errors

    def test_tenant_not_in_form_fields(self):
        form = AccountTierForm()
        assert "tenant" not in form.fields

    def test_created_at_not_in_form_fields(self):
        form = AccountTierForm()
        assert "created_at" not in form.fields

    def test_updated_at_not_in_form_fields(self):
        form = AccountTierForm()
        assert "updated_at" not in form.fields

    def test_missing_name_invalid(self):
        form = AccountTierForm(data={"segment": "enterprise", "rank": 1})
        assert not form.is_valid()
        assert "name" in form.errors

    def test_invalid_segment_choice_invalid(self):
        form = AccountTierForm(data={"name": "Test", "segment": "invalid_segment", "rank": 0})
        assert not form.is_valid()


# ============================================================ AccountForm
@pytest.mark.django_db
class TestAccountForm:
    def test_valid_form_minimal(self, tenant_a):
        form = AccountForm(data={
            "name": "Test Corp",
            "account_type": "prospect",
            "status": "active",
            "industry": "",
            "website": "",
            "phone": "",
            "billing_city": "",
            "billing_country": "",
            "employee_count": "",
            "annual_revenue": "0",
            "description": "",
            "parent": "",
            "tier": "",
        }, tenant=tenant_a)
        assert form.is_valid(), form.errors

    def test_number_not_in_form_fields(self, tenant_a):
        """number is auto-generated and must not appear in the form."""
        form = AccountForm(tenant=tenant_a)
        assert "number" not in form.fields

    def test_tenant_not_in_form_fields(self, tenant_a):
        form = AccountForm(tenant=tenant_a)
        assert "tenant" not in form.fields

    def test_created_at_not_in_form_fields(self, tenant_a):
        form = AccountForm(tenant=tenant_a)
        assert "created_at" not in form.fields

    def test_missing_name_invalid(self, tenant_a):
        form = AccountForm(data={"account_type": "prospect", "status": "active"}, tenant=tenant_a)
        assert not form.is_valid()
        assert "name" in form.errors

    def test_parent_queryset_scoped_to_tenant(self, tenant_a, tenant_b, account_a, account_b):
        """Parent accounts must only show the requesting tenant's accounts."""
        form = AccountForm(tenant=tenant_a)
        parent_pks = [a.pk for a in form.fields["parent"].queryset]
        assert account_a.pk in parent_pks
        assert account_b.pk not in parent_pks

    def test_tier_queryset_scoped_to_tenant(self, tenant_a, tenant_b, tier_a, tier_b):
        """Tier dropdown must only show the requesting tenant's tiers."""
        form = AccountForm(tenant=tenant_a)
        tier_pks = [t.pk for t in form.fields["tier"].queryset]
        assert tier_a.pk in tier_pks
        assert tier_b.pk not in tier_pks

    def test_no_tenant_gives_empty_parent_queryset(self):
        form = AccountForm(tenant=None)
        assert form.fields["parent"].queryset.count() == 0

    def test_no_tenant_gives_empty_tier_queryset(self):
        form = AccountForm(tenant=None)
        assert form.fields["tier"].queryset.count() == 0

    def test_account_excluded_from_own_parent_on_edit(self, tenant_a, account_a):
        """An account cannot be its own parent."""
        form = AccountForm(instance=account_a, tenant=tenant_a)
        parent_pks = [a.pk for a in form.fields["parent"].queryset]
        assert account_a.pk not in parent_pks


# ============================================================ ContactForm
@pytest.mark.django_db
class TestContactForm:
    def test_valid_form(self, tenant_a, account_a):
        form = ContactForm(data={
            "first_name": "Jane",
            "last_name": "Doe",
            "account": account_a.pk,
            "title": "VP Sales",
            "department": "Sales",
            "email": "jane@example.com",
            "phone": "",
            "mobile": "",
            "linkedin_url": "",
            "status": "active",
            "enrichment_status": "none",
            "is_primary": False,
            "notes": "",
        }, tenant=tenant_a)
        assert form.is_valid(), form.errors

    def test_tenant_not_in_form_fields(self, tenant_a):
        form = ContactForm(tenant=tenant_a)
        assert "tenant" not in form.fields

    def test_created_at_not_in_form_fields(self, tenant_a):
        form = ContactForm(tenant=tenant_a)
        assert "created_at" not in form.fields

    def test_missing_first_name_invalid(self, tenant_a):
        form = ContactForm(data={"last_name": "Doe", "status": "active"}, tenant=tenant_a)
        assert not form.is_valid()
        assert "first_name" in form.errors

    def test_missing_last_name_invalid(self, tenant_a):
        form = ContactForm(data={"first_name": "Jane", "status": "active"}, tenant=tenant_a)
        assert not form.is_valid()
        assert "last_name" in form.errors

    def test_account_queryset_scoped_to_tenant(self, tenant_a, tenant_b, account_a, account_b):
        """Account dropdown must only show the requesting tenant's accounts."""
        form = ContactForm(tenant=tenant_a)
        account_pks = [a.pk for a in form.fields["account"].queryset]
        assert account_a.pk in account_pks
        assert account_b.pk not in account_pks

    def test_no_tenant_gives_empty_account_queryset(self):
        form = ContactForm(tenant=None)
        assert form.fields["account"].queryset.count() == 0


# ============================================================ RelationshipMapForm
@pytest.mark.django_db
class TestRelationshipMapForm:
    def test_valid_form(self, tenant_a, account_a, contact_a, contact_a2):
        form = RelationshipMapForm(data={
            "account": account_a.pk,
            "from_contact": contact_a.pk,
            "to_contact": contact_a2.pk,
            "relationship_type": "reports_to",
            "strength": "strong",
            "notes": "",
        }, tenant=tenant_a)
        assert form.is_valid(), form.errors

    def test_tenant_not_in_form_fields(self, tenant_a):
        form = RelationshipMapForm(tenant=tenant_a)
        assert "tenant" not in form.fields

    def test_self_relationship_invalid(self, tenant_a, account_a, contact_a):
        """A contact cannot relate to itself."""
        form = RelationshipMapForm(data={
            "account": account_a.pk,
            "from_contact": contact_a.pk,
            "to_contact": contact_a.pk,
            "relationship_type": "peer",
            "strength": "moderate",
            "notes": "",
        }, tenant=tenant_a)
        assert not form.is_valid()

    def test_from_contact_queryset_scoped_to_tenant(self, tenant_a, tenant_b, contact_a, contact_b):
        form = RelationshipMapForm(tenant=tenant_a)
        contact_pks = [c.pk for c in form.fields["from_contact"].queryset]
        assert contact_a.pk in contact_pks
        assert contact_b.pk not in contact_pks

    def test_to_contact_queryset_scoped_to_tenant(self, tenant_a, tenant_b, contact_a, contact_b):
        form = RelationshipMapForm(tenant=tenant_a)
        contact_pks = [c.pk for c in form.fields["to_contact"].queryset]
        assert contact_a.pk in contact_pks
        assert contact_b.pk not in contact_pks

    def test_account_queryset_scoped_to_tenant(self, tenant_a, tenant_b, account_a, account_b):
        form = RelationshipMapForm(tenant=tenant_a)
        account_pks = [a.pk for a in form.fields["account"].queryset]
        assert account_a.pk in account_pks
        assert account_b.pk not in account_pks

    def test_no_tenant_gives_empty_querysets(self):
        form = RelationshipMapForm(tenant=None)
        assert form.fields["from_contact"].queryset.count() == 0
        assert form.fields["to_contact"].queryset.count() == 0
        assert form.fields["account"].queryset.count() == 0


# ============================================================ AccountPlanForm
@pytest.mark.django_db
class TestAccountPlanForm:
    def test_valid_form(self, tenant_a, account_a):
        from django.utils import timezone
        form = AccountPlanForm(data={
            "account": account_a.pk,
            "title": "Strategic Growth Plan",
            "fiscal_year": timezone.localdate().year,
            "status": "draft",
            "priority": "medium",
            "objective": "Grow revenue by 30%",
            "growth_strategy": "Expand into new markets",
            "target_revenue": "500000.00",
            "current_revenue": "350000.00",
            "start_date": "",
            "end_date": "",
        }, tenant=tenant_a)
        assert form.is_valid(), form.errors

    def test_tenant_not_in_form_fields(self, tenant_a):
        form = AccountPlanForm(tenant=tenant_a)
        assert "tenant" not in form.fields

    def test_number_not_in_form_fields(self, tenant_a):
        """number is auto-generated and must not appear in the form."""
        form = AccountPlanForm(tenant=tenant_a)
        assert "number" not in form.fields

    def test_approved_at_not_in_form_fields(self, tenant_a):
        """approved_at is system-set and must not appear in the form."""
        form = AccountPlanForm(tenant=tenant_a)
        assert "approved_at" not in form.fields

    def test_missing_title_invalid(self, tenant_a, account_a):
        from django.utils import timezone
        form = AccountPlanForm(data={
            "account": account_a.pk,
            "fiscal_year": timezone.localdate().year,
            "status": "draft",
            "priority": "medium",
        }, tenant=tenant_a)
        assert not form.is_valid()
        assert "title" in form.errors

    def test_account_queryset_scoped_to_tenant(self, tenant_a, tenant_b, account_a, account_b):
        """Account dropdown must only show the requesting tenant's accounts."""
        form = AccountPlanForm(tenant=tenant_a)
        account_pks = [a.pk for a in form.fields["account"].queryset]
        assert account_a.pk in account_pks
        assert account_b.pk not in account_pks

    def test_no_tenant_gives_empty_account_queryset(self):
        form = AccountPlanForm(tenant=None)
        assert form.fields["account"].queryset.count() == 0
