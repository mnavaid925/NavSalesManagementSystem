"""Tests for crm views: CRUD for AccountTier, Account, Contact, RelationshipMap, AccountPlan."""
import pytest
from django.test import Client
from django.urls import reverse

from apps.crm.models import Account, AccountPlan, AccountTier, Contact, RelationshipMap


# ============================================================ anonymous redirects
@pytest.mark.django_db
class TestAnonymousRedirects:
    def _anon(self):
        return Client()

    def test_account_list_redirects_anonymous(self):
        resp = self._anon().get(reverse("crm:account_list"))
        assert resp.status_code in (301, 302)

    def test_contact_list_redirects_anonymous(self):
        resp = self._anon().get(reverse("crm:contact_list"))
        assert resp.status_code in (301, 302)

    def test_relationshipmap_list_redirects_anonymous(self):
        resp = self._anon().get(reverse("crm:relationshipmap_list"))
        assert resp.status_code in (301, 302)

    def test_accounttier_list_redirects_anonymous(self):
        resp = self._anon().get(reverse("crm:accounttier_list"))
        assert resp.status_code in (301, 302)

    def test_accountplan_list_redirects_anonymous(self):
        resp = self._anon().get(reverse("crm:accountplan_list"))
        assert resp.status_code in (301, 302)


# ============================================================ AccountTier CRUD
@pytest.mark.django_db
class TestAccountTierCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("crm:accounttier_list"))
        assert resp.status_code == 200

    def test_list_context_has_tiers(self, client_a, tier_a):
        resp = client_a.get(reverse("crm:accounttier_list"))
        assert "tiers" in resp.context

    def test_list_seeded_tier_appears(self, client_a, tier_a):
        resp = client_a.get(reverse("crm:accounttier_list"))
        tier_pks = [t.pk for t in resp.context["tiers"]]
        assert tier_a.pk in tier_pks

    def test_list_context_has_segment_choices(self, client_a):
        resp = client_a.get(reverse("crm:accounttier_list"))
        assert "segment_choices" in resp.context

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("crm:accounttier_create"))
        assert resp.status_code == 200

    def test_create_post_creates_tier(self, client_a, tenant_a):
        before = AccountTier.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("crm:accounttier_create"), {
            "name": "New Enterprise Tier",
            "segment": "enterprise",
            "rank": 1,
            "min_annual_value": "250000.00",
            "color": "#2563eb",
            "description": "Enterprise tier",
            "is_active": True,
        })
        assert AccountTier.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a):
        client_a.post(reverse("crm:accounttier_create"), {
            "name": "Tenant Check Tier",
            "segment": "smb",
            "rank": 5,
            "min_annual_value": "0",
            "color": "#2563eb",
            "description": "",
            "is_active": True,
        })
        tier = AccountTier.objects.filter(name="Tenant Check Tier").first()
        assert tier is not None
        assert tier.tenant == tenant_a

    def test_detail_200(self, client_a, tier_a):
        resp = client_a.get(reverse("crm:accounttier_detail", args=[tier_a.pk]))
        assert resp.status_code == 200

    def test_edit_get_200(self, client_a, tier_a):
        resp = client_a.get(reverse("crm:accounttier_edit", args=[tier_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_tier(self, client_a, tier_a):
        client_a.post(reverse("crm:accounttier_edit", args=[tier_a.pk]), {
            "name": "Updated Tier Name",
            "segment": "strategic",
            "rank": 1,
            "min_annual_value": "500000.00",
            "color": "#2563eb",
            "description": "Updated description",
            "is_active": True,
        })
        tier_a.refresh_from_db()
        assert tier_a.name == "Updated Tier Name"

    def test_delete_post_deletes_tier(self, client_a, tenant_a):
        tier = AccountTier.objects.create(tenant=tenant_a, name="ToDelete Tier", rank=99)
        client_a.post(reverse("crm:accounttier_delete", args=[tier.pk]))
        assert not AccountTier.objects.filter(pk=tier.pk).exists()

    def test_detail_404_for_other_tenant(self, client_a, tier_b):
        resp = client_a.get(reverse("crm:accounttier_detail", args=[tier_b.pk]))
        assert resp.status_code == 404

    def test_edit_404_for_other_tenant(self, client_a, tier_b):
        resp = client_a.get(reverse("crm:accounttier_edit", args=[tier_b.pk]))
        assert resp.status_code == 404

    def test_delete_404_for_other_tenant(self, client_a, tier_b):
        resp = client_a.post(reverse("crm:accounttier_delete", args=[tier_b.pk]))
        assert resp.status_code == 404


# ============================================================ Account CRUD
@pytest.mark.django_db
class TestAccountCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("crm:account_list"))
        assert resp.status_code == 200

    def test_list_context_has_accounts(self, client_a, account_a):
        resp = client_a.get(reverse("crm:account_list"))
        assert "accounts" in resp.context

    def test_list_seeded_account_appears(self, client_a, account_a):
        resp = client_a.get(reverse("crm:account_list"))
        account_pks = [a.pk for a in resp.context["accounts"]]
        assert account_a.pk in account_pks

    def test_list_context_has_type_choices(self, client_a):
        resp = client_a.get(reverse("crm:account_list"))
        assert "type_choices" in resp.context

    def test_list_context_has_status_choices(self, client_a):
        resp = client_a.get(reverse("crm:account_list"))
        assert "status_choices" in resp.context

    def test_list_context_has_tiers(self, client_a):
        resp = client_a.get(reverse("crm:account_list"))
        assert "tiers" in resp.context

    def test_list_context_has_total(self, client_a):
        resp = client_a.get(reverse("crm:account_list"))
        assert "total" in resp.context

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("crm:account_create"))
        assert resp.status_code == 200

    def test_create_post_creates_account(self, client_a, tenant_a):
        before = Account.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("crm:account_create"), {
            "name": "New Account Corp",
            "account_type": "prospect",
            "status": "active",
            "industry": "Tech",
            "website": "",
            "phone": "",
            "billing_city": "",
            "billing_country": "",
            "employee_count": "",
            "annual_revenue": "0",
            "description": "",
            "parent": "",
            "tier": "",
        })
        assert Account.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a):
        client_a.post(reverse("crm:account_create"), {
            "name": "Tenant Check Corp",
            "account_type": "customer",
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
        })
        acc = Account.objects.filter(name="Tenant Check Corp").first()
        assert acc is not None
        assert acc.tenant == tenant_a

    def test_create_auto_numbers_account(self, client_a, tenant_a):
        Account.objects.filter(tenant=tenant_a).delete()
        client_a.post(reverse("crm:account_create"), {
            "name": "Numbered Corp",
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
        })
        acc = Account.objects.filter(name="Numbered Corp").first()
        assert acc.number.startswith("ACC-")

    def test_detail_200(self, client_a, account_a):
        resp = client_a.get(reverse("crm:account_detail", args=[account_a.pk]))
        assert resp.status_code == 200

    def test_edit_get_200(self, client_a, account_a):
        resp = client_a.get(reverse("crm:account_edit", args=[account_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_account(self, client_a, account_a, tier_a):
        client_a.post(reverse("crm:account_edit", args=[account_a.pk]), {
            "name": "Updated Acme Corp",
            "account_type": "customer",
            "status": "active",
            "industry": "Manufacturing",
            "website": "",
            "phone": "",
            "billing_city": "",
            "billing_country": "",
            "employee_count": "",
            "annual_revenue": "0",
            "description": "",
            "parent": "",
            "tier": tier_a.pk,
        })
        account_a.refresh_from_db()
        assert account_a.name == "Updated Acme Corp"
        assert account_a.industry == "Manufacturing"

    def test_delete_post_deletes_account(self, client_a, tenant_a):
        acc = Account.objects.create(tenant=tenant_a, name="ToDelete Corp")
        client_a.post(reverse("crm:account_delete", args=[acc.pk]))
        assert not Account.objects.filter(pk=acc.pk).exists()

    def test_detail_404_for_other_tenant(self, client_a, account_b):
        resp = client_a.get(reverse("crm:account_detail", args=[account_b.pk]))
        assert resp.status_code == 404

    def test_edit_404_for_other_tenant(self, client_a, account_b):
        resp = client_a.get(reverse("crm:account_edit", args=[account_b.pk]))
        assert resp.status_code == 404

    def test_delete_404_for_other_tenant(self, client_a, account_b):
        resp = client_a.post(reverse("crm:account_delete", args=[account_b.pk]))
        assert resp.status_code == 404

    def test_list_search_filters_by_name(self, client_a, account_a, tenant_a):
        Account.objects.create(tenant=tenant_a, name="Other Corp")
        resp = client_a.get(reverse("crm:account_list"), {"q": "Acme"})
        account_pks = [a.pk for a in resp.context["accounts"]]
        assert account_a.pk in account_pks

    def test_list_filter_by_status(self, client_a, account_a, tenant_a):
        Account.objects.create(tenant=tenant_a, name="Inactive Corp", status=Account.STATUS_INACTIVE)
        resp = client_a.get(reverse("crm:account_list"), {"status": Account.STATUS_ACTIVE})
        account_names = [a.name for a in resp.context["accounts"]]
        assert "Inactive Corp" not in account_names


# ============================================================ Contact CRUD
@pytest.mark.django_db
class TestContactCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("crm:contact_list"))
        assert resp.status_code == 200

    def test_list_context_has_contacts(self, client_a, contact_a):
        resp = client_a.get(reverse("crm:contact_list"))
        assert "contacts" in resp.context

    def test_list_seeded_contact_appears(self, client_a, contact_a):
        resp = client_a.get(reverse("crm:contact_list"))
        contact_pks = [c.pk for c in resp.context["contacts"]]
        assert contact_a.pk in contact_pks

    def test_list_context_has_status_choices(self, client_a):
        resp = client_a.get(reverse("crm:contact_list"))
        assert "status_choices" in resp.context

    def test_list_context_has_enrichment_choices(self, client_a):
        resp = client_a.get(reverse("crm:contact_list"))
        assert "enrichment_choices" in resp.context

    def test_list_context_has_accounts(self, client_a):
        resp = client_a.get(reverse("crm:contact_list"))
        assert "accounts" in resp.context

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("crm:contact_create"))
        assert resp.status_code == 200

    def test_create_post_creates_contact(self, client_a, tenant_a, account_a):
        before = Contact.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("crm:contact_create"), {
            "first_name": "New",
            "last_name": "Person",
            "account": account_a.pk,
            "title": "",
            "department": "",
            "email": "new@example.com",
            "phone": "",
            "mobile": "",
            "linkedin_url": "",
            "status": "active",
            "enrichment_status": "none",
            "is_primary": False,
            "notes": "",
        })
        assert Contact.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a, account_a):
        client_a.post(reverse("crm:contact_create"), {
            "first_name": "Tenant",
            "last_name": "Check",
            "account": account_a.pk,
            "title": "",
            "department": "",
            "email": "tc@example.com",
            "phone": "",
            "mobile": "",
            "linkedin_url": "",
            "status": "active",
            "enrichment_status": "none",
            "is_primary": False,
            "notes": "",
        })
        c = Contact.objects.filter(first_name="Tenant", last_name="Check").first()
        assert c is not None
        assert c.tenant == tenant_a

    def test_detail_200(self, client_a, contact_a):
        resp = client_a.get(reverse("crm:contact_detail", args=[contact_a.pk]))
        assert resp.status_code == 200

    def test_edit_get_200(self, client_a, contact_a):
        resp = client_a.get(reverse("crm:contact_edit", args=[contact_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_contact(self, client_a, contact_a, account_a):
        client_a.post(reverse("crm:contact_edit", args=[contact_a.pk]), {
            "first_name": "Alice",
            "last_name": "Updated",
            "account": account_a.pk,
            "title": "CTO",
            "department": "Engineering",
            "email": "alice@acme.com",
            "phone": "",
            "mobile": "",
            "linkedin_url": "",
            "status": "active",
            "enrichment_status": "verified",
            "is_primary": True,
            "notes": "",
        })
        contact_a.refresh_from_db()
        assert contact_a.last_name == "Updated"
        assert contact_a.enrichment_status == "verified"

    def test_delete_post_deletes_contact(self, client_a, tenant_a):
        c = Contact.objects.create(tenant=tenant_a, first_name="ToDelete", last_name="User")
        client_a.post(reverse("crm:contact_delete", args=[c.pk]))
        assert not Contact.objects.filter(pk=c.pk).exists()

    def test_detail_404_for_other_tenant(self, client_a, contact_b):
        resp = client_a.get(reverse("crm:contact_detail", args=[contact_b.pk]))
        assert resp.status_code == 404

    def test_edit_404_for_other_tenant(self, client_a, contact_b):
        resp = client_a.get(reverse("crm:contact_edit", args=[contact_b.pk]))
        assert resp.status_code == 404

    def test_delete_404_for_other_tenant(self, client_a, contact_b):
        resp = client_a.post(reverse("crm:contact_delete", args=[contact_b.pk]))
        assert resp.status_code == 404


# ============================================================ RelationshipMap CRUD
@pytest.mark.django_db
class TestRelationshipMapCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("crm:relationshipmap_list"))
        assert resp.status_code == 200

    def test_list_context_has_relationships(self, client_a, relmap_a):
        resp = client_a.get(reverse("crm:relationshipmap_list"))
        assert "relationships" in resp.context

    def test_list_seeded_relmap_appears(self, client_a, relmap_a):
        resp = client_a.get(reverse("crm:relationshipmap_list"))
        pks = [r.pk for r in resp.context["relationships"]]
        assert relmap_a.pk in pks

    def test_list_context_has_type_choices(self, client_a):
        resp = client_a.get(reverse("crm:relationshipmap_list"))
        assert "type_choices" in resp.context

    def test_list_context_has_strength_choices(self, client_a):
        resp = client_a.get(reverse("crm:relationshipmap_list"))
        assert "strength_choices" in resp.context

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("crm:relationshipmap_create"))
        assert resp.status_code == 200

    def test_create_post_creates_relmap(self, client_a, tenant_a, account_a, contact_a, contact_a2):
        before = RelationshipMap.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("crm:relationshipmap_create"), {
            "account": account_a.pk,
            "from_contact": contact_a.pk,
            "to_contact": contact_a2.pk,
            "relationship_type": "influences",
            "strength": "moderate",
            "notes": "",
        })
        assert RelationshipMap.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a, account_a, contact_a, contact_a2):
        client_a.post(reverse("crm:relationshipmap_create"), {
            "account": account_a.pk,
            "from_contact": contact_a.pk,
            "to_contact": contact_a2.pk,
            "relationship_type": "sponsor",
            "strength": "weak",
            "notes": "tenant check",
        })
        rm = RelationshipMap.objects.filter(notes="tenant check").first()
        assert rm is not None
        assert rm.tenant == tenant_a

    def test_create_self_relationship_rejected(self, client_a, tenant_a, account_a, contact_a):
        before = RelationshipMap.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("crm:relationshipmap_create"), {
            "account": account_a.pk,
            "from_contact": contact_a.pk,
            "to_contact": contact_a.pk,
            "relationship_type": "peer",
            "strength": "moderate",
            "notes": "",
        })
        # Should not have been created
        assert RelationshipMap.objects.filter(tenant=tenant_a).count() == before

    def test_detail_200(self, client_a, relmap_a):
        resp = client_a.get(reverse("crm:relationshipmap_detail", args=[relmap_a.pk]))
        assert resp.status_code == 200

    def test_edit_get_200(self, client_a, relmap_a):
        resp = client_a.get(reverse("crm:relationshipmap_edit", args=[relmap_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_relmap(self, client_a, relmap_a, account_a, contact_a, contact_a2):
        client_a.post(reverse("crm:relationshipmap_edit", args=[relmap_a.pk]), {
            "account": account_a.pk,
            "from_contact": contact_a.pk,
            "to_contact": contact_a2.pk,
            "relationship_type": "influences",
            "strength": "weak",
            "notes": "updated notes",
        })
        relmap_a.refresh_from_db()
        assert relmap_a.relationship_type == "influences"
        assert relmap_a.notes == "updated notes"

    def test_delete_post_deletes_relmap(self, client_a, tenant_a, account_a, contact_a, contact_a2):
        rm = RelationshipMap.objects.create(
            tenant=tenant_a,
            account=account_a,
            from_contact=contact_a,
            to_contact=contact_a2,
            relationship_type=RelationshipMap.TYPE_BLOCKER,
        )
        client_a.post(reverse("crm:relationshipmap_delete", args=[rm.pk]))
        assert not RelationshipMap.objects.filter(pk=rm.pk).exists()

    def test_detail_404_for_other_tenant(self, client_a, relmap_b):
        resp = client_a.get(reverse("crm:relationshipmap_detail", args=[relmap_b.pk]))
        assert resp.status_code == 404

    def test_edit_404_for_other_tenant(self, client_a, relmap_b):
        resp = client_a.get(reverse("crm:relationshipmap_edit", args=[relmap_b.pk]))
        assert resp.status_code == 404

    def test_delete_404_for_other_tenant(self, client_a, relmap_b):
        resp = client_a.post(reverse("crm:relationshipmap_delete", args=[relmap_b.pk]))
        assert resp.status_code == 404


# ============================================================ AccountPlan CRUD
@pytest.mark.django_db
class TestAccountPlanCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("crm:accountplan_list"))
        assert resp.status_code == 200

    def test_list_context_has_plans(self, client_a, plan_a):
        resp = client_a.get(reverse("crm:accountplan_list"))
        assert "plans" in resp.context

    def test_list_seeded_plan_appears(self, client_a, plan_a):
        resp = client_a.get(reverse("crm:accountplan_list"))
        plan_pks = [p.pk for p in resp.context["plans"]]
        assert plan_a.pk in plan_pks

    def test_list_context_has_status_choices(self, client_a):
        resp = client_a.get(reverse("crm:accountplan_list"))
        assert "status_choices" in resp.context

    def test_list_context_has_priority_choices(self, client_a):
        resp = client_a.get(reverse("crm:accountplan_list"))
        assert "priority_choices" in resp.context

    def test_list_context_has_accounts(self, client_a):
        resp = client_a.get(reverse("crm:accountplan_list"))
        assert "accounts" in resp.context

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("crm:accountplan_create"))
        assert resp.status_code == 200

    def test_create_post_creates_plan(self, client_a, tenant_a, account_a):
        from django.utils import timezone
        before = AccountPlan.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("crm:accountplan_create"), {
            "account": account_a.pk,
            "title": "New Growth Plan",
            "fiscal_year": timezone.localdate().year,
            "status": "draft",
            "priority": "high",
            "objective": "Grow 30%",
            "growth_strategy": "Expand product line",
            "target_revenue": "300000.00",
            "current_revenue": "200000.00",
            "start_date": "",
            "end_date": "",
        })
        assert AccountPlan.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a, account_a):
        from django.utils import timezone
        client_a.post(reverse("crm:accountplan_create"), {
            "account": account_a.pk,
            "title": "Tenant Check Plan",
            "fiscal_year": timezone.localdate().year,
            "status": "draft",
            "priority": "medium",
            "objective": "",
            "growth_strategy": "",
            "target_revenue": "0",
            "current_revenue": "0",
            "start_date": "",
            "end_date": "",
        })
        plan = AccountPlan.objects.filter(title="Tenant Check Plan").first()
        assert plan is not None
        assert plan.tenant == tenant_a

    def test_create_auto_numbers_plan(self, client_a, tenant_a, account_a):
        from django.utils import timezone
        AccountPlan.objects.filter(tenant=tenant_a).delete()
        client_a.post(reverse("crm:accountplan_create"), {
            "account": account_a.pk,
            "title": "Numbered Plan",
            "fiscal_year": timezone.localdate().year,
            "status": "draft",
            "priority": "low",
            "objective": "",
            "growth_strategy": "",
            "target_revenue": "0",
            "current_revenue": "0",
            "start_date": "",
            "end_date": "",
        })
        plan = AccountPlan.objects.filter(title="Numbered Plan").first()
        assert plan.number.startswith("PLAN-")

    def test_detail_200(self, client_a, plan_a):
        resp = client_a.get(reverse("crm:accountplan_detail", args=[plan_a.pk]))
        assert resp.status_code == 200

    def test_edit_get_200(self, client_a, plan_a):
        resp = client_a.get(reverse("crm:accountplan_edit", args=[plan_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates_plan(self, client_a, plan_a, account_a):
        from django.utils import timezone
        client_a.post(reverse("crm:accountplan_edit", args=[plan_a.pk]), {
            "account": account_a.pk,
            "title": "Updated Growth Plan",
            "fiscal_year": timezone.localdate().year,
            "status": "active",
            "priority": "high",
            "objective": "Updated objective",
            "growth_strategy": "",
            "target_revenue": "0",
            "current_revenue": "0",
            "start_date": "",
            "end_date": "",
        })
        plan_a.refresh_from_db()
        assert plan_a.title == "Updated Growth Plan"
        assert plan_a.status == "active"

    def test_delete_post_deletes_plan(self, client_a, tenant_a, account_a):
        plan = AccountPlan.objects.create(tenant=tenant_a, account=account_a, title="ToDelete Plan")
        client_a.post(reverse("crm:accountplan_delete", args=[plan.pk]))
        assert not AccountPlan.objects.filter(pk=plan.pk).exists()

    def test_detail_404_for_other_tenant(self, client_a, plan_b):
        resp = client_a.get(reverse("crm:accountplan_detail", args=[plan_b.pk]))
        assert resp.status_code == 404

    def test_edit_404_for_other_tenant(self, client_a, plan_b):
        resp = client_a.get(reverse("crm:accountplan_edit", args=[plan_b.pk]))
        assert resp.status_code == 404

    def test_delete_404_for_other_tenant(self, client_a, plan_b):
        resp = client_a.post(reverse("crm:accountplan_delete", args=[plan_b.pk]))
        assert resp.status_code == 404


# ============================================================ Rep (non-admin) permissions
@pytest.mark.django_db
class TestRepPermissions:
    def test_rep_can_view_account_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("crm:account_list"))
        assert resp.status_code == 200

    def test_rep_can_view_contact_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("crm:contact_list"))
        assert resp.status_code == 200

    def test_rep_can_view_relationshipmap_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("crm:relationshipmap_list"))
        assert resp.status_code == 200

    def test_rep_can_view_accounttier_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("crm:accounttier_list"))
        assert resp.status_code == 200

    def test_rep_can_view_accountplan_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("crm:accountplan_list"))
        assert resp.status_code == 200

    def test_rep_cannot_create_account(self, rep_client_a):
        resp = rep_client_a.get(reverse("crm:account_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_contact(self, rep_client_a):
        resp = rep_client_a.get(reverse("crm:contact_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_tier(self, rep_client_a):
        resp = rep_client_a.get(reverse("crm:accounttier_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_plan(self, rep_client_a):
        resp = rep_client_a.get(reverse("crm:accountplan_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_delete_account(self, rep_client_a, account_a):
        resp = rep_client_a.post(reverse("crm:account_delete", args=[account_a.pk]))
        assert resp.status_code in (301, 302)
        assert Account.objects.filter(pk=account_a.pk).exists()

    def test_rep_cannot_delete_contact(self, rep_client_a, contact_a):
        resp = rep_client_a.post(reverse("crm:contact_delete", args=[contact_a.pk]))
        assert resp.status_code in (301, 302)
        assert Contact.objects.filter(pk=contact_a.pk).exists()
