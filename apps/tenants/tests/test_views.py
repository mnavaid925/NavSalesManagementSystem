"""Tests for tenants views: CRUD for all Module 0 models."""
import pytest
from django.urls import reverse
from django.test import Client

from apps.tenants.models import (
    BrandingSetting, EncryptionKey, HealthMetric, Invoice, OnboardingStep, Subscription,
)


# ============================================================ anonymous redirects
@pytest.mark.django_db
class TestAnonymousRedirects:
    def _get(self, url):
        return Client().get(url)

    def test_onboarding_list_redirects_anonymous(self):
        resp = self._get(reverse("tenants:onboardingstep_list"))
        assert resp.status_code in (301, 302)

    def test_subscription_list_redirects_anonymous(self):
        resp = self._get(reverse("tenants:subscription_list"))
        assert resp.status_code in (301, 302)

    def test_invoice_list_redirects_anonymous(self):
        resp = self._get(reverse("tenants:invoice_list"))
        assert resp.status_code in (301, 302)

    def test_encryption_key_list_redirects_anonymous(self):
        resp = self._get(reverse("tenants:encryptionkey_list"))
        assert resp.status_code in (301, 302)

    def test_branding_list_redirects_anonymous(self):
        resp = self._get(reverse("tenants:brandingsetting_list"))
        assert resp.status_code in (301, 302)

    def test_healthmetric_list_redirects_anonymous(self):
        resp = self._get(reverse("tenants:healthmetric_list"))
        assert resp.status_code in (301, 302)


# ============================================================ non-admin rep blocked on write views
@pytest.mark.django_db
class TestRepBlockedFromWriteViews:
    def test_rep_cannot_create_onboarding_step(self, rep_client_a):
        resp = rep_client_a.get(reverse("tenants:onboardingstep_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_subscription(self, rep_client_a):
        resp = rep_client_a.get(reverse("tenants:subscription_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_invoice(self, rep_client_a):
        resp = rep_client_a.get(reverse("tenants:invoice_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_encryption_key(self, rep_client_a):
        resp = rep_client_a.get(reverse("tenants:encryptionkey_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_branding(self, rep_client_a):
        resp = rep_client_a.get(reverse("tenants:brandingsetting_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_healthmetric(self, rep_client_a):
        resp = rep_client_a.get(reverse("tenants:healthmetric_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_rotate_encryption_key(self, rep_client_a, encryption_key_a):
        resp = rep_client_a.post(reverse("tenants:encryptionkey_rotate", args=[encryption_key_a.pk]))
        assert resp.status_code in (301, 302)

    def test_rep_can_view_list_pages(self, rep_client_a):
        """Reps can VIEW (read-only) list pages (decorator only blocks write views)."""
        resp = rep_client_a.get(reverse("tenants:onboardingstep_list"))
        assert resp.status_code == 200


# ============================================================ onboarding steps
@pytest.mark.django_db
class TestOnboardingStepCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("tenants:onboardingstep_list"))
        assert resp.status_code == 200

    def test_list_context_has_steps(self, client_a, onboarding_step_a):
        resp = client_a.get(reverse("tenants:onboardingstep_list"))
        assert "steps" in resp.context

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("tenants:onboardingstep_create"))
        assert resp.status_code == 200

    def test_create_post_creates_step(self, client_a, tenant_a):
        before = OnboardingStep.objects.filter(tenant=tenant_a).count()
        resp = client_a.post(reverse("tenants:onboardingstep_create"), {
            "title": "New Step",
            "description": "Do it",
            "order": 10,
            "status": "pending",
        })
        assert OnboardingStep.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a):
        client_a.post(reverse("tenants:onboardingstep_create"), {
            "title": "Tenant Step",
            "description": "",
            "order": 1,
            "status": "pending",
        })
        step = OnboardingStep.objects.filter(title="Tenant Step").first()
        assert step is not None
        assert step.tenant == tenant_a

    def test_detail_200(self, client_a, onboarding_step_a):
        resp = client_a.get(reverse("tenants:onboardingstep_detail", args=[onboarding_step_a.pk]))
        assert resp.status_code == 200

    def test_edit_get_200(self, client_a, onboarding_step_a):
        resp = client_a.get(reverse("tenants:onboardingstep_edit", args=[onboarding_step_a.pk]))
        assert resp.status_code == 200

    def test_delete_post_deletes(self, client_a, tenant_a):
        step = OnboardingStep.objects.create(tenant=tenant_a, title="ToDelete", order=99)
        resp = client_a.post(reverse("tenants:onboardingstep_delete", args=[step.pk]))
        assert not OnboardingStep.objects.filter(pk=step.pk).exists()

    def test_detail_404_for_other_tenant(self, client_a, onboarding_step_b):
        resp = client_a.get(reverse("tenants:onboardingstep_detail", args=[onboarding_step_b.pk]))
        assert resp.status_code == 404

    def test_edit_404_for_other_tenant(self, client_a, onboarding_step_b):
        resp = client_a.get(reverse("tenants:onboardingstep_edit", args=[onboarding_step_b.pk]))
        assert resp.status_code == 404


# ============================================================ subscriptions
@pytest.mark.django_db
class TestSubscriptionCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("tenants:subscription_list"))
        assert resp.status_code == 200

    def test_list_context_has_subscriptions(self, client_a, subscription_a):
        resp = client_a.get(reverse("tenants:subscription_list"))
        assert "subscriptions" in resp.context

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("tenants:subscription_create"))
        assert resp.status_code == 200

    def test_create_post_creates_subscription(self, client_a, tenant_a):
        from django.utils import timezone
        before = Subscription.objects.filter(tenant=tenant_a).count()
        today = timezone.localdate().isoformat()
        resp = client_a.post(reverse("tenants:subscription_create"), {
            "plan": "pro",
            "status": "active",
            "seats": 10,
            "monthly_amount": "99.00",
            "started_on": today,
            "renews_on": "",
            "is_auto_renew": True,
        })
        assert Subscription.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a):
        from django.utils import timezone
        today = timezone.localdate().isoformat()
        client_a.post(reverse("tenants:subscription_create"), {
            "plan": "enterprise",
            "status": "trialing",
            "seats": 25,
            "monthly_amount": "500.00",
            "started_on": today,
            "renews_on": "",
            "is_auto_renew": False,
        })
        sub = Subscription.objects.filter(tenant=tenant_a, plan="enterprise").first()
        assert sub is not None
        assert sub.tenant == tenant_a

    def test_detail_200(self, client_a, subscription_a):
        resp = client_a.get(reverse("tenants:subscription_detail", args=[subscription_a.pk]))
        assert resp.status_code == 200

    def test_detail_404_for_other_tenant(self, client_a, subscription_b):
        resp = client_a.get(reverse("tenants:subscription_detail", args=[subscription_b.pk]))
        assert resp.status_code == 404

    def test_edit_get_200(self, client_a, subscription_a):
        resp = client_a.get(reverse("tenants:subscription_edit", args=[subscription_a.pk]))
        assert resp.status_code == 200

    def test_edit_404_for_other_tenant(self, client_a, subscription_b):
        resp = client_a.get(reverse("tenants:subscription_edit", args=[subscription_b.pk]))
        assert resp.status_code == 404

    def test_delete_post_deletes(self, client_a, tenant_a):
        from django.utils import timezone
        sub = Subscription.objects.create(tenant=tenant_a, plan=Subscription.PLAN_STARTER)
        resp = client_a.post(reverse("tenants:subscription_delete", args=[sub.pk]))
        assert not Subscription.objects.filter(pk=sub.pk).exists()

    def test_delete_404_for_other_tenant(self, client_a, subscription_b):
        resp = client_a.post(reverse("tenants:subscription_delete", args=[subscription_b.pk]))
        assert resp.status_code == 404


# ============================================================ invoices
@pytest.mark.django_db
class TestInvoiceCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("tenants:invoice_list"))
        assert resp.status_code == 200

    def test_list_context_has_invoices(self, client_a, invoice_a):
        resp = client_a.get(reverse("tenants:invoice_list"))
        assert "invoices" in resp.context

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("tenants:invoice_create"))
        assert resp.status_code == 200

    def test_create_post_creates_invoice(self, client_a, tenant_a):
        from django.utils import timezone
        before = Invoice.objects.filter(tenant=tenant_a).count()
        today = timezone.localdate().isoformat()
        resp = client_a.post(reverse("tenants:invoice_create"), {
            "subscription": "",
            "amount": "199.00",
            "status": "draft",
            "period_start": "",
            "period_end": "",
            "issued_on": today,
            "due_on": "",
            "notes": "",
        })
        assert Invoice.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_auto_numbers_invoice(self, client_a, tenant_a):
        from django.utils import timezone
        today = timezone.localdate().isoformat()
        # Remove existing invoices for clean count
        Invoice.objects.filter(tenant=tenant_a).delete()
        client_a.post(reverse("tenants:invoice_create"), {
            "subscription": "",
            "amount": "50.00",
            "status": "draft",
            "period_start": "",
            "period_end": "",
            "issued_on": today,
            "due_on": "",
            "notes": "",
        })
        inv = Invoice.objects.filter(tenant=tenant_a).latest("created_at")
        assert inv.number.startswith("INV-")

    def test_create_assigns_correct_tenant(self, client_a, tenant_a):
        from django.utils import timezone
        today = timezone.localdate().isoformat()
        client_a.post(reverse("tenants:invoice_create"), {
            "subscription": "",
            "amount": "75.00",
            "status": "draft",
            "period_start": "",
            "period_end": "",
            "issued_on": today,
            "due_on": "",
            "notes": "tenant check",
        })
        inv = Invoice.objects.filter(tenant=tenant_a, notes="tenant check").first()
        assert inv is not None
        assert inv.tenant == tenant_a

    def test_detail_200(self, client_a, invoice_a):
        resp = client_a.get(reverse("tenants:invoice_detail", args=[invoice_a.pk]))
        assert resp.status_code == 200

    def test_detail_404_for_other_tenant(self, client_a, invoice_b):
        resp = client_a.get(reverse("tenants:invoice_detail", args=[invoice_b.pk]))
        assert resp.status_code == 404

    def test_edit_get_200(self, client_a, invoice_a):
        resp = client_a.get(reverse("tenants:invoice_edit", args=[invoice_a.pk]))
        assert resp.status_code == 200

    def test_edit_404_for_other_tenant(self, client_a, invoice_b):
        resp = client_a.get(reverse("tenants:invoice_edit", args=[invoice_b.pk]))
        assert resp.status_code == 404

    def test_delete_post_deletes(self, client_a, tenant_a):
        inv = Invoice.objects.create(tenant=tenant_a, amount="10.00")
        resp = client_a.post(reverse("tenants:invoice_delete", args=[inv.pk]))
        assert not Invoice.objects.filter(pk=inv.pk).exists()

    def test_delete_404_for_other_tenant(self, client_a, invoice_b):
        resp = client_a.post(reverse("tenants:invoice_delete", args=[invoice_b.pk]))
        assert resp.status_code == 404


# ============================================================ encryption keys
@pytest.mark.django_db
class TestEncryptionKeyCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("tenants:encryptionkey_list"))
        assert resp.status_code == 200

    def test_list_context_has_keys(self, client_a, encryption_key_a):
        resp = client_a.get(reverse("tenants:encryptionkey_list"))
        assert "keys" in resp.context

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("tenants:encryptionkey_create"))
        assert resp.status_code == 200

    def test_create_post_creates_key(self, client_a, tenant_a):
        before = EncryptionKey.objects.filter(tenant=tenant_a).count()
        resp = client_a.post(reverse("tenants:encryptionkey_create"), {
            "label": "My New Key",
            "algorithm": "aes-256",
            "status": "active",
        })
        assert EncryptionKey.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_stores_only_prefix_and_hash_not_plaintext(self, client_a, tenant_a):
        """On create, the view generates prefix+hash — plaintext must NOT be stored."""
        resp = client_a.post(reverse("tenants:encryptionkey_create"), {
            "label": "Security Test Key",
            "algorithm": "hmac-sha256",
            "status": "active",
        })
        key = EncryptionKey.objects.filter(tenant=tenant_a, label="Security Test Key").first()
        assert key is not None
        assert key.key_prefix  # prefix should be set
        assert key.hashed_key  # hash should be set
        # The hashed_key should look like a SHA-256 hex digest
        assert len(key.hashed_key) == 64

    def test_create_secret_revealed_once_in_session(self, client_a, tenant_a):
        """After create, the plaintext is in session and shown once on detail."""
        resp = client_a.post(reverse("tenants:encryptionkey_create"), {
            "label": "One Time Key",
            "algorithm": "aes-256",
            "status": "active",
        })
        # Follow redirect to detail page
        detail_resp = client_a.get(resp.url)
        assert detail_resp.status_code == 200
        # plaintext_once should be in context on first visit
        assert detail_resp.context["plaintext_once"] is not None

    def test_secret_gone_on_second_detail_visit(self, client_a, tenant_a):
        """Plaintext is consumed from session on first detail visit; gone on refresh."""
        resp = client_a.post(reverse("tenants:encryptionkey_create"), {
            "label": "Gone Key",
            "algorithm": "aes-256",
            "status": "active",
        })
        detail_url = resp.url
        # First visit: plaintext revealed
        first_resp = client_a.get(detail_url)
        assert first_resp.context["plaintext_once"] is not None
        # Second visit: plaintext gone
        second_resp = client_a.get(detail_url)
        assert second_resp.context["plaintext_once"] is None

    def test_hashed_key_not_in_html_response(self, client_a, tenant_a):
        """The hashed_key value must NEVER appear in the HTML output."""
        resp = client_a.post(reverse("tenants:encryptionkey_create"), {
            "label": "Hash Test Key",
            "algorithm": "aes-256",
            "status": "active",
        })
        key = EncryptionKey.objects.filter(tenant=tenant_a, label="Hash Test Key").first()
        # Check detail page HTML
        detail_resp = client_a.get(resp.url)
        content = detail_resp.content.decode()
        assert key.hashed_key not in content

    def test_detail_200(self, client_a, encryption_key_a):
        resp = client_a.get(reverse("tenants:encryptionkey_detail", args=[encryption_key_a.pk]))
        assert resp.status_code == 200

    def test_detail_404_for_other_tenant(self, client_a, encryption_key_b):
        resp = client_a.get(reverse("tenants:encryptionkey_detail", args=[encryption_key_b.pk]))
        assert resp.status_code == 404

    def test_edit_get_200(self, client_a, encryption_key_a):
        resp = client_a.get(reverse("tenants:encryptionkey_edit", args=[encryption_key_a.pk]))
        assert resp.status_code == 200

    def test_edit_404_for_other_tenant(self, client_a, encryption_key_b):
        resp = client_a.get(reverse("tenants:encryptionkey_edit", args=[encryption_key_b.pk]))
        assert resp.status_code == 404

    def test_rotate_post_changes_prefix_and_hash(self, client_a, encryption_key_a):
        old_prefix = encryption_key_a.key_prefix
        old_hash = encryption_key_a.hashed_key
        resp = client_a.post(reverse("tenants:encryptionkey_rotate", args=[encryption_key_a.pk]))
        encryption_key_a.refresh_from_db()
        assert encryption_key_a.key_prefix != old_prefix
        assert encryption_key_a.hashed_key != old_hash

    def test_rotate_404_for_other_tenant(self, client_a, encryption_key_b):
        resp = client_a.post(reverse("tenants:encryptionkey_rotate", args=[encryption_key_b.pk]))
        assert resp.status_code == 404

    def test_delete_post_deletes(self, client_a, tenant_a):
        _, prefix, hashed = EncryptionKey.generate_secret()
        key = EncryptionKey.objects.create(tenant=tenant_a, label="TDKey", key_prefix=prefix, hashed_key=hashed)
        resp = client_a.post(reverse("tenants:encryptionkey_delete", args=[key.pk]))
        assert not EncryptionKey.objects.filter(pk=key.pk).exists()

    def test_delete_404_for_other_tenant(self, client_a, encryption_key_b):
        resp = client_a.post(reverse("tenants:encryptionkey_delete", args=[encryption_key_b.pk]))
        assert resp.status_code == 404


# ============================================================ branding
@pytest.mark.django_db
class TestBrandingSettingCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("tenants:brandingsetting_list"))
        assert resp.status_code == 200

    def test_list_context_has_profiles(self, client_a, branding_a):
        resp = client_a.get(reverse("tenants:brandingsetting_list"))
        assert "profiles" in resp.context

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("tenants:brandingsetting_create"))
        assert resp.status_code == 200

    def test_create_post_creates_branding(self, client_a, tenant_a):
        before = BrandingSetting.objects.filter(tenant=tenant_a).count()
        resp = client_a.post(reverse("tenants:brandingsetting_create"), {
            "name": "New Brand",
            "is_default": False,
            "logo_url": "",
            "primary_color": "#123abc",
            "accent_color": "#0ea5e9",
            "login_message": "",
            "email_from_name": "",
            "email_signature": "",
            "theme": "light",
        })
        assert BrandingSetting.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_rejects_invalid_hex_color(self, client_a, tenant_a):
        before = BrandingSetting.objects.filter(tenant=tenant_a).count()
        resp = client_a.post(reverse("tenants:brandingsetting_create"), {
            "name": "Bad Color Brand",
            "is_default": False,
            "logo_url": "",
            "primary_color": "not-a-hex",
            "accent_color": "#0ea5e9",
            "login_message": "",
            "email_from_name": "",
            "email_signature": "",
            "theme": "light",
        })
        # Form should be invalid — no new object created
        assert BrandingSetting.objects.filter(tenant=tenant_a).count() == before

    def test_detail_200(self, client_a, branding_a):
        resp = client_a.get(reverse("tenants:brandingsetting_detail", args=[branding_a.pk]))
        assert resp.status_code == 200

    def test_detail_404_for_other_tenant(self, client_a, branding_b):
        resp = client_a.get(reverse("tenants:brandingsetting_detail", args=[branding_b.pk]))
        assert resp.status_code == 404

    def test_edit_get_200(self, client_a, branding_a):
        resp = client_a.get(reverse("tenants:brandingsetting_edit", args=[branding_a.pk]))
        assert resp.status_code == 200

    def test_edit_404_for_other_tenant(self, client_a, branding_b):
        resp = client_a.get(reverse("tenants:brandingsetting_edit", args=[branding_b.pk]))
        assert resp.status_code == 404

    def test_delete_post_deletes(self, client_a, tenant_a):
        b = BrandingSetting.objects.create(tenant=tenant_a, name="ToDelete Brand")
        resp = client_a.post(reverse("tenants:brandingsetting_delete", args=[b.pk]))
        assert not BrandingSetting.objects.filter(pk=b.pk).exists()

    def test_delete_404_for_other_tenant(self, client_a, branding_b):
        resp = client_a.post(reverse("tenants:brandingsetting_delete", args=[branding_b.pk]))
        assert resp.status_code == 404


# ============================================================ health metrics
@pytest.mark.django_db
class TestHealthMetricCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("tenants:healthmetric_list"))
        assert resp.status_code == 200

    def test_list_context_has_metrics(self, client_a, healthmetric_a):
        resp = client_a.get(reverse("tenants:healthmetric_list"))
        assert "metrics" in resp.context

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("tenants:healthmetric_create"))
        assert resp.status_code == 200

    def test_create_post_creates_metric(self, client_a, tenant_a):
        before = HealthMetric.objects.filter(tenant=tenant_a).count()
        resp = client_a.post(reverse("tenants:healthmetric_create"), {
            "metric_name": "Disk Usage",
            "category": "resource",
            "value": "55.5",
            "unit": "%",
            "threshold": "80.0",
            "status": "ok",
        })
        assert HealthMetric.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a):
        client_a.post(reverse("tenants:healthmetric_create"), {
            "metric_name": "Tenant Check Metric",
            "category": "usage",
            "value": "30.0",
            "unit": "GB",
            "threshold": "",
            "status": "ok",
        })
        metric = HealthMetric.objects.filter(metric_name="Tenant Check Metric").first()
        assert metric is not None
        assert metric.tenant == tenant_a

    def test_detail_200(self, client_a, healthmetric_a):
        resp = client_a.get(reverse("tenants:healthmetric_detail", args=[healthmetric_a.pk]))
        assert resp.status_code == 200

    def test_detail_404_for_other_tenant(self, client_a, healthmetric_b):
        resp = client_a.get(reverse("tenants:healthmetric_detail", args=[healthmetric_b.pk]))
        assert resp.status_code == 404

    def test_edit_get_200(self, client_a, healthmetric_a):
        resp = client_a.get(reverse("tenants:healthmetric_edit", args=[healthmetric_a.pk]))
        assert resp.status_code == 200

    def test_edit_404_for_other_tenant(self, client_a, healthmetric_b):
        resp = client_a.get(reverse("tenants:healthmetric_edit", args=[healthmetric_b.pk]))
        assert resp.status_code == 404

    def test_delete_post_deletes(self, client_a, tenant_a):
        m = HealthMetric.objects.create(tenant=tenant_a, metric_name="ToDelete Metric", value="10")
        resp = client_a.post(reverse("tenants:healthmetric_delete", args=[m.pk]))
        assert not HealthMetric.objects.filter(pk=m.pk).exists()

    def test_delete_404_for_other_tenant(self, client_a, healthmetric_b):
        resp = client_a.post(reverse("tenants:healthmetric_delete", args=[healthmetric_b.pk]))
        assert resp.status_code == 404
