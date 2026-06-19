from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.decorators import tenant_admin_required
from apps.core.utils import log_action

from .forms import (
    CampaignInfluenceForm, CampaignPerformanceForm, ContentEngagementForm,
    MarketingEventForm, MQLHandoffForm,
)
from .models import (
    CampaignInfluence, CampaignPerformance, ContentEngagement, MarketingEvent, MQLHandoff,
)


def _no_tenant_redirect(request):
    messages.info(request, "Switch to a tenant workspace to manage this — the superuser has no tenant.")
    return redirect("dashboard:index")


def _page(request, qs, per_page=12):
    paginator = Paginator(qs, per_page)
    return paginator, paginator.get_page(request.GET.get("page"))


# ============================================================ campaign influence
@login_required
def campaigninfluence_list(request):
    qs = CampaignInfluence.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(campaign_name__icontains=q) | Q(period_label__icontains=q))
    model_type = request.GET.get("model_type", "")
    if model_type:
        qs = qs.filter(model_type=model_type)
    paginator, page_obj = _page(request, qs)
    return render(request, "marketing/campaigninfluence_list.html", {
        "page_title": "Campaign Influence & Attribution", "page_obj": page_obj,
        "campaigninfluences": page_obj.object_list,
        "model_type_choices": CampaignInfluence.MODEL_TYPE_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def campaigninfluence_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = CampaignInfluenceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Campaign influence recorded.")
        return redirect("marketing:campaigninfluence_list")
    return render(request, "marketing/campaigninfluence_form.html",
                  {"form": form, "page_title": "Add Campaign Influence", "mode": "create"})


@login_required
def campaigninfluence_detail(request, pk):
    obj = get_object_or_404(CampaignInfluence, pk=pk, tenant=request.tenant)
    return render(request, "marketing/campaigninfluence_detail.html",
                  {"obj": obj, "page_title": obj.campaign_name})


@tenant_admin_required
def campaigninfluence_edit(request, pk):
    obj = get_object_or_404(CampaignInfluence, pk=pk, tenant=request.tenant)
    form = CampaignInfluenceForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Campaign influence updated.")
        return redirect("marketing:campaigninfluence_detail", pk=obj.pk)
    return render(request, "marketing/campaigninfluence_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.campaign_name}", "mode": "edit"})


@tenant_admin_required
def campaigninfluence_delete(request, pk):
    obj = get_object_or_404(CampaignInfluence, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.campaign_name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Campaign influence “{label}” deleted.")
    return redirect("marketing:campaigninfluence_list")


# ============================================================ MQL handoffs
@login_required
def mqlhandoff_list(request):
    qs = MQLHandoff.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(lead_name__icontains=q) | Q(company__icontains=q))
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "marketing/mqlhandoff_list.html", {
        "page_title": "MQL-to-SQL Tracking", "page_obj": page_obj,
        "mqlhandoffs": page_obj.object_list,
        "status_choices": MQLHandoff.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def mqlhandoff_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = MQLHandoffForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, f"Handoff {obj.number} recorded.")
        return redirect("marketing:mqlhandoff_list")
    return render(request, "marketing/mqlhandoff_form.html",
                  {"form": form, "page_title": "Add MQL Handoff", "mode": "create"})


@login_required
def mqlhandoff_detail(request, pk):
    obj = get_object_or_404(MQLHandoff, pk=pk, tenant=request.tenant)
    return render(request, "marketing/mqlhandoff_detail.html",
                  {"obj": obj, "page_title": obj.number})


@tenant_admin_required
def mqlhandoff_edit(request, pk):
    obj = get_object_or_404(MQLHandoff, pk=pk, tenant=request.tenant)
    form = MQLHandoffForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Handoff updated.")
        return redirect("marketing:mqlhandoff_detail", pk=obj.pk)
    return render(request, "marketing/mqlhandoff_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.number}", "mode": "edit"})


@tenant_admin_required
def mqlhandoff_delete(request, pk):
    obj = get_object_or_404(MQLHandoff, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.number
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Handoff {label} deleted.")
    return redirect("marketing:mqlhandoff_list")


# ============================================================ campaign performance
@login_required
def campaignperformance_list(request):
    qs = CampaignPerformance.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(campaign_name__icontains=q) | Q(notes__icontains=q))
    channel = request.GET.get("channel", "")
    if channel:
        qs = qs.filter(channel=channel)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "marketing/campaignperformance_list.html", {
        "page_title": "Campaign Performance Integration", "page_obj": page_obj,
        "campaignperformances": page_obj.object_list,
        "channel_choices": CampaignPerformance.CHANNEL_CHOICES,
        "status_choices": CampaignPerformance.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def campaignperformance_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = CampaignPerformanceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Campaign performance recorded.")
        return redirect("marketing:campaignperformance_list")
    return render(request, "marketing/campaignperformance_form.html",
                  {"form": form, "page_title": "Add Campaign Performance", "mode": "create"})


@login_required
def campaignperformance_detail(request, pk):
    obj = get_object_or_404(CampaignPerformance, pk=pk, tenant=request.tenant)
    return render(request, "marketing/campaignperformance_detail.html",
                  {"obj": obj, "page_title": obj.campaign_name})


@tenant_admin_required
def campaignperformance_edit(request, pk):
    obj = get_object_or_404(CampaignPerformance, pk=pk, tenant=request.tenant)
    form = CampaignPerformanceForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Campaign performance updated.")
        return redirect("marketing:campaignperformance_detail", pk=obj.pk)
    return render(request, "marketing/campaignperformance_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.campaign_name}", "mode": "edit"})


@tenant_admin_required
def campaignperformance_delete(request, pk):
    obj = get_object_or_404(CampaignPerformance, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.campaign_name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Campaign performance “{label}” deleted.")
    return redirect("marketing:campaignperformance_list")


# ============================================================ content engagement
@login_required
def contentengagement_list(request):
    qs = ContentEngagement.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(content_title__icontains=q))
    content_type = request.GET.get("content_type", "")
    if content_type:
        qs = qs.filter(content_type=content_type)
    paginator, page_obj = _page(request, qs)
    return render(request, "marketing/contentengagement_list.html", {
        "page_title": "Content Performance & Engagement", "page_obj": page_obj,
        "contentengagements": page_obj.object_list,
        "content_type_choices": ContentEngagement.CONTENT_TYPE_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def contentengagement_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = ContentEngagementForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Content engagement recorded.")
        return redirect("marketing:contentengagement_list")
    return render(request, "marketing/contentengagement_form.html",
                  {"form": form, "page_title": "Add Content Engagement", "mode": "create"})


@login_required
def contentengagement_detail(request, pk):
    obj = get_object_or_404(ContentEngagement, pk=pk, tenant=request.tenant)
    return render(request, "marketing/contentengagement_detail.html",
                  {"obj": obj, "page_title": obj.content_title})


@tenant_admin_required
def contentengagement_edit(request, pk):
    obj = get_object_or_404(ContentEngagement, pk=pk, tenant=request.tenant)
    form = ContentEngagementForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Content engagement updated.")
        return redirect("marketing:contentengagement_detail", pk=obj.pk)
    return render(request, "marketing/contentengagement_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.content_title}", "mode": "edit"})


@tenant_admin_required
def contentengagement_delete(request, pk):
    obj = get_object_or_404(ContentEngagement, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.content_title
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Content engagement “{label}” deleted.")
    return redirect("marketing:contentengagement_list")


# ============================================================ marketing events
@login_required
def marketingevent_list(request):
    qs = MarketingEvent.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(name__icontains=q) | Q(location__icontains=q))
    event_type = request.GET.get("event_type", "")
    if event_type:
        qs = qs.filter(event_type=event_type)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "marketing/marketingevent_list.html", {
        "page_title": "Event & Webinar Management", "page_obj": page_obj,
        "marketingevents": page_obj.object_list,
        "event_type_choices": MarketingEvent.EVENT_TYPE_CHOICES,
        "status_choices": MarketingEvent.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def marketingevent_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = MarketingEventForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, f"Event {obj.number} created.")
        return redirect("marketing:marketingevent_list")
    return render(request, "marketing/marketingevent_form.html",
                  {"form": form, "page_title": "Add Marketing Event", "mode": "create"})


@login_required
def marketingevent_detail(request, pk):
    obj = get_object_or_404(MarketingEvent, pk=pk, tenant=request.tenant)
    return render(request, "marketing/marketingevent_detail.html",
                  {"obj": obj, "page_title": obj.number})


@tenant_admin_required
def marketingevent_edit(request, pk):
    obj = get_object_or_404(MarketingEvent, pk=pk, tenant=request.tenant)
    form = MarketingEventForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Event updated.")
        return redirect("marketing:marketingevent_detail", pk=obj.pk)
    return render(request, "marketing/marketingevent_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.number}", "mode": "edit"})


@tenant_admin_required
def marketingevent_delete(request, pk):
    obj = get_object_or_404(MarketingEvent, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.number
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Event {label} deleted.")
    return redirect("marketing:marketingevent_list")
