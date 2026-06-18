from django.db import models, transaction
from django.utils import timezone


class Order(models.Model):
    """Order Capture & Validation — a sales order (auto-numbered ORD-00001)."""

    STATUS_DRAFT = "draft"
    STATUS_VALIDATED = "validated"
    STATUS_CONFIRMED = "confirmed"
    STATUS_FULFILLED = "fulfilled"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_VALIDATED, "Validated"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_FULFILLED, "Fulfilled"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    CHANNEL_DIRECT = "direct"
    CHANNEL_PARTNER = "partner"
    CHANNEL_ONLINE = "online"
    CHANNEL_RENEWAL = "renewal"
    CHANNEL_CHOICES = [
        (CHANNEL_DIRECT, "Direct Sales"),
        (CHANNEL_PARTNER, "Partner / Channel"),
        (CHANNEL_ONLINE, "Online / Self-serve"),
        (CHANNEL_RENEWAL, "Renewal"),
    ]

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, related_name="orders_orders")
    number = models.CharField(max_length=20, blank=True)
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField(blank=True)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default=CHANNEL_DIRECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    currency = models.CharField(max_length=3, default="USD")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_validated = models.BooleanField(default=False)
    order_date = models.DateField(default=timezone.localdate)
    requested_ship_date = models.DateField(null=True, blank=True)
    billing_address = models.TextField(blank=True)
    shipping_address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-order_date", "-id"]
        unique_together = ("tenant", "number")
        indexes = [
            models.Index(fields=["tenant", "status"], name="order_tenant_status_idx"),
            models.Index(fields=["tenant", "order_date"], name="order_tenant_date_idx"),
        ]

    def __str__(self):
        return self.number or f"Order #{self.pk}"

    def save(self, *args, **kwargs):
        if not self.number and self.tenant_id:
            # Per-tenant sequence with a row lock to avoid duplicate numbers under
            # concurrent creation (idempotent for seeds).
            with transaction.atomic():
                last = (Order.objects.select_for_update()
                        .filter(tenant_id=self.tenant_id, number__startswith="ORD-")
                        .order_by("-number").first())
                seq = 1
                if last and last.number:
                    try:
                        seq = int(last.number.split("-")[1]) + 1
                    except (IndexError, ValueError):
                        seq = Order.objects.filter(tenant_id=self.tenant_id).count() + 1
                self.number = f"ORD-{seq:05d}"
                if self.status == self.STATUS_CONFIRMED and self.confirmed_at is None:
                    self.confirmed_at = timezone.now()
                super().save(*args, **kwargs)
                return
        if self.status == self.STATUS_CONFIRMED and self.confirmed_at is None:
            self.confirmed_at = timezone.now()
        super().save(*args, **kwargs)


class OrderLine(models.Model):
    """Order Capture & Validation — a single line item on an order."""

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, related_name="orders_orderlines")
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="lines")
    product_name = models.CharField(max_length=200)
    sku = models.CharField(max_length=60, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]
        indexes = [
            models.Index(fields=["tenant", "order"], name="orderline_tenant_order_idx"),
        ]

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    def save(self, *args, **kwargs):
        # Derive line_total from qty, price and discount (system-computed, off forms).
        gross = self.unit_price * self.quantity
        discount = gross * (self.discount_percent / 100)
        self.line_total = gross - discount
        super().save(*args, **kwargs)


class Fulfillment(models.Model):
    """Order Fulfillment Tracking — a shipment / delivery against an order."""

    STATUS_PENDING = "pending"
    STATUS_PICKING = "picking"
    STATUS_PACKED = "packed"
    STATUS_SHIPPED = "shipped"
    STATUS_DELIVERED = "delivered"
    STATUS_RETURNED = "returned"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PICKING, "Picking"),
        (STATUS_PACKED, "Packed"),
        (STATUS_SHIPPED, "Shipped"),
        (STATUS_DELIVERED, "Delivered"),
        (STATUS_RETURNED, "Returned"),
    ]

    CARRIER_FEDEX = "fedex"
    CARRIER_UPS = "ups"
    CARRIER_DHL = "dhl"
    CARRIER_USPS = "usps"
    CARRIER_DIGITAL = "digital"
    CARRIER_CHOICES = [
        (CARRIER_FEDEX, "FedEx"),
        (CARRIER_UPS, "UPS"),
        (CARRIER_DHL, "DHL"),
        (CARRIER_USPS, "USPS"),
        (CARRIER_DIGITAL, "Digital Delivery"),
    ]

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, related_name="orders_fulfillments")
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="fulfillments")
    warehouse = models.CharField(max_length=120, blank=True)
    carrier = models.CharField(max_length=20, choices=CARRIER_CHOICES, default=CARRIER_FEDEX)
    tracking_number = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    shipped_on = models.DateField(null=True, blank=True)
    expected_delivery = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="fulfil_tenant_status_idx"),
            models.Index(fields=["tenant", "order"], name="fulfil_tenant_order_idx"),
        ]

    def __str__(self):
        return f"{self.get_carrier_display()} — {self.tracking_number or self.get_status_display()}"

    def save(self, *args, **kwargs):
        if self.status == self.STATUS_DELIVERED and self.delivered_at is None:
            self.delivered_at = timezone.now()
        super().save(*args, **kwargs)


class OrderAmendment(models.Model):
    """Order Amendments & Cancellations — a change or cancellation request."""

    TYPE_QUANTITY = "quantity"
    TYPE_PRICE = "price"
    TYPE_ADDRESS = "address"
    TYPE_DATE = "date"
    TYPE_CANCELLATION = "cancellation"
    TYPE_CHOICES = [
        (TYPE_QUANTITY, "Quantity Change"),
        (TYPE_PRICE, "Price Adjustment"),
        (TYPE_ADDRESS, "Address Change"),
        (TYPE_DATE, "Date Change"),
        (TYPE_CANCELLATION, "Cancellation"),
    ]

    STATUS_REQUESTED = "requested"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_APPLIED = "applied"
    STATUS_CHOICES = [
        (STATUS_REQUESTED, "Requested"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_APPLIED, "Applied"),
    ]

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, related_name="orders_amendments")
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="amendments")
    amendment_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_QUANTITY)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_REQUESTED)
    reason = models.TextField(blank=True)
    requested_by = models.CharField(max_length=150, blank=True)
    amount_delta = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    requested_on = models.DateField(default=timezone.localdate)
    resolved_at = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-requested_on", "-id"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="amend_tenant_status_idx"),
            models.Index(fields=["tenant", "order"], name="amend_tenant_order_idx"),
        ]

    def __str__(self):
        return f"{self.get_amendment_type_display()} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if self.status in (self.STATUS_APPROVED, self.STATUS_REJECTED, self.STATUS_APPLIED) \
                and self.resolved_at is None:
            self.resolved_at = timezone.now()
        if self.status == self.STATUS_REQUESTED:
            self.resolved_at = None
        super().save(*args, **kwargs)


class RevenueSchedule(models.Model):
    """Revenue Recognition & Scheduling — a recognized revenue installment."""

    METHOD_IMMEDIATE = "immediate"
    METHOD_RATABLE = "ratable"
    METHOD_MILESTONE = "milestone"
    METHOD_USAGE = "usage"
    METHOD_CHOICES = [
        (METHOD_IMMEDIATE, "Immediate"),
        (METHOD_RATABLE, "Ratable (Straight-line)"),
        (METHOD_MILESTONE, "Milestone-based"),
        (METHOD_USAGE, "Usage-based"),
    ]

    STATUS_SCHEDULED = "scheduled"
    STATUS_RECOGNIZED = "recognized"
    STATUS_DEFERRED = "deferred"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_SCHEDULED, "Scheduled"),
        (STATUS_RECOGNIZED, "Recognized"),
        (STATUS_DEFERRED, "Deferred"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, related_name="orders_revenueschedules")
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="revenue_schedules")
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default=METHOD_RATABLE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SCHEDULED)
    period_label = models.CharField(max_length=60, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    recognition_date = models.DateField(default=timezone.localdate)
    notes = models.TextField(blank=True)
    recognized_at = models.DateTimeField(null=True, blank=True)  # system-set (off forms)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["recognition_date", "id"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="revsched_tenant_status_idx"),
        ]

    def __str__(self):
        return f"{self.period_label or self.recognition_date} — {self.amount}"

    def save(self, *args, **kwargs):
        if self.status == self.STATUS_RECOGNIZED and self.recognized_at is None:
            self.recognized_at = timezone.now()
        if self.status != self.STATUS_RECOGNIZED:
            self.recognized_at = None
        super().save(*args, **kwargs)
