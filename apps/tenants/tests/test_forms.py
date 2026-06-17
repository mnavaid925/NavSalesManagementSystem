"""Tests for tenants.forms: each form's required fields and field exclusions."""
import pytest

from apps.tenants.forms import (
    BrandingSettingForm, EncryptionKeyForm, HealthMetricForm,
    InvoiceForm, OnboardingStepForm, SubscriptionForm,
)


@pytest.mark.django_db
class TestOnboardingStepForm:
    def test_valid_form(self):
        form = OnboardingStepForm(data={
            "title": "Setup Profile",
            "description": "Do the thing.",
            "order": 1,
            "status": "pending",
        })
        assert form.is_valid(), form.errors

    def test_missing_title_invalid(self):
        form = OnboardingStepForm(data={"order": 1, "status": "pending"})
        assert not form.is_valid()

    def test_tenant_not_in_form_fields(self):
        form = OnboardingStepForm()
        assert "tenant" not in form.fields

    def test_completed_at_not_in_form_fields(self):
        """completed_at is system-set, not a form field."""
        form = OnboardingStepForm()
        assert "completed_at" not in form.fields


@pytest.mark.django_db
class TestSubscriptionForm:
    def test_valid_form(self):
        from django.utils import timezone
        today = timezone.localdate().isoformat()
        form = SubscriptionForm(data={
            "plan": "starter",
            "status": "trialing",
            "seats": 5,
            "monthly_amount": "0.00",
            "started_on": today,
            "renews_on": "",
            "is_auto_renew": True,
        })
        assert form.is_valid(), form.errors

    def test_tenant_not_in_form_fields(self):
        form = SubscriptionForm()
        assert "tenant" not in form.fields

    def test_invalid_plan_invalid(self):
        form = SubscriptionForm(data={"plan": "invalid_plan", "status": "active", "seats": 5})
        assert not form.is_valid()


@pytest.mark.django_db
class TestInvoiceForm:
    def test_valid_form(self, tenant_a):
        from django.utils import timezone
        today = timezone.localdate().isoformat()
        form = InvoiceForm(data={
            "subscription": "",
            "amount": "100.00",
            "status": "draft",
            "period_start": "",
            "period_end": "",
            "issued_on": today,
            "due_on": "",
            "notes": "",
        }, tenant=tenant_a)
        assert form.is_valid(), form.errors

    def test_number_not_in_form_fields(self, tenant_a):
        """number is auto-generated, should not be in the form."""
        form = InvoiceForm(tenant=tenant_a)
        assert "number" not in form.fields

    def test_tenant_not_in_form_fields(self, tenant_a):
        form = InvoiceForm(tenant=tenant_a)
        assert "tenant" not in form.fields

    def test_paid_at_not_in_form_fields(self, tenant_a):
        """paid_at is system-set, not a form field."""
        form = InvoiceForm(tenant=tenant_a)
        assert "paid_at" not in form.fields

    def test_subscription_scoped_to_tenant(self, tenant_a, tenant_b, subscription_a, subscription_b):
        form = InvoiceForm(tenant=tenant_a)
        sub_pks = [s.pk for s in form.fields["subscription"].queryset]
        assert subscription_a.pk in sub_pks
        assert subscription_b.pk not in sub_pks


@pytest.mark.django_db
class TestEncryptionKeyForm:
    def test_valid_form(self):
        form = EncryptionKeyForm(data={
            "label": "My API Key",
            "algorithm": "aes-256",
            "status": "active",
        })
        assert form.is_valid(), form.errors

    def test_key_prefix_not_in_form_fields(self):
        """key_prefix is set by the view, not the form."""
        form = EncryptionKeyForm()
        assert "key_prefix" not in form.fields

    def test_hashed_key_not_in_form_fields(self):
        """hashed_key is set by the view, not the form."""
        form = EncryptionKeyForm()
        assert "hashed_key" not in form.fields

    def test_tenant_not_in_form_fields(self):
        form = EncryptionKeyForm()
        assert "tenant" not in form.fields

    def test_missing_label_invalid(self):
        form = EncryptionKeyForm(data={"algorithm": "aes-256", "status": "active"})
        assert not form.is_valid()


@pytest.mark.django_db
class TestBrandingSettingForm:
    def test_valid_form(self):
        form = BrandingSettingForm(data={
            "name": "Default",
            "is_default": False,
            "logo_url": "",
            "primary_color": "#2563eb",
            "accent_color": "#0ea5e9",
            "login_message": "",
            "email_from_name": "",
            "email_signature": "",
            "theme": "light",
        })
        assert form.is_valid(), form.errors

    def test_invalid_hex_color_invalid(self):
        """Non-hex color should fail validation."""
        form = BrandingSettingForm(data={
            "name": "Bad Color",
            "is_default": False,
            "logo_url": "",
            "primary_color": "not-a-color",
            "accent_color": "#0ea5e9",
            "login_message": "",
            "email_from_name": "",
            "email_signature": "",
            "theme": "light",
        })
        assert not form.is_valid()
        assert "primary_color" in form.errors

    def test_tenant_not_in_form_fields(self):
        form = BrandingSettingForm()
        assert "tenant" not in form.fields


@pytest.mark.django_db
class TestHealthMetricForm:
    def test_valid_form(self):
        form = HealthMetricForm(data={
            "metric_name": "CPU Load",
            "category": "resource",
            "value": "75.5",
            "unit": "%",
            "threshold": "90.0",
            "status": "ok",
        })
        assert form.is_valid(), form.errors

    def test_tenant_not_in_form_fields(self):
        form = HealthMetricForm()
        assert "tenant" not in form.fields

    def test_recorded_at_not_in_form_fields(self):
        """recorded_at is system-set, not a form field."""
        form = HealthMetricForm()
        assert "recorded_at" not in form.fields

    def test_missing_metric_name_invalid(self):
        form = HealthMetricForm(data={"category": "resource", "value": "50", "status": "ok"})
        assert not form.is_valid()
