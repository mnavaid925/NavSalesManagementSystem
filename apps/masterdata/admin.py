from django.contrib import admin

from .models import (
    CustomField, LocalizationSetting, MethodologyConfig, PriceBook, ProductCatalog,
)


@admin.register(ProductCatalog)
class ProductCatalogAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "sku", "category", "status", "unit_price", "currency")
    list_filter = ("tenant", "category", "status")
    search_fields = ("name", "sku", "description")


@admin.register(CustomField)
class CustomFieldAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "field_key", "object_type", "field_type", "status", "required")
    list_filter = ("tenant", "object_type", "field_type", "status")
    search_fields = ("name", "field_key")


@admin.register(MethodologyConfig)
class MethodologyConfigAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "methodology", "status", "stages_count", "is_default")
    list_filter = ("tenant", "methodology", "status")
    search_fields = ("name", "description")


@admin.register(PriceBook)
class PriceBookAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "currency", "status", "region", "is_default", "valid_from")
    list_filter = ("tenant", "status", "currency")
    search_fields = ("name", "region", "description")


@admin.register(LocalizationSetting)
class LocalizationSettingAdmin(admin.ModelAdmin):
    list_display = ("language_name", "tenant", "language_code", "locale", "status", "is_default")
    list_filter = ("tenant", "status")
    search_fields = ("language_code", "language_name", "locale")
