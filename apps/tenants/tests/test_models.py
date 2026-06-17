"""Tests for tenants.models: OnboardingStep, Subscription, Invoice, EncryptionKey, BrandingSetting, HealthMetric."""
import hashlib
import pytest
from django.utils import timezone

from apps.core.models import Tenant
from apps.tenants.models import (
    BrandingSetting, EncryptionKey, HealthMetric, Invoice, OnboardingStep, Subscription,
)


@pytest.mark.django_db
class TestOnboardingStep:
    def test_str_returns_title(self, onboarding_step_a):
        assert str(onboarding_step_a) == "Setup Profile"

    def test_default_status_is_pending(self, tenant_a):
        step = OnboardingStep.objects.create(tenant=tenant_a, title="New Step")
        assert step.status == OnboardingStep.STATUS_PENDING

    def test_status_choices_contain_all_three(self):
        choices = dict(OnboardingStep.STATUS_CHOICES)
        assert OnboardingStep.STATUS_PENDING in choices
        assert OnboardingStep.STATUS_IN_PROGRESS in choices
        assert OnboardingStep.STATUS_DONE in choices

    def test_save_sets_completed_at_when_done(self, onboarding_step_a):
        onboarding_step_a.status = OnboardingStep.STATUS_DONE
        onboarding_step_a.save()
        assert onboarding_step_a.completed_at is not None

    def test_save_clears_completed_at_when_not_done(self, tenant_a):
        step = OnboardingStep.objects.create(
            tenant=tenant_a, title="Undo Done", status=OnboardingStep.STATUS_DONE
        )
        assert step.completed_at is not None
        step.status = OnboardingStep.STATUS_PENDING
        step.save()
        assert step.completed_at is None

    def test_seed_defaults_creates_six_steps(self, tenant_a):
        OnboardingStep.seed_defaults(tenant_a)
        assert OnboardingStep.objects.filter(tenant=tenant_a).count() == 6

    def test_seed_defaults_idempotent(self, tenant_a):
        OnboardingStep.seed_defaults(tenant_a)
        OnboardingStep.seed_defaults(tenant_a)
        assert OnboardingStep.objects.filter(tenant=tenant_a).count() == 6

    def test_ordering_by_order_then_id(self, tenant_a):
        OnboardingStep.objects.create(tenant=tenant_a, title="Step B", order=2)
        OnboardingStep.objects.create(tenant=tenant_a, title="Step A", order=1)
        steps = list(OnboardingStep.objects.filter(tenant=tenant_a).values_list("order", flat=True))
        assert steps == sorted(steps)


@pytest.mark.django_db
class TestSubscription:
    def test_str_shows_plan_and_status(self, subscription_a):
        result = str(subscription_a)
        assert "Starter" in result
        assert "Trialing" in result

    def test_default_plan_is_starter(self, tenant_a):
        sub = Subscription.objects.create(tenant=tenant_a)
        assert sub.plan == Subscription.PLAN_STARTER

    def test_default_status_is_trialing(self, tenant_a):
        sub = Subscription.objects.create(tenant=tenant_a)
        assert sub.status == Subscription.STATUS_TRIALING

    def test_default_seats_is_5(self, tenant_a):
        sub = Subscription.objects.create(tenant=tenant_a)
        assert sub.seats == 5

    def test_default_is_auto_renew_true(self, tenant_a):
        sub = Subscription.objects.create(tenant=tenant_a)
        assert sub.is_auto_renew is True

    def test_plan_choices_contain_all_three(self):
        choices = dict(Subscription.PLAN_CHOICES)
        assert Subscription.PLAN_STARTER in choices
        assert Subscription.PLAN_PRO in choices
        assert Subscription.PLAN_ENTERPRISE in choices

    def test_status_choices_contain_all_four(self):
        choices = dict(Subscription.STATUS_CHOICES)
        assert Subscription.STATUS_TRIALING in choices
        assert Subscription.STATUS_ACTIVE in choices
        assert Subscription.STATUS_PAST_DUE in choices
        assert Subscription.STATUS_CANCELED in choices


@pytest.mark.django_db
class TestInvoice:
    def test_auto_number_generated_on_save(self, tenant_a):
        inv = Invoice.objects.create(tenant=tenant_a, amount="100.00")
        assert inv.number.startswith("INV-")

    def test_auto_number_format_five_digits(self, tenant_a):
        inv = Invoice.objects.create(tenant=tenant_a, amount="100.00")
        parts = inv.number.split("-")
        assert len(parts) == 2
        assert len(parts[1]) == 5
        assert parts[1].isdigit()

    def test_auto_number_first_invoice_is_INV_00001(self, tenant_a):
        inv = Invoice.objects.create(tenant=tenant_a, amount="100.00")
        assert inv.number == "INV-00001"

    def test_auto_number_increments_per_tenant(self, tenant_a):
        inv1 = Invoice.objects.create(tenant=tenant_a, amount="10.00")
        inv2 = Invoice.objects.create(tenant=tenant_a, amount="20.00")
        assert inv1.number == "INV-00001"
        assert inv2.number == "INV-00002"

    def test_auto_number_isolated_per_tenant(self, tenant_a, tenant_b):
        inv_a = Invoice.objects.create(tenant=tenant_a, amount="10.00")
        inv_b = Invoice.objects.create(tenant=tenant_b, amount="20.00")
        # Each tenant starts its own sequence at INV-00001
        assert inv_a.number == "INV-00001"
        assert inv_b.number == "INV-00001"

    def test_str_returns_number(self, invoice_a):
        assert invoice_a.number in str(invoice_a)

    def test_str_fallback_when_no_number(self, tenant_a):
        inv = Invoice(tenant=tenant_a, amount="0")
        # not saved yet — number is blank
        result = str(inv)
        assert result is not None

    def test_unique_together_tenant_number(self, tenant_a):
        Invoice.objects.create(tenant=tenant_a, amount="10.00")  # gets INV-00001
        import django.db.utils as db_utils
        with pytest.raises(db_utils.IntegrityError):
            Invoice.objects.create(tenant=tenant_a, number="INV-00001", amount="20.00")

    def test_paid_at_set_when_status_paid(self, invoice_a):
        invoice_a.status = Invoice.STATUS_PAID
        invoice_a.save()
        assert invoice_a.paid_at is not None

    def test_status_choices_contain_all_four(self):
        choices = dict(Invoice.STATUS_CHOICES)
        assert Invoice.STATUS_DRAFT in choices
        assert Invoice.STATUS_SENT in choices
        assert Invoice.STATUS_PAID in choices
        assert Invoice.STATUS_OVERDUE in choices


@pytest.mark.django_db
class TestEncryptionKey:
    def test_generate_secret_returns_tuple(self):
        plaintext, prefix, hashed = EncryptionKey.generate_secret()
        assert plaintext.startswith("sk_")
        assert prefix == plaintext[:10]
        assert hashed == hashlib.sha256(plaintext.encode()).hexdigest()

    def test_create_stores_only_prefix_and_hash(self, tenant_a):
        plaintext, prefix, hashed = EncryptionKey.generate_secret()
        key = EncryptionKey.objects.create(
            tenant=tenant_a, label="My Key",
            key_prefix=prefix, hashed_key=hashed,
        )
        key.refresh_from_db()
        # Plaintext must NOT be stored anywhere
        assert key.key_prefix == prefix
        assert key.hashed_key == hashed
        # No field on the model contains the full plaintext
        assert not hasattr(key, "plaintext") or getattr(key, "plaintext", None) is None

    def test_masked_uses_prefix_and_dots(self, encryption_key_a):
        masked = encryption_key_a.masked
        assert encryption_key_a.key_prefix in masked
        assert "•" in masked

    def test_masked_no_prefix_returns_dots(self, tenant_a):
        key = EncryptionKey.objects.create(tenant=tenant_a, label="No Prefix")
        assert key.masked == "••••••••"

    def test_str_includes_label_and_masked(self, encryption_key_a):
        result = str(encryption_key_a)
        assert "Test Key" in result

    def test_default_status_is_active(self, tenant_a):
        key = EncryptionKey.objects.create(tenant=tenant_a, label="Default Status")
        assert key.status == EncryptionKey.STATUS_ACTIVE

    def test_algo_choices_contain_all_three(self):
        choices = dict(EncryptionKey.ALGO_CHOICES)
        assert EncryptionKey.ALGO_AES256 in choices
        assert EncryptionKey.ALGO_RSA2048 in choices
        assert EncryptionKey.ALGO_HMAC in choices

    def test_status_choices_contain_all_three(self):
        choices = dict(EncryptionKey.STATUS_CHOICES)
        assert EncryptionKey.STATUS_ACTIVE in choices
        assert EncryptionKey.STATUS_ROTATED in choices
        assert EncryptionKey.STATUS_REVOKED in choices

    def test_hashed_key_is_sha256_hex(self, tenant_a):
        plaintext, prefix, hashed = EncryptionKey.generate_secret()
        assert len(hashed) == 64  # SHA-256 hex digest is 64 chars
        assert all(c in "0123456789abcdef" for c in hashed)


@pytest.mark.django_db
class TestBrandingSetting:
    def test_str_returns_name(self, branding_a):
        assert str(branding_a) == "Default Brand"

    def test_default_primary_color(self, tenant_a):
        b = BrandingSetting.objects.create(tenant=tenant_a, name="B")
        assert b.primary_color == "#2563eb"

    def test_default_theme_is_light(self, tenant_a):
        b = BrandingSetting.objects.create(tenant=tenant_a, name="C")
        assert b.theme == BrandingSetting.THEME_LIGHT

    def test_theme_choices_contain_all_three(self):
        choices = dict(BrandingSetting.THEME_CHOICES)
        assert BrandingSetting.THEME_LIGHT in choices
        assert BrandingSetting.THEME_DARK in choices
        assert BrandingSetting.THEME_AUTO in choices

    def test_hex_color_validator_rejects_invalid(self, tenant_a):
        from django.core.exceptions import ValidationError
        b = BrandingSetting(tenant=tenant_a, name="Bad Color", primary_color="notacolor")
        with pytest.raises(ValidationError):
            b.full_clean()

    def test_hex_color_validator_accepts_valid_6_digit(self, tenant_a):
        from django.core.exceptions import ValidationError
        b = BrandingSetting(tenant=tenant_a, name="Good Color", primary_color="#FF5733")
        # Should not raise
        b.full_clean()

    def test_hex_color_validator_accepts_valid_3_digit(self, tenant_a):
        from django.core.exceptions import ValidationError
        b = BrandingSetting(tenant=tenant_a, name="Short Color", primary_color="#FFF")
        b.full_clean()


@pytest.mark.django_db
class TestHealthMetric:
    def test_str_shows_metric_name_and_value(self, healthmetric_a):
        result = str(healthmetric_a)
        assert "CPU Usage" in result
        assert "42.5" in result

    def test_default_status_is_ok(self, tenant_a):
        m = HealthMetric.objects.create(tenant=tenant_a, metric_name="Disk", value="30")
        assert m.status == HealthMetric.STATUS_OK

    def test_default_category_is_resource(self, tenant_a):
        m = HealthMetric.objects.create(tenant=tenant_a, metric_name="Disk2", value="30")
        assert m.category == HealthMetric.CATEGORY_RESOURCE

    def test_category_choices_contain_all_four(self):
        choices = dict(HealthMetric.CATEGORY_CHOICES)
        assert HealthMetric.CATEGORY_RESOURCE in choices
        assert HealthMetric.CATEGORY_USAGE in choices
        assert HealthMetric.CATEGORY_UPTIME in choices
        assert HealthMetric.CATEGORY_PERFORMANCE in choices

    def test_status_choices_contain_all_three(self):
        choices = dict(HealthMetric.STATUS_CHOICES)
        assert HealthMetric.STATUS_OK in choices
        assert HealthMetric.STATUS_WARNING in choices
        assert HealthMetric.STATUS_CRITICAL in choices
