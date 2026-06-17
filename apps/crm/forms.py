from django import forms

from apps.core.forms import StyledFormMixin

from .models import Account, AccountPlan, AccountTier, Contact, RelationshipMap

DATE = forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")


class AccountTierForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = AccountTier
        fields = ["name", "segment", "rank", "min_annual_value", "color", "description", "is_active"]
        widgets = {"color": forms.TextInput(attrs={"type": "color"})}


class AccountForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Account
        # `number` is auto-generated (off the form).
        fields = ["name", "parent", "tier", "account_type", "status", "industry",
                  "website", "phone", "billing_city", "billing_country",
                  "employee_count", "annual_revenue", "description"]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Always scope FK choices to the tenant; never fall back to .all() (no cross-tenant leak).
        parent_qs = Account.objects.filter(tenant=tenant) if tenant is not None else Account.objects.none()
        # Don't let an account be its own parent on edit.
        if self.instance and self.instance.pk:
            parent_qs = parent_qs.exclude(pk=self.instance.pk)
        self.fields["parent"].queryset = parent_qs
        self.fields["parent"].required = False
        self.fields["tier"].queryset = (
            AccountTier.objects.filter(tenant=tenant) if tenant is not None else AccountTier.objects.none()
        )
        self.fields["tier"].required = False


class ContactForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Contact
        fields = ["first_name", "last_name", "account", "title", "department",
                  "email", "phone", "mobile", "linkedin_url",
                  "status", "enrichment_status", "is_primary", "notes"]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["account"].queryset = (
            Account.objects.filter(tenant=tenant) if tenant is not None else Account.objects.none()
        )
        self.fields["account"].required = False


class RelationshipMapForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = RelationshipMap
        fields = ["account", "from_contact", "to_contact", "relationship_type", "strength", "notes"]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        account_qs = Account.objects.filter(tenant=tenant) if tenant is not None else Account.objects.none()
        contact_qs = Contact.objects.filter(tenant=tenant) if tenant is not None else Contact.objects.none()
        self.fields["account"].queryset = account_qs
        self.fields["account"].required = False
        self.fields["from_contact"].queryset = contact_qs
        self.fields["to_contact"].queryset = contact_qs

    def clean(self):
        cleaned = super().clean()
        from_contact = cleaned.get("from_contact")
        to_contact = cleaned.get("to_contact")
        if from_contact and to_contact and from_contact == to_contact:
            raise forms.ValidationError("A contact cannot have a relationship with itself.")
        return cleaned


class AccountPlanForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = AccountPlan
        # `number` is auto-generated; `approved_at` is system-set (off the form).
        fields = ["account", "title", "fiscal_year", "status", "priority",
                  "objective", "growth_strategy", "target_revenue", "current_revenue",
                  "start_date", "end_date"]
        widgets = {"start_date": DATE, "end_date": DATE}

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["account"].queryset = (
            Account.objects.filter(tenant=tenant) if tenant is not None else Account.objects.none()
        )
