from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.decorators import tenant_admin_required
from apps.core.utils import log_action

from .forms import (
    CallRecordingForm, CompetitiveCardForm, ContentAssetForm,
    PlaybookForm, TrainingRecordForm,
)
from .models import (
    CallRecording, CompetitiveCard, ContentAsset, Playbook, TrainingRecord,
)


def _no_tenant_redirect(request):
    messages.info(request, "Switch to a tenant workspace to manage this — the superuser has no tenant.")
    return redirect("dashboard:index")


def _page(request, qs, per_page=12):
    paginator = Paginator(qs, per_page)
    return paginator, paginator.get_page(request.GET.get("page"))


# ============================================================ content assets
@login_required
def contentasset_list(request):
    qs = ContentAsset.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(title__icontains=q) | Q(description__icontains=q)
            | Q(tags__icontains=q) | Q(owner__icontains=q)
        )
    asset_type = request.GET.get("asset_type", "")
    if asset_type:
        qs = qs.filter(asset_type=asset_type)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "enablement/contentasset_list.html", {
        "page_title": "Content Repository & Search", "page_obj": page_obj,
        "assets": page_obj.object_list, "type_choices": ContentAsset.TYPE_CHOICES,
        "status_choices": ContentAsset.STATUS_CHOICES, "total": paginator.count,
    })


@tenant_admin_required
def contentasset_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = ContentAssetForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Content asset added.")
        return redirect("enablement:contentasset_list")
    return render(request, "enablement/contentasset_form.html",
                  {"form": form, "page_title": "Add Content Asset", "mode": "create"})


@login_required
def contentasset_detail(request, pk):
    obj = get_object_or_404(ContentAsset, pk=pk, tenant=request.tenant)
    return render(request, "enablement/contentasset_detail.html", {"obj": obj, "page_title": obj.title})


@tenant_admin_required
def contentasset_edit(request, pk):
    obj = get_object_or_404(ContentAsset, pk=pk, tenant=request.tenant)
    form = ContentAssetForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Content asset updated.")
        return redirect("enablement:contentasset_detail", pk=obj.pk)
    return render(request, "enablement/contentasset_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.title}", "mode": "edit"})


@tenant_admin_required
def contentasset_delete(request, pk):
    obj = get_object_or_404(ContentAsset, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.title
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Content asset “{label}” deleted.")
    return redirect("enablement:contentasset_list")


# ============================================================ playbooks
@login_required
def playbook_list(request):
    qs = Playbook.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(title__icontains=q) | Q(persona__icontains=q)
            | Q(summary__icontains=q) | Q(owner__icontains=q)
        )
    stage = request.GET.get("stage", "")
    if stage:
        qs = qs.filter(stage=stage)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "enablement/playbook_list.html", {
        "page_title": "Sales Playbooks & Guidance", "page_obj": page_obj,
        "playbooks": page_obj.object_list, "stage_choices": Playbook.STAGE_CHOICES,
        "status_choices": Playbook.STATUS_CHOICES, "total": paginator.count,
    })


@tenant_admin_required
def playbook_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = PlaybookForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Playbook added.")
        return redirect("enablement:playbook_list")
    return render(request, "enablement/playbook_form.html",
                  {"form": form, "page_title": "Add Playbook", "mode": "create"})


@login_required
def playbook_detail(request, pk):
    obj = get_object_or_404(Playbook, pk=pk, tenant=request.tenant)
    return render(request, "enablement/playbook_detail.html", {"obj": obj, "page_title": obj.title})


@tenant_admin_required
def playbook_edit(request, pk):
    obj = get_object_or_404(Playbook, pk=pk, tenant=request.tenant)
    form = PlaybookForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Playbook updated.")
        return redirect("enablement:playbook_detail", pk=obj.pk)
    return render(request, "enablement/playbook_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.title}", "mode": "edit"})


@tenant_admin_required
def playbook_delete(request, pk):
    obj = get_object_or_404(Playbook, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.title
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Playbook “{label}” deleted.")
    return redirect("enablement:playbook_list")


# ============================================================ training records
@login_required
def trainingrecord_list(request):
    qs = TrainingRecord.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(course_name__icontains=q) | Q(rep_name__icontains=q)
            | Q(provider__icontains=q)
        )
    kind = request.GET.get("kind", "")
    if kind:
        qs = qs.filter(kind=kind)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "enablement/trainingrecord_list.html", {
        "page_title": "Training & Certification Tracking", "page_obj": page_obj,
        "records": page_obj.object_list, "kind_choices": TrainingRecord.KIND_CHOICES,
        "status_choices": TrainingRecord.STATUS_CHOICES, "total": paginator.count,
    })


@tenant_admin_required
def trainingrecord_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = TrainingRecordForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Training record added.")
        return redirect("enablement:trainingrecord_list")
    return render(request, "enablement/trainingrecord_form.html",
                  {"form": form, "page_title": "Add Training Record", "mode": "create"})


@login_required
def trainingrecord_detail(request, pk):
    obj = get_object_or_404(TrainingRecord, pk=pk, tenant=request.tenant)
    return render(request, "enablement/trainingrecord_detail.html", {"obj": obj, "page_title": str(obj)})


@tenant_admin_required
def trainingrecord_edit(request, pk):
    obj = get_object_or_404(TrainingRecord, pk=pk, tenant=request.tenant)
    form = TrainingRecordForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Training record updated.")
        return redirect("enablement:trainingrecord_detail", pk=obj.pk)
    return render(request, "enablement/trainingrecord_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj}", "mode": "edit"})


@tenant_admin_required
def trainingrecord_delete(request, pk):
    obj = get_object_or_404(TrainingRecord, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, "Training record deleted.")
    return redirect("enablement:trainingrecord_list")


# ============================================================ call recordings
@login_required
def callrecording_list(request):
    qs = CallRecording.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(title__icontains=q) | Q(rep_name__icontains=q)
            | Q(coach_name__icontains=q) | Q(coaching_notes__icontains=q)
        )
    call_type = request.GET.get("call_type", "")
    if call_type:
        qs = qs.filter(call_type=call_type)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "enablement/callrecording_list.html", {
        "page_title": "Coaching & Call Recording", "page_obj": page_obj,
        "recordings": page_obj.object_list, "type_choices": CallRecording.TYPE_CHOICES,
        "status_choices": CallRecording.STATUS_CHOICES, "total": paginator.count,
    })


@tenant_admin_required
def callrecording_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = CallRecordingForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Call recording added.")
        return redirect("enablement:callrecording_list")
    return render(request, "enablement/callrecording_form.html",
                  {"form": form, "page_title": "Add Call Recording", "mode": "create"})


@login_required
def callrecording_detail(request, pk):
    obj = get_object_or_404(CallRecording, pk=pk, tenant=request.tenant)
    return render(request, "enablement/callrecording_detail.html", {"obj": obj, "page_title": obj.title})


@tenant_admin_required
def callrecording_edit(request, pk):
    obj = get_object_or_404(CallRecording, pk=pk, tenant=request.tenant)
    form = CallRecordingForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Call recording updated.")
        return redirect("enablement:callrecording_detail", pk=obj.pk)
    return render(request, "enablement/callrecording_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.title}", "mode": "edit"})


@tenant_admin_required
def callrecording_delete(request, pk):
    obj = get_object_or_404(CallRecording, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.title
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Call recording “{label}” deleted.")
    return redirect("enablement:callrecording_list")


# ============================================================ competitive cards
@login_required
def competitivecard_list(request):
    qs = CompetitiveCard.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(competitor_name__icontains=q) | Q(category__icontains=q)
            | Q(overview__icontains=q) | Q(owner__icontains=q)
        )
    threat_level = request.GET.get("threat_level", "")
    if threat_level:
        qs = qs.filter(threat_level=threat_level)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "enablement/competitivecard_list.html", {
        "page_title": "Competitive Intelligence Library", "page_obj": page_obj,
        "cards": page_obj.object_list, "threat_choices": CompetitiveCard.THREAT_CHOICES,
        "status_choices": CompetitiveCard.STATUS_CHOICES, "total": paginator.count,
    })


@tenant_admin_required
def competitivecard_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = CompetitiveCardForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Competitive card added.")
        return redirect("enablement:competitivecard_list")
    return render(request, "enablement/competitivecard_form.html",
                  {"form": form, "page_title": "Add Competitive Card", "mode": "create"})


@login_required
def competitivecard_detail(request, pk):
    obj = get_object_or_404(CompetitiveCard, pk=pk, tenant=request.tenant)
    return render(request, "enablement/competitivecard_detail.html", {"obj": obj, "page_title": obj.competitor_name})


@tenant_admin_required
def competitivecard_edit(request, pk):
    obj = get_object_or_404(CompetitiveCard, pk=pk, tenant=request.tenant)
    form = CompetitiveCardForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Competitive card updated.")
        return redirect("enablement:competitivecard_detail", pk=obj.pk)
    return render(request, "enablement/competitivecard_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.competitor_name}", "mode": "edit"})


@tenant_admin_required
def competitivecard_delete(request, pk):
    obj = get_object_or_404(CompetitiveCard, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.competitor_name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Competitive card “{label}” deleted.")
    return redirect("enablement:competitivecard_list")
