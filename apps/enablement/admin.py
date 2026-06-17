from django.contrib import admin

from .models import (
    CallRecording, CompetitiveCard, ContentAsset, Playbook, TrainingRecord,
)


@admin.register(ContentAsset)
class ContentAssetAdmin(admin.ModelAdmin):
    list_display = ("title", "tenant", "asset_type", "status", "owner", "view_count", "updated_at")
    list_filter = ("tenant", "asset_type", "status")
    search_fields = ("title", "description", "tags", "owner")
    readonly_fields = ("published_at", "view_count")


@admin.register(Playbook)
class PlaybookAdmin(admin.ModelAdmin):
    list_display = ("title", "tenant", "stage", "status", "persona", "version", "updated_at")
    list_filter = ("tenant", "stage", "status")
    search_fields = ("title", "persona", "summary", "owner")


@admin.register(TrainingRecord)
class TrainingRecordAdmin(admin.ModelAdmin):
    list_display = ("course_name", "tenant", "rep_name", "kind", "status", "score", "enrolled_on", "due_on")
    list_filter = ("tenant", "kind", "status")
    search_fields = ("course_name", "rep_name", "provider")
    readonly_fields = ("completed_at",)


@admin.register(CallRecording)
class CallRecordingAdmin(admin.ModelAdmin):
    list_display = ("title", "tenant", "rep_name", "coach_name", "call_type", "status", "call_date")
    list_filter = ("tenant", "call_type", "status")
    search_fields = ("title", "rep_name", "coach_name", "coaching_notes")
    readonly_fields = ("reviewed_at",)


@admin.register(CompetitiveCard)
class CompetitiveCardAdmin(admin.ModelAdmin):
    list_display = ("competitor_name", "tenant", "category", "threat_level", "status", "owner", "last_updated_on")
    list_filter = ("tenant", "threat_level", "status")
    search_fields = ("competitor_name", "category", "overview", "owner")
