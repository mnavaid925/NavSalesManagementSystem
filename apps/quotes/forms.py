from django import forms

from apps.core.forms import StyledFormMixin

from .models import PricingRule, Proposal, Quote, QuoteLineItem, QuoteVersion

DATE = forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")


class QuoteForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Quote
        # `number` is auto-generated; `sent_at`/`converted_at` are system-set (off the form).
        fields = [
            "title", "account_name", "contact_name", "contact_email", "status",
            "currency", "subtotal", "discount_amount", "tax_amount", "total_amount",
            "valid_until", "notes",
        ]
        widgets = {"valid_until": DATE}


class QuoteLineItemForm(StyledFormMixin, forms.ModelForm):
    # `line_total` is computed in the model's save() — kept off the form.
    class Meta:
        model = QuoteLineItem
        fields = [
            "quote", "product_name", "sku", "description", "unit",
            "quantity", "unit_price", "discount_percent", "position",
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Always scope to the tenant; never fall back to .all() (no cross-tenant leak).
        self.fields["quote"].queryset = (
            Quote.objects.filter(tenant=tenant) if tenant is not None
            else Quote.objects.none()
        )


class PricingRuleForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = PricingRule
        fields = [
            "name", "rule_type", "description", "min_discount_percent",
            "max_discount_percent", "approval_level", "status", "priority",
        ]


class ProposalForm(StyledFormMixin, forms.ModelForm):
    # `sent_at` is system-set (off the form).
    class Meta:
        model = Proposal
        fields = [
            "quote", "title", "template", "status", "executive_summary",
            "body", "cover_letter", "prepared_by",
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Always scope to the tenant; never fall back to .all() (no cross-tenant leak).
        self.fields["quote"].queryset = (
            Quote.objects.filter(tenant=tenant) if tenant is not None
            else Quote.objects.none()
        )
        self.fields["quote"].required = False


class QuoteVersionForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = QuoteVersion
        fields = [
            "quote", "version_number", "change_type", "change_summary",
            "total_amount", "is_current", "snapshot_notes",
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Always scope to the tenant; never fall back to .all() (no cross-tenant leak).
        self.fields["quote"].queryset = (
            Quote.objects.filter(tenant=tenant) if tenant is not None
            else Quote.objects.none()
        )
