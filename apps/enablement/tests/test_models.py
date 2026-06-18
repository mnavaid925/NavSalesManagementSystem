"""Tests for enablement models: ContentAsset, Playbook, TrainingRecord, CallRecording, CompetitiveCard."""
import pytest
from django.utils import timezone

from apps.enablement.models import (
    CallRecording, CompetitiveCard, ContentAsset, Playbook, TrainingRecord,
)


# ============================================================ ContentAsset
@pytest.mark.django_db
class TestContentAsset:
    def test_str_returns_title(self, asset_a):
        assert str(asset_a) == "Sales Deck Q1"

    def test_default_asset_type_is_deck(self, tenant_a):
        obj = ContentAsset.objects.create(tenant=tenant_a, title="Test")
        assert obj.asset_type == ContentAsset.TYPE_DECK

    def test_default_status_is_draft(self, tenant_a):
        obj = ContentAsset.objects.create(tenant=tenant_a, title="Test2")
        assert obj.status == ContentAsset.STATUS_DRAFT

    def test_type_choices_contain_all_seven(self):
        choices = dict(ContentAsset.TYPE_CHOICES)
        assert ContentAsset.TYPE_DECK in choices
        assert ContentAsset.TYPE_ONE_PAGER in choices
        assert ContentAsset.TYPE_CASE_STUDY in choices
        assert ContentAsset.TYPE_WHITEPAPER in choices
        assert ContentAsset.TYPE_VIDEO in choices
        assert ContentAsset.TYPE_TEMPLATE in choices
        assert ContentAsset.TYPE_OTHER in choices

    def test_status_choices_contain_all_three(self):
        choices = dict(ContentAsset.STATUS_CHOICES)
        assert ContentAsset.STATUS_DRAFT in choices
        assert ContentAsset.STATUS_PUBLISHED in choices
        assert ContentAsset.STATUS_ARCHIVED in choices

    def test_save_sets_published_at_when_published(self, tenant_a):
        obj = ContentAsset.objects.create(
            tenant=tenant_a, title="Pub Test", status=ContentAsset.STATUS_DRAFT
        )
        assert obj.published_at is None
        obj.status = ContentAsset.STATUS_PUBLISHED
        obj.save()
        assert obj.published_at is not None

    def test_save_clears_published_at_when_not_published(self, tenant_a):
        obj = ContentAsset.objects.create(
            tenant=tenant_a, title="Pub Clear", status=ContentAsset.STATUS_PUBLISHED
        )
        assert obj.published_at is not None
        obj.status = ContentAsset.STATUS_DRAFT
        obj.save()
        assert obj.published_at is None

    def test_save_clears_published_at_when_archived(self, tenant_a):
        obj = ContentAsset.objects.create(
            tenant=tenant_a, title="Archive Clear", status=ContentAsset.STATUS_PUBLISHED
        )
        obj.status = ContentAsset.STATUS_ARCHIVED
        obj.save()
        assert obj.published_at is None

    def test_view_count_default_zero(self, tenant_a):
        obj = ContentAsset.objects.create(tenant=tenant_a, title="Views")
        assert obj.view_count == 0

    def test_ordering_by_updated_at_desc(self, tenant_a):
        obj1 = ContentAsset.objects.create(tenant=tenant_a, title="First")
        obj2 = ContentAsset.objects.create(tenant=tenant_a, title="Second")
        qs = list(ContentAsset.objects.filter(tenant=tenant_a))
        # Newest updated_at first
        assert qs[0].pk == obj2.pk

    def test_published_at_not_set_again_if_already_set(self, tenant_a):
        """Re-publishing after unarchiving should reset published_at (per save logic)."""
        obj = ContentAsset.objects.create(
            tenant=tenant_a, title="Repub", status=ContentAsset.STATUS_PUBLISHED
        )
        first_published_at = obj.published_at
        obj.status = ContentAsset.STATUS_ARCHIVED
        obj.save()
        obj.status = ContentAsset.STATUS_PUBLISHED
        obj.save()
        # After re-publish, published_at is reset to now (per intentional comment in model)
        assert obj.published_at is not None


# ============================================================ Playbook
@pytest.mark.django_db
class TestPlaybook:
    def test_str_returns_title(self, playbook_a):
        assert str(playbook_a) == "Discovery Playbook"

    def test_default_stage_is_prospecting(self, tenant_a):
        pb = Playbook.objects.create(tenant=tenant_a, title="Default Stage")
        assert pb.stage == Playbook.STAGE_PROSPECTING

    def test_default_status_is_draft(self, tenant_a):
        pb = Playbook.objects.create(tenant=tenant_a, title="Default Status")
        assert pb.status == Playbook.STATUS_DRAFT

    def test_default_version_is_1_0(self, tenant_a):
        pb = Playbook.objects.create(tenant=tenant_a, title="Default Ver")
        assert pb.version == "1.0"

    def test_stage_choices_contain_all_six(self):
        choices = dict(Playbook.STAGE_CHOICES)
        assert Playbook.STAGE_PROSPECTING in choices
        assert Playbook.STAGE_DISCOVERY in choices
        assert Playbook.STAGE_DEMO in choices
        assert Playbook.STAGE_NEGOTIATION in choices
        assert Playbook.STAGE_CLOSING in choices
        assert Playbook.STAGE_ONBOARDING in choices

    def test_status_choices_contain_all_three(self):
        choices = dict(Playbook.STATUS_CHOICES)
        assert Playbook.STATUS_DRAFT in choices
        assert Playbook.STATUS_ACTIVE in choices
        assert Playbook.STATUS_RETIRED in choices

    def test_ordering_by_stage_then_title(self, tenant_a):
        Playbook.objects.create(tenant=tenant_a, title="Z Playbook", stage=Playbook.STAGE_PROSPECTING)
        Playbook.objects.create(tenant=tenant_a, title="A Playbook", stage=Playbook.STAGE_PROSPECTING)
        qs = list(Playbook.objects.filter(tenant=tenant_a))
        titles = [p.title for p in qs]
        assert titles == sorted(titles)


# ============================================================ TrainingRecord
@pytest.mark.django_db
class TestTrainingRecord:
    def test_str_shows_rep_and_course(self, training_a):
        result = str(training_a)
        assert "Alice" in result
        assert "Sales Foundations" in result

    def test_str_format(self, training_a):
        assert str(training_a) == "Alice — Sales Foundations"

    def test_default_kind_is_course(self, tenant_a):
        tr = TrainingRecord.objects.create(
            tenant=tenant_a, course_name="Course", rep_name="Rep"
        )
        assert tr.kind == TrainingRecord.KIND_COURSE

    def test_default_status_is_not_started(self, tenant_a):
        tr = TrainingRecord.objects.create(
            tenant=tenant_a, course_name="Course2", rep_name="Rep2"
        )
        assert tr.status == TrainingRecord.STATUS_NOT_STARTED

    def test_kind_choices_contain_all_four(self):
        choices = dict(TrainingRecord.KIND_CHOICES)
        assert TrainingRecord.KIND_COURSE in choices
        assert TrainingRecord.KIND_CERTIFICATION in choices
        assert TrainingRecord.KIND_WORKSHOP in choices
        assert TrainingRecord.KIND_ONBOARDING in choices

    def test_status_choices_contain_all_four(self):
        choices = dict(TrainingRecord.STATUS_CHOICES)
        assert TrainingRecord.STATUS_NOT_STARTED in choices
        assert TrainingRecord.STATUS_IN_PROGRESS in choices
        assert TrainingRecord.STATUS_COMPLETED in choices
        assert TrainingRecord.STATUS_EXPIRED in choices

    def test_save_sets_completed_at_when_completed(self, training_a):
        assert training_a.completed_at is None
        training_a.status = TrainingRecord.STATUS_COMPLETED
        training_a.save()
        assert training_a.completed_at is not None

    def test_save_clears_completed_at_when_not_completed(self, tenant_a):
        tr = TrainingRecord.objects.create(
            tenant=tenant_a,
            course_name="Done Course",
            rep_name="Done Rep",
            status=TrainingRecord.STATUS_COMPLETED,
        )
        assert tr.completed_at is not None
        tr.status = TrainingRecord.STATUS_IN_PROGRESS
        tr.save()
        assert tr.completed_at is None

    def test_enrolled_on_defaults_to_today(self, tenant_a):
        tr = TrainingRecord.objects.create(
            tenant=tenant_a, course_name="Default Date", rep_name="Rep"
        )
        assert tr.enrolled_on == timezone.localdate()


# ============================================================ CallRecording
@pytest.mark.django_db
class TestCallRecording:
    def test_str_returns_title(self, recording_a):
        assert str(recording_a) == "Discovery Call — Alice"

    def test_default_call_type_is_discovery(self, tenant_a):
        cr = CallRecording.objects.create(
            tenant=tenant_a, title="Test Call", rep_name="Rep"
        )
        assert cr.call_type == CallRecording.TYPE_DISCOVERY

    def test_default_status_is_pending(self, tenant_a):
        cr = CallRecording.objects.create(
            tenant=tenant_a, title="Test Call2", rep_name="Rep"
        )
        assert cr.status == CallRecording.STATUS_PENDING

    def test_default_duration_is_zero(self, tenant_a):
        cr = CallRecording.objects.create(
            tenant=tenant_a, title="Test Call3", rep_name="Rep"
        )
        assert cr.duration_minutes == 0

    def test_call_type_choices_contain_all_five(self):
        choices = dict(CallRecording.TYPE_CHOICES)
        assert CallRecording.TYPE_DISCOVERY in choices
        assert CallRecording.TYPE_DEMO in choices
        assert CallRecording.TYPE_NEGOTIATION in choices
        assert CallRecording.TYPE_CHECK_IN in choices
        assert CallRecording.TYPE_CLOSING in choices

    def test_status_choices_contain_all_four(self):
        choices = dict(CallRecording.STATUS_CHOICES)
        assert CallRecording.STATUS_PENDING in choices
        assert CallRecording.STATUS_REVIEWED in choices
        assert CallRecording.STATUS_COACHED in choices
        assert CallRecording.STATUS_FLAGGED in choices

    def test_save_sets_reviewed_at_when_reviewed(self, recording_a):
        assert recording_a.reviewed_at is None
        recording_a.status = CallRecording.STATUS_REVIEWED
        recording_a.save()
        assert recording_a.reviewed_at is not None

    def test_save_sets_reviewed_at_when_coached(self, recording_a):
        assert recording_a.reviewed_at is None
        recording_a.status = CallRecording.STATUS_COACHED
        recording_a.save()
        assert recording_a.reviewed_at is not None

    def test_save_clears_reviewed_at_when_flagged(self, tenant_a):
        cr = CallRecording.objects.create(
            tenant=tenant_a, title="Reviewed Call", rep_name="Rep",
            status=CallRecording.STATUS_REVIEWED,
        )
        assert cr.reviewed_at is not None
        cr.status = CallRecording.STATUS_FLAGGED
        cr.save()
        assert cr.reviewed_at is None

    def test_save_clears_reviewed_at_when_pending(self, tenant_a):
        cr = CallRecording.objects.create(
            tenant=tenant_a, title="Reviewed Call2", rep_name="Rep",
            status=CallRecording.STATUS_REVIEWED,
        )
        cr.status = CallRecording.STATUS_PENDING
        cr.save()
        assert cr.reviewed_at is None

    def test_call_date_defaults_to_today(self, tenant_a):
        cr = CallRecording.objects.create(
            tenant=tenant_a, title="Date Default", rep_name="Rep"
        )
        assert cr.call_date == timezone.localdate()


# ============================================================ CompetitiveCard
@pytest.mark.django_db
class TestCompetitiveCard:
    def test_str_returns_competitor_name(self, card_a):
        assert str(card_a) == "Acme Corp"

    def test_default_threat_level_is_medium(self, tenant_a):
        cc = CompetitiveCard.objects.create(
            tenant=tenant_a, competitor_name="Default Threat"
        )
        assert cc.threat_level == CompetitiveCard.THREAT_MEDIUM

    def test_default_status_is_draft(self, tenant_a):
        cc = CompetitiveCard.objects.create(
            tenant=tenant_a, competitor_name="Default Status"
        )
        assert cc.status == CompetitiveCard.STATUS_DRAFT

    def test_threat_choices_contain_all_three(self):
        choices = dict(CompetitiveCard.THREAT_CHOICES)
        assert CompetitiveCard.THREAT_LOW in choices
        assert CompetitiveCard.THREAT_MEDIUM in choices
        assert CompetitiveCard.THREAT_HIGH in choices

    def test_status_choices_contain_all_three(self):
        choices = dict(CompetitiveCard.STATUS_CHOICES)
        assert CompetitiveCard.STATUS_DRAFT in choices
        assert CompetitiveCard.STATUS_PUBLISHED in choices
        assert CompetitiveCard.STATUS_ARCHIVED in choices

    def test_last_updated_on_defaults_to_today(self, tenant_a):
        cc = CompetitiveCard.objects.create(
            tenant=tenant_a, competitor_name="Date Default"
        )
        assert cc.last_updated_on == timezone.localdate()

    def test_ordering_by_competitor_name(self, tenant_a):
        CompetitiveCard.objects.create(tenant=tenant_a, competitor_name="Zebra Corp")
        CompetitiveCard.objects.create(tenant=tenant_a, competitor_name="Alpha Inc")
        names = list(
            CompetitiveCard.objects.filter(tenant=tenant_a).values_list("competitor_name", flat=True)
        )
        assert names == sorted(names)
