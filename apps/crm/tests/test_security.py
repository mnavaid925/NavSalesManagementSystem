"""Security tests: multi-tenant isolation and authorization for crm app."""
import pytest
from django.test import Client
from django.urls import reverse

from apps.crm.models import Account, AccountPlan, AccountTier, Contact, RelationshipMap


# ============================================================ cross-tenant IDOR 404
@pytest.mark.django_db
class TestCrossTenantIsolation404:
    """Tenant A must receive 404 (not 403/200) on ALL Tenant B resource URLs."""

    # AccountTier
    def test_accounttier_detail_cross_tenant_404(self, client_a, tier_b):
        resp = client_a.get(reverse("crm:accounttier_detail", args=[tier_b.pk]))
        assert resp.status_code == 404

    def test_accounttier_edit_cross_tenant_404(self, client_a, tier_b):
        resp = client_a.get(reverse("crm:accounttier_edit", args=[tier_b.pk]))
        assert resp.status_code == 404

    def test_accounttier_delete_cross_tenant_404(self, client_a, tier_b):
        resp = client_a.post(reverse("crm:accounttier_delete", args=[tier_b.pk]))
        assert resp.status_code == 404

    # Account
    def test_account_detail_cross_tenant_404(self, client_a, account_b):
        resp = client_a.get(reverse("crm:account_detail", args=[account_b.pk]))
        assert resp.status_code == 404

    def test_account_edit_cross_tenant_404(self, client_a, account_b):
        resp = client_a.get(reverse("crm:account_edit", args=[account_b.pk]))
        assert resp.status_code == 404

    def test_account_delete_cross_tenant_404(self, client_a, account_b):
        resp = client_a.post(reverse("crm:account_delete", args=[account_b.pk]))
        assert resp.status_code == 404

    # Contact
    def test_contact_detail_cross_tenant_404(self, client_a, contact_b):
        resp = client_a.get(reverse("crm:contact_detail", args=[contact_b.pk]))
        assert resp.status_code == 404

    def test_contact_edit_cross_tenant_404(self, client_a, contact_b):
        resp = client_a.get(reverse("crm:contact_edit", args=[contact_b.pk]))
        assert resp.status_code == 404

    def test_contact_delete_cross_tenant_404(self, client_a, contact_b):
        resp = client_a.post(reverse("crm:contact_delete", args=[contact_b.pk]))
        assert resp.status_code == 404

    # RelationshipMap
    def test_relmap_detail_cross_tenant_404(self, client_a, relmap_b):
        resp = client_a.get(reverse("crm:relationshipmap_detail", args=[relmap_b.pk]))
        assert resp.status_code == 404

    def test_relmap_edit_cross_tenant_404(self, client_a, relmap_b):
        resp = client_a.get(reverse("crm:relationshipmap_edit", args=[relmap_b.pk]))
        assert resp.status_code == 404

    def test_relmap_delete_cross_tenant_404(self, client_a, relmap_b):
        resp = client_a.post(reverse("crm:relationshipmap_delete", args=[relmap_b.pk]))
        assert resp.status_code == 404

    # AccountPlan
    def test_accountplan_detail_cross_tenant_404(self, client_a, plan_b):
        resp = client_a.get(reverse("crm:accountplan_detail", args=[plan_b.pk]))
        assert resp.status_code == 404

    def test_accountplan_edit_cross_tenant_404(self, client_a, plan_b):
        resp = client_a.get(reverse("crm:accountplan_edit", args=[plan_b.pk]))
        assert resp.status_code == 404

    def test_accountplan_delete_cross_tenant_404(self, client_a, plan_b):
        resp = client_a.post(reverse("crm:accountplan_delete", args=[plan_b.pk]))
        assert resp.status_code == 404


# ============================================================ list isolation
@pytest.mark.django_db
class TestListIsolation:
    """List views for Tenant A must never include Tenant B rows."""

    def test_accounttier_list_excludes_tenant_b(self, client_a, tier_a, tier_b):
        resp = client_a.get(reverse("crm:accounttier_list"))
        tier_pks = [t.pk for t in resp.context["tiers"]]
        assert tier_a.pk in tier_pks
        assert tier_b.pk not in tier_pks

    def test_account_list_excludes_tenant_b(self, client_a, account_a, account_b):
        resp = client_a.get(reverse("crm:account_list"))
        account_pks = [a.pk for a in resp.context["accounts"]]
        assert account_a.pk in account_pks
        assert account_b.pk not in account_pks

    def test_contact_list_excludes_tenant_b(self, client_a, contact_a, contact_b):
        resp = client_a.get(reverse("crm:contact_list"))
        contact_pks = [c.pk for c in resp.context["contacts"]]
        assert contact_a.pk in contact_pks
        assert contact_b.pk not in contact_pks

    def test_relmap_list_excludes_tenant_b(self, client_a, relmap_a, relmap_b):
        resp = client_a.get(reverse("crm:relationshipmap_list"))
        pks = [r.pk for r in resp.context["relationships"]]
        assert relmap_a.pk in pks
        assert relmap_b.pk not in pks

    def test_accountplan_list_excludes_tenant_b(self, client_a, plan_a, plan_b):
        resp = client_a.get(reverse("crm:accountplan_list"))
        plan_pks = [p.pk for p in resp.context["plans"]]
        assert plan_a.pk in plan_pks
        assert plan_b.pk not in plan_pks


# ============================================================ cross-tenant data integrity
@pytest.mark.django_db
class TestCrossTenantDataIntegrity:
    """Tenant B objects must remain untouched after Tenant A's failed IDOR attempts."""

    def test_account_b_not_deleted_after_tenant_a_delete_attempt(self, client_a, account_b):
        client_a.post(reverse("crm:account_delete", args=[account_b.pk]))
        assert Account.objects.filter(pk=account_b.pk).exists()

    def test_contact_b_not_deleted_after_tenant_a_delete_attempt(self, client_a, contact_b):
        client_a.post(reverse("crm:contact_delete", args=[contact_b.pk]))
        assert Contact.objects.filter(pk=contact_b.pk).exists()

    def test_tier_b_not_deleted_after_tenant_a_delete_attempt(self, client_a, tier_b):
        client_a.post(reverse("crm:accounttier_delete", args=[tier_b.pk]))
        assert AccountTier.objects.filter(pk=tier_b.pk).exists()

    def test_plan_b_not_deleted_after_tenant_a_delete_attempt(self, client_a, plan_b):
        client_a.post(reverse("crm:accountplan_delete", args=[plan_b.pk]))
        assert AccountPlan.objects.filter(pk=plan_b.pk).exists()

    def test_relmap_b_not_deleted_after_tenant_a_delete_attempt(self, client_a, relmap_b):
        client_a.post(reverse("crm:relationshipmap_delete", args=[relmap_b.pk]))
        assert RelationshipMap.objects.filter(pk=relmap_b.pk).exists()


# ============================================================ anonymous access
@pytest.mark.django_db
class TestAnonymousAccess:
    """Anonymous users must be redirected — not shown data or error pages."""

    def test_anonymous_cannot_delete_account(self, account_a):
        c = Client()
        resp = c.post(reverse("crm:account_delete", args=[account_a.pk]))
        assert resp.status_code in (301, 302)
        assert Account.objects.filter(pk=account_a.pk).exists()

    def test_anonymous_cannot_delete_contact(self, contact_a):
        c = Client()
        resp = c.post(reverse("crm:contact_delete", args=[contact_a.pk]))
        assert resp.status_code in (301, 302)
        assert Contact.objects.filter(pk=contact_a.pk).exists()

    def test_anonymous_cannot_create_account(self):
        c = Client()
        resp = c.post(reverse("crm:account_create"), {"name": "Hack Corp", "account_type": "prospect"})
        assert resp.status_code in (301, 302)
        assert not Account.objects.filter(name="Hack Corp").exists()

    def test_anonymous_cannot_create_contact(self):
        c = Client()
        resp = c.post(reverse("crm:contact_create"), {"first_name": "Hack", "last_name": "User"})
        assert resp.status_code in (301, 302)
        assert not Contact.objects.filter(first_name="Hack", last_name="User").exists()

    def test_anonymous_cannot_delete_plan(self, plan_a):
        c = Client()
        resp = c.post(reverse("crm:accountplan_delete", args=[plan_a.pk]))
        assert resp.status_code in (301, 302)
        assert AccountPlan.objects.filter(pk=plan_a.pk).exists()


# ============================================================ CSRF enforcement
@pytest.mark.django_db
class TestCSRFEnforcement:
    def test_csrf_blocks_anonymous_create_account(self):
        c = Client(enforce_csrf_checks=True)
        resp = c.post(reverse("crm:account_create"), {"name": "CSRF Test", "account_type": "prospect"})
        # Anonymous: gets redirect to login (302), not data creation
        assert resp.status_code in (301, 302, 403)

    def test_csrf_blocks_anonymous_create_contact(self):
        c = Client(enforce_csrf_checks=True)
        resp = c.post(reverse("crm:contact_create"), {"first_name": "CSRFTest", "last_name": "User"})
        assert resp.status_code in (301, 302, 403)
