"""Security tests: multi-tenant isolation, CSRF, and permission enforcement for enablement."""
import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from apps.enablement.models import (
    CallRecording, CompetitiveCard, ContentAsset, Playbook, TrainingRecord,
)


# ============================================================ cross-tenant isolation (404)
@pytest.mark.django_db
class TestCrossTenantIsolation404:
    """Tenant A must receive 404 (not 403/200) on ALL Tenant B resource URLs."""

    # --- ContentAsset ---
    def test_contentasset_detail_cross_tenant_404(self, client_a, asset_b):
        resp = client_a.get(reverse("enablement:contentasset_detail", args=[asset_b.pk]))
        assert resp.status_code == 404

    def test_contentasset_edit_cross_tenant_404(self, client_a, asset_b):
        resp = client_a.get(reverse("enablement:contentasset_edit", args=[asset_b.pk]))
        assert resp.status_code == 404

    def test_contentasset_delete_cross_tenant_404(self, client_a, asset_b):
        resp = client_a.post(reverse("enablement:contentasset_delete", args=[asset_b.pk]))
        assert resp.status_code == 404

    # --- Playbook ---
    def test_playbook_detail_cross_tenant_404(self, client_a, playbook_b):
        resp = client_a.get(reverse("enablement:playbook_detail", args=[playbook_b.pk]))
        assert resp.status_code == 404

    def test_playbook_edit_cross_tenant_404(self, client_a, playbook_b):
        resp = client_a.get(reverse("enablement:playbook_edit", args=[playbook_b.pk]))
        assert resp.status_code == 404

    def test_playbook_delete_cross_tenant_404(self, client_a, playbook_b):
        resp = client_a.post(reverse("enablement:playbook_delete", args=[playbook_b.pk]))
        assert resp.status_code == 404

    # --- TrainingRecord ---
    def test_trainingrecord_detail_cross_tenant_404(self, client_a, training_b):
        resp = client_a.get(reverse("enablement:trainingrecord_detail", args=[training_b.pk]))
        assert resp.status_code == 404

    def test_trainingrecord_edit_cross_tenant_404(self, client_a, training_b):
        resp = client_a.get(reverse("enablement:trainingrecord_edit", args=[training_b.pk]))
        assert resp.status_code == 404

    def test_trainingrecord_delete_cross_tenant_404(self, client_a, training_b):
        resp = client_a.post(reverse("enablement:trainingrecord_delete", args=[training_b.pk]))
        assert resp.status_code == 404

    # --- CallRecording ---
    def test_callrecording_detail_cross_tenant_404(self, client_a, recording_b):
        resp = client_a.get(reverse("enablement:callrecording_detail", args=[recording_b.pk]))
        assert resp.status_code == 404

    def test_callrecording_edit_cross_tenant_404(self, client_a, recording_b):
        resp = client_a.get(reverse("enablement:callrecording_edit", args=[recording_b.pk]))
        assert resp.status_code == 404

    def test_callrecording_delete_cross_tenant_404(self, client_a, recording_b):
        resp = client_a.post(reverse("enablement:callrecording_delete", args=[recording_b.pk]))
        assert resp.status_code == 404

    # --- CompetitiveCard ---
    def test_competitivecard_detail_cross_tenant_404(self, client_a, card_b):
        resp = client_a.get(reverse("enablement:competitivecard_detail", args=[card_b.pk]))
        assert resp.status_code == 404

    def test_competitivecard_edit_cross_tenant_404(self, client_a, card_b):
        resp = client_a.get(reverse("enablement:competitivecard_edit", args=[card_b.pk]))
        assert resp.status_code == 404

    def test_competitivecard_delete_cross_tenant_404(self, client_a, card_b):
        resp = client_a.post(reverse("enablement:competitivecard_delete", args=[card_b.pk]))
        assert resp.status_code == 404


# ============================================================ list isolation
@pytest.mark.django_db
class TestListIsolation:
    """List views for Tenant A should never include Tenant B rows."""

    def test_contentasset_list_excludes_tenant_b(self, client_a, asset_a, asset_b):
        resp = client_a.get(reverse("enablement:contentasset_list"))
        pks = [obj.pk for obj in resp.context["assets"]]
        assert asset_a.pk in pks
        assert asset_b.pk not in pks

    def test_playbook_list_excludes_tenant_b(self, client_a, playbook_a, playbook_b):
        resp = client_a.get(reverse("enablement:playbook_list"))
        pks = [obj.pk for obj in resp.context["playbooks"]]
        assert playbook_a.pk in pks
        assert playbook_b.pk not in pks

    def test_trainingrecord_list_excludes_tenant_b(self, client_a, training_a, training_b):
        resp = client_a.get(reverse("enablement:trainingrecord_list"))
        pks = [obj.pk for obj in resp.context["records"]]
        assert training_a.pk in pks
        assert training_b.pk not in pks

    def test_callrecording_list_excludes_tenant_b(self, client_a, recording_a, recording_b):
        resp = client_a.get(reverse("enablement:callrecording_list"))
        pks = [obj.pk for obj in resp.context["recordings"]]
        assert recording_a.pk in pks
        assert recording_b.pk not in pks

    def test_competitivecard_list_excludes_tenant_b(self, client_a, card_a, card_b):
        resp = client_a.get(reverse("enablement:competitivecard_list"))
        pks = [obj.pk for obj in resp.context["cards"]]
        assert card_a.pk in pks
        assert card_b.pk not in pks


# ============================================================ anonymous POST → no mutation
@pytest.mark.django_db
class TestAnonymousCannotMutate:
    """Anonymous users cannot create or delete records; data remains intact."""

    def test_anonymous_create_contentasset_redirects(self):
        c = Client()
        resp = c.post(reverse("enablement:contentasset_create"), {
            "title": "Anon Asset",
            "asset_type": "deck",
            "status": "draft",
        })
        assert resp.status_code in (301, 302)
        assert not ContentAsset.objects.filter(title="Anon Asset").exists()

    def test_anonymous_create_playbook_redirects(self):
        c = Client()
        resp = c.post(reverse("enablement:playbook_create"), {
            "title": "Anon Playbook",
            "stage": "discovery",
            "status": "draft",
            "version": "1.0",
        })
        assert resp.status_code in (301, 302)
        assert not Playbook.objects.filter(title="Anon Playbook").exists()

    def test_anonymous_delete_contentasset_no_mutation(self, asset_a):
        c = Client()
        resp = c.post(reverse("enablement:contentasset_delete", args=[asset_a.pk]))
        assert resp.status_code in (301, 302)
        # Asset must still exist
        assert ContentAsset.objects.filter(pk=asset_a.pk).exists()

    def test_anonymous_delete_playbook_no_mutation(self, playbook_a):
        c = Client()
        resp = c.post(reverse("enablement:playbook_delete", args=[playbook_a.pk]))
        assert resp.status_code in (301, 302)
        assert Playbook.objects.filter(pk=playbook_a.pk).exists()

    def test_anonymous_delete_trainingrecord_no_mutation(self, training_a):
        c = Client()
        resp = c.post(reverse("enablement:trainingrecord_delete", args=[training_a.pk]))
        assert resp.status_code in (301, 302)
        assert TrainingRecord.objects.filter(pk=training_a.pk).exists()

    def test_anonymous_delete_callrecording_no_mutation(self, recording_a):
        c = Client()
        resp = c.post(reverse("enablement:callrecording_delete", args=[recording_a.pk]))
        assert resp.status_code in (301, 302)
        assert CallRecording.objects.filter(pk=recording_a.pk).exists()

    def test_anonymous_delete_competitivecard_no_mutation(self, card_a):
        c = Client()
        resp = c.post(reverse("enablement:competitivecard_delete", args=[card_a.pk]))
        assert resp.status_code in (301, 302)
        assert CompetitiveCard.objects.filter(pk=card_a.pk).exists()


# ============================================================ rep (non-admin) blocked from write views
@pytest.mark.django_db
class TestRepBlockedFromWriteViews:
    """Non-admin reps are redirected away from create/edit/delete views."""

    def test_rep_cannot_create_contentasset(self, rep_client_a):
        resp = rep_client_a.get(reverse("enablement:contentasset_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_edit_contentasset(self, rep_client_a, asset_a):
        resp = rep_client_a.get(reverse("enablement:contentasset_edit", args=[asset_a.pk]))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_delete_contentasset(self, rep_client_a, asset_a):
        resp = rep_client_a.post(reverse("enablement:contentasset_delete", args=[asset_a.pk]))
        assert resp.status_code in (301, 302)
        # Asset must still exist (rep was blocked)
        assert ContentAsset.objects.filter(pk=asset_a.pk).exists()

    def test_rep_cannot_create_playbook(self, rep_client_a):
        resp = rep_client_a.get(reverse("enablement:playbook_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_edit_playbook(self, rep_client_a, playbook_a):
        resp = rep_client_a.get(reverse("enablement:playbook_edit", args=[playbook_a.pk]))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_trainingrecord(self, rep_client_a):
        resp = rep_client_a.get(reverse("enablement:trainingrecord_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_edit_trainingrecord(self, rep_client_a, training_a):
        resp = rep_client_a.get(reverse("enablement:trainingrecord_edit", args=[training_a.pk]))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_callrecording(self, rep_client_a):
        resp = rep_client_a.get(reverse("enablement:callrecording_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_edit_callrecording(self, rep_client_a, recording_a):
        resp = rep_client_a.get(reverse("enablement:callrecording_edit", args=[recording_a.pk]))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_create_competitivecard(self, rep_client_a):
        resp = rep_client_a.get(reverse("enablement:competitivecard_create"))
        assert resp.status_code in (301, 302)

    def test_rep_cannot_edit_competitivecard(self, rep_client_a, card_a):
        resp = rep_client_a.get(reverse("enablement:competitivecard_edit", args=[card_a.pk]))
        assert resp.status_code in (301, 302)

    def test_rep_can_view_contentasset_list(self, rep_client_a):
        """Reps can READ list pages — only write operations are blocked."""
        resp = rep_client_a.get(reverse("enablement:contentasset_list"))
        assert resp.status_code == 200

    def test_rep_can_view_playbook_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("enablement:playbook_list"))
        assert resp.status_code == 200

    def test_rep_can_view_trainingrecord_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("enablement:trainingrecord_list"))
        assert resp.status_code == 200

    def test_rep_can_view_callrecording_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("enablement:callrecording_list"))
        assert resp.status_code == 200

    def test_rep_can_view_competitivecard_list(self, rep_client_a):
        resp = rep_client_a.get(reverse("enablement:competitivecard_list"))
        assert resp.status_code == 200

    def test_rep_can_view_contentasset_detail(self, rep_client_a, asset_a):
        resp = rep_client_a.get(reverse("enablement:contentasset_detail", args=[asset_a.pk]))
        assert resp.status_code == 200

    def test_rep_can_view_playbook_detail(self, rep_client_a, playbook_a):
        resp = rep_client_a.get(reverse("enablement:playbook_detail", args=[playbook_a.pk]))
        assert resp.status_code == 200


# ============================================================ CSRF enforcement
@pytest.mark.django_db
class TestCSRFEnforcement:
    """Anonymous CSRF-enforced POST hits are rejected (302 or 403)."""

    def test_anonymous_csrf_create_contentasset(self):
        c = Client(enforce_csrf_checks=True)
        resp = c.post(reverse("enablement:contentasset_create"), {
            "title": "CSRF Test Asset",
            "asset_type": "deck",
            "status": "draft",
        })
        assert resp.status_code in (301, 302, 403)

    def test_anonymous_csrf_delete_playbook(self, playbook_a):
        c = Client(enforce_csrf_checks=True)
        resp = c.post(reverse("enablement:playbook_delete", args=[playbook_a.pk]))
        assert resp.status_code in (301, 302, 403)
        # playbook must still exist
        assert Playbook.objects.filter(pk=playbook_a.pk).exists()

    def test_anonymous_csrf_create_competitivecard(self):
        today = timezone.localdate().isoformat()
        c = Client(enforce_csrf_checks=True)
        resp = c.post(reverse("enablement:competitivecard_create"), {
            "competitor_name": "CSRF Rival",
            "threat_level": "medium",
            "status": "draft",
            "last_updated_on": today,
        })
        assert resp.status_code in (301, 302, 403)
        assert not CompetitiveCard.objects.filter(competitor_name="CSRF Rival").exists()
