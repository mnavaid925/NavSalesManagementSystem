from django.db import models, transaction
from django.utils import timezone


class CampaignInfluence(models.Model):
    """Campaign Influence & Attribution — influenced revenue under an attribution model."""

    MODEL_FIRST_TOUCH = "first_touch"
    MODEL_LAST_TOUCH = "last_touch"
    MODEL_LINEAR = "linear"
    MODEL_TIME_DECAY = "time_decay"
    MODEL_W_SHAPED = "w_shaped"
    MODEL_TYPE_CHOICES = [
        (MODEL_FIRST_TOUCH, "First touch"),
        (MODEL_LAST_TOUCH, "Last touch"),
        (MODEL_LINEAR, "Linear"),
        (MODEL_TIME_DECAY, "Time decay"),
        (MODEL_W_SHAPED, "W-shaped"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="marketing_campaigninfluences")
    campaign_name = models.CharField(max_length=150)
    model_type = models.CharField(max_length=20, choices=MODEL_TYPE_CHOICES, default=MODEL_LINEAR)
    influenced_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    opportunities_count = models.IntegerField(default=0)
    attribution_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    period_label = models.CharField(max_length=60)
    recorded_on = models.DateField(default=timezone.localdate)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-recorded_on", "campaign_name"]
        indexes = [
            models.Index(fields=["tenant", "model_type"], name="ci_tenant_modeltype_idx"),
            models.Index(fields=["tenant", "recorded_on"], name="ci_tenant_recdate_idx"),
        ]

    def __str__(self):
        return self.campaign_name


class MQLHandoff(models.Model):
    """MQL-to-SQL Tracking — a marketing-qualified lead handoff (auto MQL-00001)."""

    STATUS_MQL = "mql"
    STATUS_ACCEPTED = "accepted"
    STATUS_REJECTED = "rejected"
    STATUS_SQL = "sql"
    STATUS_RECYCLED = "recycled"
    STATUS_CHOICES = [
        (STATUS_MQL, "MQL"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_SQL, "SQL"),
        (STATUS_RECYCLED, "Recycled"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="marketing_mqlhandoffs")
    number = models.CharField(max_length=20, blank=True)
    lead_name = models.CharField(max_length=150)
    company = models.CharField(max_length=150, blank=True)
    mql_score = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_MQL)
    source = models.CharField(max_length=120, blank=True)
    handed_to = models.CharField(max_length=120, blank=True)
    handoff_date = models.DateField(default=timezone.localdate)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-handoff_date", "-id"]
        unique_together = ("tenant", "number")
        indexes = [
            models.Index(fields=["tenant", "status"], name="mql_tenant_status_idx"),
            models.Index(fields=["tenant", "handoff_date"], name="mql_tenant_handdate_idx"),
        ]

    def __str__(self):
        return self.number or f"MQL #{self.pk}"

    def save(self, *args, **kwargs):
        if not self.number and self.tenant_id:
            # Per-tenant sequence with a row lock to avoid duplicate numbers under
            # concurrent creation (idempotent for seeds).
            with transaction.atomic():
                last = (MQLHandoff.objects.select_for_update()
                        .filter(tenant_id=self.tenant_id, number__startswith="MQL-")
                        .order_by("-number").first())
                seq = 1
                if last and last.number:
                    try:
                        seq = int(last.number.split("-")[1]) + 1
                    except (IndexError, ValueError):
                        seq = (MQLHandoff.objects
                               .filter(tenant_id=self.tenant_id, number__startswith="MQL-")
                               .count() + 1)
                self.number = f"MQL-{seq:05d}"
                super().save(*args, **kwargs)
                return
        super().save(*args, **kwargs)


class CampaignPerformance(models.Model):
    """Campaign Performance Integration — spend, leads and ROI for a campaign."""

    CHANNEL_EMAIL = "email"
    CHANNEL_PAID_SEARCH = "paid_search"
    CHANNEL_SOCIAL = "social"
    CHANNEL_WEBINAR = "webinar"
    CHANNEL_EVENT = "event"
    CHANNEL_CONTENT = "content"
    CHANNEL_DIRECT = "direct"
    CHANNEL_CHOICES = [
        (CHANNEL_EMAIL, "Email"),
        (CHANNEL_PAID_SEARCH, "Paid search"),
        (CHANNEL_SOCIAL, "Social"),
        (CHANNEL_WEBINAR, "Webinar"),
        (CHANNEL_EVENT, "Event"),
        (CHANNEL_CONTENT, "Content"),
        (CHANNEL_DIRECT, "Direct"),
    ]

    STATUS_PLANNED = "planned"
    STATUS_ACTIVE = "active"
    STATUS_PAUSED = "paused"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = [
        (STATUS_PLANNED, "Planned"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_PAUSED, "Paused"),
        (STATUS_COMPLETED, "Completed"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="marketing_campaignperformances")
    campaign_name = models.CharField(max_length=150)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default=CHANNEL_EMAIL)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PLANNED)
    spend = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    leads_generated = models.IntegerField(default=0)
    revenue_influenced = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    roi = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    start_date = models.DateField(default=timezone.localdate)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date", "campaign_name"]
        indexes = [
            models.Index(fields=["tenant", "status"], name="cperf_tenant_status_idx"),
            models.Index(fields=["tenant", "channel"], name="cperf_tenant_channel_idx"),
        ]

    def __str__(self):
        return self.campaign_name


class ContentEngagement(models.Model):
    """Content Performance & Engagement — views, downloads and conversions on an asset."""

    TYPE_BLOG = "blog"
    TYPE_WHITEPAPER = "whitepaper"
    TYPE_VIDEO = "video"
    TYPE_WEBINAR = "webinar"
    TYPE_CASE_STUDY = "case_study"
    TYPE_EBOOK = "ebook"
    TYPE_DATASHEET = "datasheet"
    CONTENT_TYPE_CHOICES = [
        (TYPE_BLOG, "Blog post"),
        (TYPE_WHITEPAPER, "Whitepaper"),
        (TYPE_VIDEO, "Video"),
        (TYPE_WEBINAR, "Webinar"),
        (TYPE_CASE_STUDY, "Case study"),
        (TYPE_EBOOK, "eBook"),
        (TYPE_DATASHEET, "Datasheet"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="marketing_contentengagements")
    content_title = models.CharField(max_length=150)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default=TYPE_BLOG)
    views = models.IntegerField(default=0)
    downloads = models.IntegerField(default=0)
    avg_time_seconds = models.IntegerField(default=0)
    conversions = models.IntegerField(default=0)
    engagement_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    published_on = models.DateField(default=timezone.localdate)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_on", "content_title"]
        indexes = [
            models.Index(fields=["tenant", "content_type"], name="ce_tenant_ctype_idx"),
            models.Index(fields=["tenant", "published_on"], name="ce_tenant_pubdate_idx"),
        ]

    def __str__(self):
        return self.content_title


class MarketingEvent(models.Model):
    """Event & Webinar Management — registrations, attendees and leads (auto EVT-00001)."""

    TYPE_WEBINAR = "webinar"
    TYPE_CONFERENCE = "conference"
    TYPE_TRADE_SHOW = "trade_show"
    TYPE_WORKSHOP = "workshop"
    TYPE_VIRTUAL = "virtual"
    EVENT_TYPE_CHOICES = [
        (TYPE_WEBINAR, "Webinar"),
        (TYPE_CONFERENCE, "Conference"),
        (TYPE_TRADE_SHOW, "Trade show"),
        (TYPE_WORKSHOP, "Workshop"),
        (TYPE_VIRTUAL, "Virtual"),
    ]

    STATUS_PLANNED = "planned"
    STATUS_REGISTRATION_OPEN = "registration_open"
    STATUS_LIVE = "live"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELED = "canceled"
    STATUS_CHOICES = [
        (STATUS_PLANNED, "Planned"),
        (STATUS_REGISTRATION_OPEN, "Registration open"),
        (STATUS_LIVE, "Live"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELED, "Canceled"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, related_name="marketing_marketingevents")
    number = models.CharField(max_length=20, blank=True)
    name = models.CharField(max_length=150)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default=TYPE_WEBINAR)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PLANNED)
    event_date = models.DateField(default=timezone.localdate)
    registrations = models.IntegerField(default=0)
    attendees = models.IntegerField(default=0)
    leads_captured = models.IntegerField(default=0)
    location = models.CharField(max_length=150, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-event_date", "-id"]
        unique_together = ("tenant", "number")
        indexes = [
            models.Index(fields=["tenant", "status"], name="evt_tenant_status_idx"),
            models.Index(fields=["tenant", "event_type"], name="evt_tenant_etype_idx"),
        ]

    def __str__(self):
        return self.number or self.name

    def save(self, *args, **kwargs):
        if not self.number and self.tenant_id:
            # Per-tenant sequence with a row lock to avoid duplicate numbers under
            # concurrent creation (idempotent for seeds).
            with transaction.atomic():
                last = (MarketingEvent.objects.select_for_update()
                        .filter(tenant_id=self.tenant_id, number__startswith="EVT-")
                        .order_by("-number").first())
                seq = 1
                if last and last.number:
                    try:
                        seq = int(last.number.split("-")[1]) + 1
                    except (IndexError, ValueError):
                        seq = (MarketingEvent.objects
                               .filter(tenant_id=self.tenant_id, number__startswith="EVT-")
                               .count() + 1)
                self.number = f"EVT-{seq:05d}"
                super().save(*args, **kwargs)
                return
        super().save(*args, **kwargs)
