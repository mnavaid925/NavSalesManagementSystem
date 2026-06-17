from django.contrib import admin

from .models import PricingRule, Proposal, Quote, QuoteLineItem, QuoteVersion


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ("number", "tenant", "title", "account_name", "status", "currency", "total_amount", "valid_until")
    list_filter = ("tenant", "status", "currency")
    search_fields = ("number", "title", "account_name", "contact_name", "contact_email")
    readonly_fields = ("number", "sent_at", "converted_at")


@admin.register(QuoteLineItem)
class QuoteLineItemAdmin(admin.ModelAdmin):
    list_display = ("product_name", "tenant", "quote", "unit", "quantity", "unit_price", "discount_percent", "line_total")
    list_filter = ("tenant", "unit")
    search_fields = ("product_name", "sku", "description")
    readonly_fields = ("line_total",)


@admin.register(PricingRule)
class PricingRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "rule_type", "approval_level", "min_discount_percent", "max_discount_percent", "status", "priority")
    list_filter = ("tenant", "rule_type", "approval_level", "status")
    search_fields = ("name", "description")


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ("title", "tenant", "quote", "template", "status", "prepared_by", "sent_at")
    list_filter = ("tenant", "template", "status")
    search_fields = ("title", "prepared_by", "executive_summary")
    readonly_fields = ("sent_at",)


@admin.register(QuoteVersion)
class QuoteVersionAdmin(admin.ModelAdmin):
    list_display = ("quote", "tenant", "version_number", "change_type", "total_amount", "is_current", "created_at")
    list_filter = ("tenant", "change_type", "is_current")
    search_fields = ("change_summary", "snapshot_notes")
