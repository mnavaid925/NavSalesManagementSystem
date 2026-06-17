from django.contrib import admin

from .models import Fulfillment, Order, OrderAmendment, OrderLine, RevenueSchedule


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("number", "tenant", "customer_name", "channel", "status",
                    "total_amount", "order_date", "confirmed_at")
    list_filter = ("tenant", "status", "channel")
    search_fields = ("number", "customer_name", "customer_email", "notes")
    readonly_fields = ("number", "confirmed_at")


@admin.register(OrderLine)
class OrderLineAdmin(admin.ModelAdmin):
    list_display = ("product_name", "tenant", "order", "sku", "quantity",
                    "unit_price", "discount_percent", "line_total")
    list_filter = ("tenant",)
    search_fields = ("product_name", "sku", "order__number")
    readonly_fields = ("line_total",)


@admin.register(Fulfillment)
class FulfillmentAdmin(admin.ModelAdmin):
    list_display = ("order", "tenant", "carrier", "tracking_number", "status",
                    "shipped_on", "expected_delivery", "delivered_at")
    list_filter = ("tenant", "status", "carrier")
    search_fields = ("tracking_number", "warehouse", "order__number")
    readonly_fields = ("delivered_at",)


@admin.register(OrderAmendment)
class OrderAmendmentAdmin(admin.ModelAdmin):
    list_display = ("order", "tenant", "amendment_type", "status", "amount_delta",
                    "requested_by", "requested_on", "resolved_at")
    list_filter = ("tenant", "status", "amendment_type")
    search_fields = ("reason", "requested_by", "order__number")
    readonly_fields = ("resolved_at",)


@admin.register(RevenueSchedule)
class RevenueScheduleAdmin(admin.ModelAdmin):
    list_display = ("order", "tenant", "method", "status", "period_label",
                    "amount", "recognition_date", "recognized_at")
    list_filter = ("tenant", "status", "method")
    search_fields = ("period_label", "notes", "order__number")
    readonly_fields = ("recognized_at",)
