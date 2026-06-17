"""Security tests: multi-tenant isolation and authorization enforcement."""
import pytest
from django.test import Client
from django.urls import reverse

from apps.accounts.models import Role, User, UserInvite
from apps.tenants.models import (
    BrandingSetting, EncryptionKey, HealthMetric, Invoice, OnboardingStep, Subscription,
)


@pytest.mark.django_db
class TestCrossTenatIsolation404:
    """Tenant A must receive 404 (not 403/200) on ALL Tenant B resource URLs."""

    def test_invoice_detail_cross_tenant_404(self, client_a, invoice_b):
        resp = client_a.get(reverse("tenants:invoice_detail", args=[invoice_b.pk]))
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"

    def test_invoice_edit_cross_tenant_404(self, client_a, invoice_b):
        resp = client_a.get(reverse("tenants:invoice_edit", args=[invoice_b.pk]))
        assert resp.status_code == 404

    def test_invoice_delete_cross_tenant_404(self, client_a, invoice_b):
        resp = client_a.post(reverse("tenants:invoice_delete", args=[invoice_b.pk]))
        assert resp.status_code == 404

    def test_subscription_detail_cross_tenant_404(self, client_a, subscription_b):
        resp = client_a.get(reverse("tenants:subscription_detail", args=[subscription_b.pk]))
        assert resp.status_code == 404

    def test_subscription_edit_cross_tenant_404(self, client_a, subscription_b):
        resp = client_a.get(reverse("tenants:subscription_edit", args=[subscription_b.pk]))
        assert resp.status_code == 404

    def test_subscription_delete_cross_tenant_404(self, client_a, subscription_b):
        resp = client_a.post(reverse("tenants:subscription_delete", args=[subscription_b.pk]))
        assert resp.status_code == 404

    def test_encryption_key_detail_cross_tenant_404(self, client_a, encryption_key_b):
        resp = client_a.get(reverse("tenants:encryptionkey_detail", args=[encryption_key_b.pk]))
        assert resp.status_code == 404

    def test_encryption_key_rotate_cross_tenant_404(self, client_a, encryption_key_b):
        resp = client_a.post(reverse("tenants:encryptionkey_rotate", args=[encryption_key_b.pk]))
        assert resp.status_code == 404

    def test_encryption_key_delete_cross_tenant_404(self, client_a, encryption_key_b):
        resp = client_a.post(reverse("tenants:encryptionkey_delete", args=[encryption_key_b.pk]))
        assert resp.status_code == 404

    def test_branding_detail_cross_tenant_404(self, client_a, branding_b):
        resp = client_a.get(reverse("tenants:brandingsetting_detail", args=[branding_b.pk]))
        assert resp.status_code == 404

    def test_branding_edit_cross_tenant_404(self, client_a, branding_b):
        resp = client_a.get(reverse("tenants:brandingsetting_edit", args=[branding_b.pk]))
        assert resp.status_code == 404

    def test_branding_delete_cross_tenant_404(self, client_a, branding_b):
        resp = client_a.post(reverse("tenants:brandingsetting_delete", args=[branding_b.pk]))
        assert resp.status_code == 404

    def test_healthmetric_detail_cross_tenant_404(self, client_a, healthmetric_b):
        resp = client_a.get(reverse("tenants:healthmetric_detail", args=[healthmetric_b.pk]))
        assert resp.status_code == 404

    def test_healthmetric_edit_cross_tenant_404(self, client_a, healthmetric_b):
        resp = client_a.get(reverse("tenants:healthmetric_edit", args=[healthmetric_b.pk]))
        assert resp.status_code == 404

    def test_healthmetric_delete_cross_tenant_404(self, client_a, healthmetric_b):
        resp = client_a.post(reverse("tenants:healthmetric_delete", args=[healthmetric_b.pk]))
        assert resp.status_code == 404

    def test_onboarding_step_detail_cross_tenant_404(self, client_a, onboarding_step_b):
        resp = client_a.get(reverse("tenants:onboardingstep_detail", args=[onboarding_step_b.pk]))
        assert resp.status_code == 404

    def test_onboarding_step_edit_cross_tenant_404(self, client_a, onboarding_step_b):
        resp = client_a.get(reverse("tenants:onboardingstep_edit", args=[onboarding_step_b.pk]))
        assert resp.status_code == 404

    def test_onboarding_step_delete_cross_tenant_404(self, client_a, onboarding_step_b):
        resp = client_a.post(reverse("tenants:onboardingstep_delete", args=[onboarding_step_b.pk]))
        assert resp.status_code == 404

    def test_user_detail_cross_tenant_404(self, client_a, admin_b):
        resp = client_a.get(reverse("accounts:user_detail", args=[admin_b.pk]))
        assert resp.status_code == 404

    def test_user_edit_cross_tenant_404(self, client_a, admin_b):
        resp = client_a.get(reverse("accounts:user_edit", args=[admin_b.pk]))
        assert resp.status_code == 404

    def test_user_delete_cross_tenant_404(self, client_a, admin_b):
        resp = client_a.post(reverse("accounts:user_delete", args=[admin_b.pk]))
        assert resp.status_code == 404

    def test_role_detail_cross_tenant_404(self, client_a, role_b):
        resp = client_a.get(reverse("accounts:role_detail", args=[role_b.pk]))
        assert resp.status_code == 404

    def test_role_edit_cross_tenant_404(self, client_a, role_b):
        resp = client_a.get(reverse("accounts:role_edit", args=[role_b.pk]))
        assert resp.status_code == 404


@pytest.mark.django_db
class TestListIsolation:
    """List views for Tenant A should never include Tenant B rows."""

    def test_invoice_list_excludes_tenant_b(self, client_a, invoice_a, invoice_b):
        resp = client_a.get(reverse("tenants:invoice_list"))
        invoice_pks = [inv.pk for inv in resp.context["invoices"]]
        assert invoice_a.pk in invoice_pks
        assert invoice_b.pk not in invoice_pks

    def test_subscription_list_excludes_tenant_b(self, client_a, subscription_a, subscription_b):
        resp = client_a.get(reverse("tenants:subscription_list"))
        sub_pks = [s.pk for s in resp.context["subscriptions"]]
        assert subscription_a.pk in sub_pks
        assert subscription_b.pk not in sub_pks

    def test_encryption_key_list_excludes_tenant_b(self, client_a, encryption_key_a, encryption_key_b):
        resp = client_a.get(reverse("tenants:encryptionkey_list"))
        key_pks = [k.pk for k in resp.context["keys"]]
        assert encryption_key_a.pk in key_pks
        assert encryption_key_b.pk not in key_pks

    def test_branding_list_excludes_tenant_b(self, client_a, branding_a, branding_b):
        resp = client_a.get(reverse("tenants:brandingsetting_list"))
        profile_pks = [p.pk for p in resp.context["profiles"]]
        assert branding_a.pk in profile_pks
        assert branding_b.pk not in profile_pks

    def test_healthmetric_list_excludes_tenant_b(self, client_a, healthmetric_a, healthmetric_b):
        resp = client_a.get(reverse("tenants:healthmetric_list"))
        metric_pks = [m.pk for m in resp.context["metrics"]]
        assert healthmetric_a.pk in metric_pks
        assert healthmetric_b.pk not in metric_pks

    def test_onboarding_list_excludes_tenant_b(self, client_a, onboarding_step_a, onboarding_step_b):
        resp = client_a.get(reverse("tenants:onboardingstep_list"))
        step_pks = [s.pk for s in resp.context["steps"]]
        assert onboarding_step_a.pk in step_pks
        assert onboarding_step_b.pk not in step_pks

    def test_user_list_excludes_tenant_b_users(self, client_a, admin_b):
        resp = client_a.get(reverse("accounts:user_list"))
        user_pks = [u.pk for u in resp.context["users"]]
        assert admin_b.pk not in user_pks


@pytest.mark.django_db
class TestCSRFAndPermissions:
    """CSRF is enforced by Django middleware; anonymous hits → login redirect."""

    def test_anonymous_invoice_create_redirects_to_login(self):
        c = Client(enforce_csrf_checks=True)
        resp = c.post(reverse("tenants:invoice_create"), {"amount": "100.00"})
        assert resp.status_code in (301, 302, 403)

    def test_anonymous_cannot_rotate_key(self):
        c = Client()
        from apps.core.models import Tenant as CoreTenant
        from apps.tenants.models import EncryptionKey
        t = CoreTenant.objects.create(name="CsrfTest", slug="csrf-test")
        _, prefix, hashed = EncryptionKey.generate_secret()
        key = EncryptionKey.objects.create(tenant=t, label="CK", key_prefix=prefix, hashed_key=hashed)
        resp = c.post(reverse("tenants:encryptionkey_rotate", args=[key.pk]))
        assert resp.status_code in (301, 302)

    def test_anonymous_cannot_delete_invoice(self):
        c = Client()
        from apps.core.models import Tenant as CoreTenant
        t = CoreTenant.objects.create(name="AnonTest", slug="anon-test")
        inv = Invoice.objects.create(tenant=t, amount="1.00")
        resp = c.post(reverse("tenants:invoice_delete", args=[inv.pk]))
        assert resp.status_code in (301, 302)
        # Invoice should still exist
        assert Invoice.objects.filter(pk=inv.pk).exists()

    def test_anonymous_cannot_delete_subscription(self):
        c = Client()
        from apps.core.models import Tenant as CoreTenant
        t = CoreTenant.objects.create(name="AnonTest2", slug="anon-test2")
        sub = Subscription.objects.create(tenant=t)
        resp = c.post(reverse("tenants:subscription_delete", args=[sub.pk]))
        assert resp.status_code in (301, 302)
        assert Subscription.objects.filter(pk=sub.pk).exists()
