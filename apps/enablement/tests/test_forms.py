"""Tests for enablement forms: required fields and field exclusions."""
import pytest
from django.utils import timezone

from apps.enablement.forms import (
    CallRecordingForm, CompetitiveCardForm, ContentAssetForm,
    PlaybookForm, TrainingRecordForm,
)


@pytest.mark.django_db
class TestContentAssetForm:
    def test_valid_form(self):
        form = ContentAssetForm(data={
            "title": "My Deck",
            "asset_type": "deck",
            "status": "draft",
            "description": "",
            "tags": "",
            "file_url": "",
            "owner": "",
        })
        assert form.is_valid(), form.errors

    def test_missing_title_invalid(self):
        form = ContentAssetForm(data={
            "asset_type": "deck",
            "status": "draft",
        })
        assert not form.is_valid()
        assert "title" in form.errors

    def test_tenant_not_in_form_fields(self):
        form = ContentAssetForm()
        assert "tenant" not in form.fields

    def test_published_at_not_in_form_fields(self):
        """published_at is system-set, not a form field."""
        form = ContentAssetForm()
        assert "published_at" not in form.fields

    def test_view_count_not_in_form_fields(self):
        """view_count is managed programmatically, not a form field."""
        form = ContentAssetForm()
        assert "view_count" not in form.fields

    def test_created_at_not_in_form_fields(self):
        form = ContentAssetForm()
        assert "created_at" not in form.fields

    def test_invalid_asset_type_invalid(self):
        form = ContentAssetForm(data={
            "title": "Bad Type",
            "asset_type": "invalid_type",
            "status": "draft",
        })
        assert not form.is_valid()

    def test_invalid_status_invalid(self):
        form = ContentAssetForm(data={
            "title": "Bad Status",
            "asset_type": "deck",
            "status": "nonexistent",
        })
        assert not form.is_valid()

    def test_all_form_fields_present(self):
        form = ContentAssetForm()
        expected = {"title", "asset_type", "status", "description", "tags", "file_url", "owner"}
        assert expected == set(form.fields.keys())


@pytest.mark.django_db
class TestPlaybookForm:
    def test_valid_form(self):
        form = PlaybookForm(data={
            "title": "Discovery Guide",
            "stage": "discovery",
            "status": "active",
            "persona": "VP Sales",
            "summary": "A brief summary.",
            "guidance": "Talk tracks here.",
            "owner": "Jane",
            "version": "1.0",
        })
        assert form.is_valid(), form.errors

    def test_missing_title_invalid(self):
        form = PlaybookForm(data={
            "stage": "discovery",
            "status": "draft",
            "version": "1.0",
        })
        assert not form.is_valid()
        assert "title" in form.errors

    def test_tenant_not_in_form_fields(self):
        form = PlaybookForm()
        assert "tenant" not in form.fields

    def test_created_at_not_in_form_fields(self):
        form = PlaybookForm()
        assert "created_at" not in form.fields

    def test_invalid_stage_invalid(self):
        form = PlaybookForm(data={
            "title": "Bad Stage",
            "stage": "nonexistent_stage",
            "status": "draft",
            "version": "1.0",
        })
        assert not form.is_valid()

    def test_all_form_fields_present(self):
        form = PlaybookForm()
        expected = {"title", "stage", "status", "persona", "summary", "guidance", "owner", "version"}
        assert expected == set(form.fields.keys())


@pytest.mark.django_db
class TestTrainingRecordForm:
    def test_valid_form(self):
        today = timezone.localdate().isoformat()
        form = TrainingRecordForm(data={
            "course_name": "Sales 101",
            "rep_name": "Alice",
            "kind": "course",
            "status": "not_started",
            "provider": "Coursera",
            "score": "",
            "enrolled_on": today,
            "due_on": "",
            "expires_on": "",
            "notes": "",
        })
        assert form.is_valid(), form.errors

    def test_missing_course_name_invalid(self):
        today = timezone.localdate().isoformat()
        form = TrainingRecordForm(data={
            "rep_name": "Alice",
            "kind": "course",
            "status": "not_started",
            "enrolled_on": today,
        })
        assert not form.is_valid()
        assert "course_name" in form.errors

    def test_missing_rep_name_invalid(self):
        today = timezone.localdate().isoformat()
        form = TrainingRecordForm(data={
            "course_name": "Sales 101",
            "kind": "course",
            "status": "not_started",
            "enrolled_on": today,
        })
        assert not form.is_valid()
        assert "rep_name" in form.errors

    def test_tenant_not_in_form_fields(self):
        form = TrainingRecordForm()
        assert "tenant" not in form.fields

    def test_completed_at_not_in_form_fields(self):
        """completed_at is system-set, not a form field."""
        form = TrainingRecordForm()
        assert "completed_at" not in form.fields

    def test_created_at_not_in_form_fields(self):
        form = TrainingRecordForm()
        assert "created_at" not in form.fields

    def test_enrolled_on_uses_date_widget(self):
        form = TrainingRecordForm()
        from django.forms import DateInput
        assert isinstance(form.fields["enrolled_on"].widget, DateInput)

    def test_all_form_fields_present(self):
        form = TrainingRecordForm()
        expected = {
            "course_name", "rep_name", "kind", "status", "provider",
            "score", "enrolled_on", "due_on", "expires_on", "notes"
        }
        assert expected == set(form.fields.keys())


@pytest.mark.django_db
class TestCallRecordingForm:
    def test_valid_form(self):
        today = timezone.localdate().isoformat()
        form = CallRecordingForm(data={
            "title": "Intro Call",
            "rep_name": "Alice",
            "coach_name": "Bob",
            "call_type": "discovery",
            "status": "pending",
            "duration_minutes": 30,
            "recording_url": "",
            "score": "",
            "coaching_notes": "",
            "call_date": today,
        })
        assert form.is_valid(), form.errors

    def test_missing_title_invalid(self):
        today = timezone.localdate().isoformat()
        form = CallRecordingForm(data={
            "rep_name": "Alice",
            "call_type": "discovery",
            "status": "pending",
            "duration_minutes": 30,
            "call_date": today,
        })
        assert not form.is_valid()
        assert "title" in form.errors

    def test_missing_rep_name_invalid(self):
        today = timezone.localdate().isoformat()
        form = CallRecordingForm(data={
            "title": "Call",
            "call_type": "discovery",
            "status": "pending",
            "duration_minutes": 0,
            "call_date": today,
        })
        assert not form.is_valid()
        assert "rep_name" in form.errors

    def test_tenant_not_in_form_fields(self):
        form = CallRecordingForm()
        assert "tenant" not in form.fields

    def test_reviewed_at_not_in_form_fields(self):
        """reviewed_at is system-set, not a form field."""
        form = CallRecordingForm()
        assert "reviewed_at" not in form.fields

    def test_created_at_not_in_form_fields(self):
        form = CallRecordingForm()
        assert "created_at" not in form.fields

    def test_call_date_uses_date_widget(self):
        form = CallRecordingForm()
        from django.forms import DateInput
        assert isinstance(form.fields["call_date"].widget, DateInput)

    def test_all_form_fields_present(self):
        form = CallRecordingForm()
        expected = {
            "title", "rep_name", "coach_name", "call_type", "status",
            "duration_minutes", "recording_url", "score", "coaching_notes", "call_date"
        }
        assert expected == set(form.fields.keys())


@pytest.mark.django_db
class TestCompetitiveCardForm:
    def test_valid_form(self):
        today = timezone.localdate().isoformat()
        form = CompetitiveCardForm(data={
            "competitor_name": "Rival Corp",
            "category": "CRM",
            "threat_level": "high",
            "status": "draft",
            "overview": "A strong competitor.",
            "our_strengths": "Better UX.",
            "their_strengths": "Lower price.",
            "objection_handling": "Emphasize ROI.",
            "owner": "Alice",
            "last_updated_on": today,
        })
        assert form.is_valid(), form.errors

    def test_missing_competitor_name_invalid(self):
        today = timezone.localdate().isoformat()
        form = CompetitiveCardForm(data={
            "threat_level": "medium",
            "status": "draft",
            "last_updated_on": today,
        })
        assert not form.is_valid()
        assert "competitor_name" in form.errors

    def test_tenant_not_in_form_fields(self):
        form = CompetitiveCardForm()
        assert "tenant" not in form.fields

    def test_created_at_not_in_form_fields(self):
        form = CompetitiveCardForm()
        assert "created_at" not in form.fields

    def test_last_updated_on_uses_date_widget(self):
        form = CompetitiveCardForm()
        from django.forms import DateInput
        assert isinstance(form.fields["last_updated_on"].widget, DateInput)

    def test_invalid_threat_level_invalid(self):
        today = timezone.localdate().isoformat()
        form = CompetitiveCardForm(data={
            "competitor_name": "Bad Threat",
            "threat_level": "nuclear",
            "status": "draft",
            "last_updated_on": today,
        })
        assert not form.is_valid()

    def test_all_form_fields_present(self):
        form = CompetitiveCardForm()
        expected = {
            "competitor_name", "category", "threat_level", "status", "overview",
            "our_strengths", "their_strengths", "objection_handling",
            "owner", "last_updated_on"
        }
        assert expected == set(form.fields.keys())
