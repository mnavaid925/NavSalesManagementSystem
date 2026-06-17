from django.contrib import admin

from .models import (
    BrandingSetting, EncryptionKey, HealthMetric, Invoice, OnboardingStep, Subscription,
)


@admin.register(OnboardingStep)
class OnboardingStepAdmin(admin.ModelAdmin):
    list_display = ("title", "tenant", "order", "status", "completed_at")
    list_filter = ("tenant", "status")
    search_fields = ("title", "description")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("tenant", "plan", "status", "seats", "monthly_amount", "started_on", "renews_on")
    list_filter = ("tenant", "plan", "status")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("number", "tenant", "amount", "status", "issued_on", "due_on", "paid_at")
    list_filter = ("tenant", "status")
    search_fields = ("number", "notes")
    readonly_fields = ("number", "paid_at")


@admin.register(EncryptionKey)
class EncryptionKeyAdmin(admin.ModelAdmin):
    list_display = ("label", "tenant", "algorithm", "status", "key_prefix", "created_at")
    list_filter = ("tenant", "algorithm", "status")
    search_fields = ("label",)
    # Never expose the hash for editing; prefix/hash are system-managed.
    readonly_fields = ("key_prefix", "hashed_key", "last_rotated_at")


@admin.register(BrandingSetting)
class BrandingSettingAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "is_default", "theme", "primary_color")
    list_filter = ("tenant", "theme", "is_default")
    search_fields = ("name",)


@admin.register(HealthMetric)
class HealthMetricAdmin(admin.ModelAdmin):
    list_display = ("metric_name", "tenant", "category", "value", "unit", "status", "recorded_at")
    list_filter = ("tenant", "category", "status")
    search_fields = ("metric_name",)
