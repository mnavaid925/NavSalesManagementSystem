from django import forms

from apps.core.forms import StyledFormMixin

from .models import Fulfillment, Order, OrderAmendment, OrderLine, RevenueSchedule

DATE = forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")


class OrderForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Order
        # `number` is auto-generated; `confirmed_at` is system-set (off the form).
        fields = ["customer_name", "customer_email", "channel", "status", "currency",
                  "total_amount", "is_validated", "order_date", "requested_ship_date",
                  "billing_address", "shipping_address", "notes"]
        widgets = {"order_date": DATE, "requested_ship_date": DATE}


class OrderLineForm(StyledFormMixin, forms.ModelForm):
    # `line_total` is system-computed in save() — excluded from the form.
    class Meta:
        model = OrderLine
        fields = ["order", "product_name", "sku", "quantity", "unit_price", "discount_percent"]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Always scope to the tenant; never fall back to .all() (no cross-tenant leak).
        self.fields["order"].queryset = (
            Order.objects.filter(tenant=tenant) if tenant is not None
            else Order.objects.none()
        )


class FulfillmentForm(StyledFormMixin, forms.ModelForm):
    # `delivered_at` is system-set (off the form).
    class Meta:
        model = Fulfillment
        fields = ["order", "warehouse", "carrier", "tracking_number", "status",
                  "shipped_on", "expected_delivery", "notes"]
        widgets = {"shipped_on": DATE, "expected_delivery": DATE}

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["order"].queryset = (
            Order.objects.filter(tenant=tenant) if tenant is not None
            else Order.objects.none()
        )


class OrderAmendmentForm(StyledFormMixin, forms.ModelForm):
    # `resolved_at` is system-set (off the form).
    class Meta:
        model = OrderAmendment
        fields = ["order", "amendment_type", "status", "reason", "requested_by",
                  "amount_delta", "requested_on"]
        widgets = {"requested_on": DATE}

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["order"].queryset = (
            Order.objects.filter(tenant=tenant) if tenant is not None
            else Order.objects.none()
        )


class RevenueScheduleForm(StyledFormMixin, forms.ModelForm):
    # `recognized_at` is system-set (off the form).
    class Meta:
        model = RevenueSchedule
        fields = ["order", "method", "status", "period_label", "amount",
                  "recognition_date", "notes"]
        widgets = {"recognition_date": DATE}

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["order"].queryset = (
            Order.objects.filter(tenant=tenant) if tenant is not None
            else Order.objects.none()
        )
