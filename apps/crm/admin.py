from django.contrib import admin

from .models import Account, AccountPlan, AccountTier, Contact, RelationshipMap


@admin.register(AccountTier)
class AccountTierAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "segment", "rank", "min_annual_value", "is_active")
    list_filter = ("tenant", "segment", "is_active")
    search_fields = ("name", "description")


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("number", "name", "tenant", "account_type", "status", "tier", "parent", "annual_revenue")
    list_filter = ("tenant", "account_type", "status", "tier")
    search_fields = ("number", "name", "industry", "billing_city")
    readonly_fields = ("number",)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "tenant", "account", "title", "email", "status", "enrichment_status")
    list_filter = ("tenant", "status", "enrichment_status", "is_primary")
    search_fields = ("first_name", "last_name", "email", "title")


@admin.register(RelationshipMap)
class RelationshipMapAdmin(admin.ModelAdmin):
    list_display = ("from_contact", "to_contact", "tenant", "account", "relationship_type", "strength")
    list_filter = ("tenant", "relationship_type", "strength")
    search_fields = ("from_contact__first_name", "from_contact__last_name",
                     "to_contact__first_name", "to_contact__last_name", "notes")


@admin.register(AccountPlan)
class AccountPlanAdmin(admin.ModelAdmin):
    list_display = ("number", "title", "tenant", "account", "fiscal_year", "status", "priority", "target_revenue")
    list_filter = ("tenant", "status", "priority", "fiscal_year")
    search_fields = ("number", "title", "objective")
    readonly_fields = ("number", "approved_at")
