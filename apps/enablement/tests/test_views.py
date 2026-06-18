"""Tests for enablement views: CRUD for all five models."""
import pytest
from django.urls import reverse
from django.test import Client
from django.utils import timezone

from apps.enablement.models import (
    CallRecording, CompetitiveCard, ContentAsset, Playbook, TrainingRecord,
)


# ============================================================ anonymous redirects
@pytest.mark.django_db
class TestAnonymousRedirects:
    def _get(self, url):
        return Client().get(url)

    def test_contentasset_list_redirects_anonymous(self):
        resp = self._get(reverse("enablement:contentasset_list"))
        assert resp.status_code in (301, 302)

    def test_playbook_list_redirects_anonymous(self):
        resp = self._get(reverse("enablement:playbook_list"))
        assert resp.status_code in (301, 302)

    def test_trainingrecord_list_redirects_anonymous(self):
        resp = self._get(reverse("enablement:trainingrecord_list"))
        assert resp.status_code in (301, 302)

    def test_callrecording_list_redirects_anonymous(self):
        resp = self._get(reverse("enablement:callrecording_list"))
        assert resp.status_code in (301, 302)

    def test_competitivecard_list_redirects_anonymous(self):
        resp = self._get(reverse("enablement:competitivecard_list"))
        assert resp.status_code in (301, 302)


# ============================================================ ContentAsset CRUD
@pytest.mark.django_db
class TestContentAssetCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("enablement:contentasset_list"))
        assert resp.status_code == 200

    def test_list_context_has_assets(self, client_a, asset_a):
        resp = client_a.get(reverse("enablement:contentasset_list"))
        assert "assets" in resp.context

    def test_list_seeded_asset_appears(self, client_a, asset_a):
        resp = client_a.get(reverse("enablement:contentasset_list"))
        pks = [obj.pk for obj in resp.context["assets"]]
        assert asset_a.pk in pks

    def test_list_has_type_choices_in_context(self, client_a):
        resp = client_a.get(reverse("enablement:contentasset_list"))
        assert "type_choices" in resp.context

    def test_list_has_status_choices_in_context(self, client_a):
        resp = client_a.get(reverse("enablement:contentasset_list"))
        assert "status_choices" in resp.context

    def test_list_filter_by_status(self, client_a, asset_a):
        resp = client_a.get(reverse("enablement:contentasset_list") + "?status=draft")
        assert resp.status_code == 200
        pks = [obj.pk for obj in resp.context["assets"]]
        assert asset_a.pk in pks

    def test_list_search_by_title(self, client_a, asset_a):
        resp = client_a.get(reverse("enablement:contentasset_list") + "?q=Sales+Deck")
        assert resp.status_code == 200
        pks = [obj.pk for obj in resp.context["assets"]]
        assert asset_a.pk in pks

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("enablement:contentasset_create"))
        assert resp.status_code == 200

    def test_create_post_creates_asset(self, client_a, tenant_a):
        before = ContentAsset.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("enablement:contentasset_create"), {
            "title": "New Asset",
            "asset_type": "deck",
            "status": "draft",
            "description": "",
            "tags": "",
            "file_url": "",
            "owner": "",
        })
        assert ContentAsset.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a):
        client_a.post(reverse("enablement:contentasset_create"), {
            "title": "Tenant Check Asset",
            "asset_type": "one_pager",
            "status": "draft",
            "description": "",
            "tags": "",
            "file_url": "",
            "owner": "",
        })
        obj = ContentAsset.objects.filter(title="Tenant Check Asset").first()
        assert obj is not None
        assert obj.tenant == tenant_a

    def test_detail_200(self, client_a, asset_a):
        resp = client_a.get(reverse("enablement:contentasset_detail", args=[asset_a.pk]))
        assert resp.status_code == 200

    def test_detail_context_has_obj(self, client_a, asset_a):
        resp = client_a.get(reverse("enablement:contentasset_detail", args=[asset_a.pk]))
        assert "obj" in resp.context
        assert resp.context["obj"].pk == asset_a.pk

    def test_edit_get_200(self, client_a, asset_a):
        resp = client_a.get(reverse("enablement:contentasset_edit", args=[asset_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates(self, client_a, asset_a):
        client_a.post(reverse("enablement:contentasset_edit", args=[asset_a.pk]), {
            "title": "Updated Asset Title",
            "asset_type": "whitepaper",
            "status": "published",
            "description": "",
            "tags": "",
            "file_url": "",
            "owner": "",
        })
        asset_a.refresh_from_db()
        assert asset_a.title == "Updated Asset Title"

    def test_delete_post_removes_asset(self, client_a, tenant_a):
        obj = ContentAsset.objects.create(
            tenant=tenant_a, title="To Delete Asset", asset_type="deck", status="draft"
        )
        client_a.post(reverse("enablement:contentasset_delete", args=[obj.pk]))
        assert not ContentAsset.objects.filter(pk=obj.pk).exists()

    def test_delete_post_redirects_to_list(self, client_a, tenant_a):
        obj = ContentAsset.objects.create(
            tenant=tenant_a, title="Delete Redirect Asset", asset_type="deck", status="draft"
        )
        resp = client_a.post(reverse("enablement:contentasset_delete", args=[obj.pk]))
        assert resp.status_code in (301, 302)


# ============================================================ Playbook CRUD
@pytest.mark.django_db
class TestPlaybookCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("enablement:playbook_list"))
        assert resp.status_code == 200

    def test_list_context_has_playbooks(self, client_a, playbook_a):
        resp = client_a.get(reverse("enablement:playbook_list"))
        assert "playbooks" in resp.context

    def test_list_seeded_playbook_appears(self, client_a, playbook_a):
        resp = client_a.get(reverse("enablement:playbook_list"))
        pks = [obj.pk for obj in resp.context["playbooks"]]
        assert playbook_a.pk in pks

    def test_list_has_stage_choices_in_context(self, client_a):
        resp = client_a.get(reverse("enablement:playbook_list"))
        assert "stage_choices" in resp.context

    def test_list_has_status_choices_in_context(self, client_a):
        resp = client_a.get(reverse("enablement:playbook_list"))
        assert "status_choices" in resp.context

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("enablement:playbook_create"))
        assert resp.status_code == 200

    def test_create_post_creates_playbook(self, client_a, tenant_a):
        before = Playbook.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("enablement:playbook_create"), {
            "title": "New Playbook",
            "stage": "discovery",
            "status": "draft",
            "persona": "",
            "summary": "",
            "guidance": "",
            "owner": "",
            "version": "1.0",
        })
        assert Playbook.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a):
        client_a.post(reverse("enablement:playbook_create"), {
            "title": "Tenant Check Playbook",
            "stage": "prospecting",
            "status": "draft",
            "persona": "",
            "summary": "",
            "guidance": "",
            "owner": "",
            "version": "1.0",
        })
        obj = Playbook.objects.filter(title="Tenant Check Playbook").first()
        assert obj is not None
        assert obj.tenant == tenant_a

    def test_detail_200(self, client_a, playbook_a):
        resp = client_a.get(reverse("enablement:playbook_detail", args=[playbook_a.pk]))
        assert resp.status_code == 200

    def test_edit_get_200(self, client_a, playbook_a):
        resp = client_a.get(reverse("enablement:playbook_edit", args=[playbook_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates(self, client_a, playbook_a):
        client_a.post(reverse("enablement:playbook_edit", args=[playbook_a.pk]), {
            "title": "Updated Playbook",
            "stage": "demo",
            "status": "active",
            "persona": "",
            "summary": "",
            "guidance": "",
            "owner": "",
            "version": "2.0",
        })
        playbook_a.refresh_from_db()
        assert playbook_a.title == "Updated Playbook"
        assert playbook_a.version == "2.0"

    def test_delete_post_removes_playbook(self, client_a, tenant_a):
        obj = Playbook.objects.create(
            tenant=tenant_a, title="To Delete Playbook", stage="prospecting", status="draft"
        )
        client_a.post(reverse("enablement:playbook_delete", args=[obj.pk]))
        assert not Playbook.objects.filter(pk=obj.pk).exists()


# ============================================================ TrainingRecord CRUD
@pytest.mark.django_db
class TestTrainingRecordCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("enablement:trainingrecord_list"))
        assert resp.status_code == 200

    def test_list_context_has_records(self, client_a, training_a):
        resp = client_a.get(reverse("enablement:trainingrecord_list"))
        assert "records" in resp.context

    def test_list_seeded_record_appears(self, client_a, training_a):
        resp = client_a.get(reverse("enablement:trainingrecord_list"))
        pks = [obj.pk for obj in resp.context["records"]]
        assert training_a.pk in pks

    def test_list_has_kind_choices_in_context(self, client_a):
        resp = client_a.get(reverse("enablement:trainingrecord_list"))
        assert "kind_choices" in resp.context

    def test_list_has_status_choices_in_context(self, client_a):
        resp = client_a.get(reverse("enablement:trainingrecord_list"))
        assert "status_choices" in resp.context

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("enablement:trainingrecord_create"))
        assert resp.status_code == 200

    def test_create_post_creates_record(self, client_a, tenant_a):
        today = timezone.localdate().isoformat()
        before = TrainingRecord.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("enablement:trainingrecord_create"), {
            "course_name": "New Course",
            "rep_name": "Charlie",
            "kind": "certification",
            "status": "not_started",
            "provider": "",
            "score": "",
            "enrolled_on": today,
            "due_on": "",
            "expires_on": "",
            "notes": "",
        })
        assert TrainingRecord.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a):
        today = timezone.localdate().isoformat()
        client_a.post(reverse("enablement:trainingrecord_create"), {
            "course_name": "Tenant Check Course",
            "rep_name": "Dave",
            "kind": "course",
            "status": "not_started",
            "provider": "",
            "score": "",
            "enrolled_on": today,
            "due_on": "",
            "expires_on": "",
            "notes": "",
        })
        obj = TrainingRecord.objects.filter(course_name="Tenant Check Course").first()
        assert obj is not None
        assert obj.tenant == tenant_a

    def test_detail_200(self, client_a, training_a):
        resp = client_a.get(reverse("enablement:trainingrecord_detail", args=[training_a.pk]))
        assert resp.status_code == 200

    def test_edit_get_200(self, client_a, training_a):
        resp = client_a.get(reverse("enablement:trainingrecord_edit", args=[training_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates(self, client_a, training_a):
        today = timezone.localdate().isoformat()
        client_a.post(reverse("enablement:trainingrecord_edit", args=[training_a.pk]), {
            "course_name": "Updated Course",
            "rep_name": "Alice Updated",
            "kind": "workshop",
            "status": "in_progress",
            "provider": "Udemy",
            "score": "",
            "enrolled_on": today,
            "due_on": "",
            "expires_on": "",
            "notes": "",
        })
        training_a.refresh_from_db()
        assert training_a.course_name == "Updated Course"

    def test_delete_post_removes_record(self, client_a, tenant_a):
        obj = TrainingRecord.objects.create(
            tenant=tenant_a,
            course_name="To Delete Course",
            rep_name="Rep",
            enrolled_on=timezone.localdate(),
        )
        client_a.post(reverse("enablement:trainingrecord_delete", args=[obj.pk]))
        assert not TrainingRecord.objects.filter(pk=obj.pk).exists()


# ============================================================ CallRecording CRUD
@pytest.mark.django_db
class TestCallRecordingCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("enablement:callrecording_list"))
        assert resp.status_code == 200

    def test_list_context_has_recordings(self, client_a, recording_a):
        resp = client_a.get(reverse("enablement:callrecording_list"))
        assert "recordings" in resp.context

    def test_list_seeded_recording_appears(self, client_a, recording_a):
        resp = client_a.get(reverse("enablement:callrecording_list"))
        pks = [obj.pk for obj in resp.context["recordings"]]
        assert recording_a.pk in pks

    def test_list_has_type_choices_in_context(self, client_a):
        resp = client_a.get(reverse("enablement:callrecording_list"))
        assert "type_choices" in resp.context

    def test_list_has_status_choices_in_context(self, client_a):
        resp = client_a.get(reverse("enablement:callrecording_list"))
        assert "status_choices" in resp.context

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("enablement:callrecording_create"))
        assert resp.status_code == 200

    def test_create_post_creates_recording(self, client_a, tenant_a):
        today = timezone.localdate().isoformat()
        before = CallRecording.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("enablement:callrecording_create"), {
            "title": "New Call",
            "rep_name": "Eve",
            "coach_name": "",
            "call_type": "demo",
            "status": "pending",
            "duration_minutes": 45,
            "recording_url": "",
            "score": "",
            "coaching_notes": "",
            "call_date": today,
        })
        assert CallRecording.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a):
        today = timezone.localdate().isoformat()
        client_a.post(reverse("enablement:callrecording_create"), {
            "title": "Tenant Check Call",
            "rep_name": "Frank",
            "coach_name": "",
            "call_type": "discovery",
            "status": "pending",
            "duration_minutes": 0,
            "recording_url": "",
            "score": "",
            "coaching_notes": "",
            "call_date": today,
        })
        obj = CallRecording.objects.filter(title="Tenant Check Call").first()
        assert obj is not None
        assert obj.tenant == tenant_a

    def test_detail_200(self, client_a, recording_a):
        resp = client_a.get(reverse("enablement:callrecording_detail", args=[recording_a.pk]))
        assert resp.status_code == 200

    def test_edit_get_200(self, client_a, recording_a):
        resp = client_a.get(reverse("enablement:callrecording_edit", args=[recording_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates(self, client_a, recording_a):
        today = timezone.localdate().isoformat()
        client_a.post(reverse("enablement:callrecording_edit", args=[recording_a.pk]), {
            "title": "Updated Call Title",
            "rep_name": "Alice Updated",
            "coach_name": "Coach",
            "call_type": "negotiation",
            "status": "reviewed",
            "duration_minutes": 60,
            "recording_url": "",
            "score": "",
            "coaching_notes": "",
            "call_date": today,
        })
        recording_a.refresh_from_db()
        assert recording_a.title == "Updated Call Title"

    def test_delete_post_removes_recording(self, client_a, tenant_a):
        obj = CallRecording.objects.create(
            tenant=tenant_a,
            title="To Delete Call",
            rep_name="Rep",
            call_date=timezone.localdate(),
        )
        client_a.post(reverse("enablement:callrecording_delete", args=[obj.pk]))
        assert not CallRecording.objects.filter(pk=obj.pk).exists()


# ============================================================ CompetitiveCard CRUD
@pytest.mark.django_db
class TestCompetitiveCardCRUD:
    def test_list_200(self, client_a):
        resp = client_a.get(reverse("enablement:competitivecard_list"))
        assert resp.status_code == 200

    def test_list_context_has_cards(self, client_a, card_a):
        resp = client_a.get(reverse("enablement:competitivecard_list"))
        assert "cards" in resp.context

    def test_list_seeded_card_appears(self, client_a, card_a):
        resp = client_a.get(reverse("enablement:competitivecard_list"))
        pks = [obj.pk for obj in resp.context["cards"]]
        assert card_a.pk in pks

    def test_list_has_threat_choices_in_context(self, client_a):
        resp = client_a.get(reverse("enablement:competitivecard_list"))
        assert "threat_choices" in resp.context

    def test_list_has_status_choices_in_context(self, client_a):
        resp = client_a.get(reverse("enablement:competitivecard_list"))
        assert "status_choices" in resp.context

    def test_create_get_200(self, client_a):
        resp = client_a.get(reverse("enablement:competitivecard_create"))
        assert resp.status_code == 200

    def test_create_post_creates_card(self, client_a, tenant_a):
        today = timezone.localdate().isoformat()
        before = CompetitiveCard.objects.filter(tenant=tenant_a).count()
        client_a.post(reverse("enablement:competitivecard_create"), {
            "competitor_name": "New Rival",
            "category": "CRM",
            "threat_level": "medium",
            "status": "draft",
            "overview": "",
            "our_strengths": "",
            "their_strengths": "",
            "objection_handling": "",
            "owner": "",
            "last_updated_on": today,
        })
        assert CompetitiveCard.objects.filter(tenant=tenant_a).count() == before + 1

    def test_create_assigns_correct_tenant(self, client_a, tenant_a):
        today = timezone.localdate().isoformat()
        client_a.post(reverse("enablement:competitivecard_create"), {
            "competitor_name": "Tenant Check Rival",
            "category": "",
            "threat_level": "low",
            "status": "draft",
            "overview": "",
            "our_strengths": "",
            "their_strengths": "",
            "objection_handling": "",
            "owner": "",
            "last_updated_on": today,
        })
        obj = CompetitiveCard.objects.filter(competitor_name="Tenant Check Rival").first()
        assert obj is not None
        assert obj.tenant == tenant_a

    def test_detail_200(self, client_a, card_a):
        resp = client_a.get(reverse("enablement:competitivecard_detail", args=[card_a.pk]))
        assert resp.status_code == 200

    def test_edit_get_200(self, client_a, card_a):
        resp = client_a.get(reverse("enablement:competitivecard_edit", args=[card_a.pk]))
        assert resp.status_code == 200

    def test_edit_post_updates(self, client_a, card_a):
        today = timezone.localdate().isoformat()
        client_a.post(reverse("enablement:competitivecard_edit", args=[card_a.pk]), {
            "competitor_name": "Updated Rival Corp",
            "category": "SalesForce",
            "threat_level": "low",
            "status": "published",
            "overview": "Updated overview.",
            "our_strengths": "",
            "their_strengths": "",
            "objection_handling": "",
            "owner": "",
            "last_updated_on": today,
        })
        card_a.refresh_from_db()
        assert card_a.competitor_name == "Updated Rival Corp"

    def test_delete_post_removes_card(self, client_a, tenant_a):
        obj = CompetitiveCard.objects.create(
            tenant=tenant_a,
            competitor_name="To Delete Rival",
            last_updated_on=timezone.localdate(),
        )
        client_a.post(reverse("enablement:competitivecard_delete", args=[obj.pk]))
        assert not CompetitiveCard.objects.filter(pk=obj.pk).exists()

    def test_delete_post_redirects_to_list(self, client_a, tenant_a):
        obj = CompetitiveCard.objects.create(
            tenant=tenant_a,
            competitor_name="Delete Redirect Rival",
            last_updated_on=timezone.localdate(),
        )
        resp = client_a.post(reverse("enablement:competitivecard_delete", args=[obj.pk]))
        assert resp.status_code in (301, 302)
