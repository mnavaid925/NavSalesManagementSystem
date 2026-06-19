from django import forms

from apps.core.forms import StyledFormMixin

from .models import (
    CustomField, LocalizationSetting, MethodologyConfig, PriceBook, ProductCatalog,
)

DATE = forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")


class ProductCatalogForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ProductCatalog
        fields = ["name", "sku", "category", "status", "unit_price",
                  "cost", "currency", "description"]


class CustomFieldForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = CustomField
        fields = ["name", "field_key", "object_type", "field_type", "status",
                  "required", "default_value", "help_text", "notes"]


class MethodologyConfigForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = MethodologyConfig
        fields = ["name", "methodology", "status", "stages_count",
                  "qualification_fields", "is_default", "description"]


class PriceBookForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = PriceBook
        fields = ["name", "currency", "status", "region", "is_default",
                  "valid_from", "valid_to", "description"]
        widgets = {"valid_from": DATE, "valid_to": DATE}


class LocalizationSettingForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = LocalizationSetting
        fields = ["language_code", "language_name", "locale", "status",
                  "is_default", "date_format", "number_format", "currency",
                  "completion_pct", "notes"]
