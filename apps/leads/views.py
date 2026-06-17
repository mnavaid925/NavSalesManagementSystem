from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.decorators import tenant_admin_required
from apps.core.utils import log_action

from .forms import (
    LeadConversionForm, LeadForm, LeadScoreForm, LeadSourceForm, NurtureCampaignForm,
)
from .models import (
    Lead, LeadConversion, LeadScore, LeadSource, NurtureCampaign,
)


def _no_tenant_redirect(request):
    messages.info(request, "Switch to a tenant workspace to manage this — the superuser has no tenant.")
    return redirect("dashboard:index")


def _page(request, qs, per_page=12):
    paginator = Paginator(qs, per_page)
    return paginator, paginator.get_page(request.GET.get("page"))


# ============================================================ lead sources
@login_required
def leadsource_list(request):
    qs = LeadSource.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(default_owner__icontains=q) | Q(description__icontains=q))
    source_type = request.GET.get("source_type", "")
    if source_type:
        qs = qs.filter(source_type=source_type)
    routing = request.GET.get("routing_rule", "")
    if routing:
        qs = qs.filter(routing_rule=routing)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "leads/leadsource_list.html", {
        "page_title": "Lead Qualification & Routing", "page_obj": page_obj,
        "sources": page_obj.object_list, "type_choices": LeadSource.TYPE_CHOICES,
        "routing_choices": LeadSource.ROUTING_CHOICES, "status_choices": LeadSource.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def leadsource_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = LeadSourceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Lead source created.")
        return redirect("leads:leadsource_list")
    return render(request, "leads/leadsource_form.html",
                  {"form": form, "page_title": "Add Lead Source", "mode": "create"})


@login_required
def leadsource_detail(request, pk):
    obj = get_object_or_404(LeadSource, pk=pk, tenant=request.tenant)
    leads = obj.leads.all()[:20]
    return render(request, "leads/leadsource_detail.html",
                  {"obj": obj, "leads": leads, "page_title": obj.name})


@tenant_admin_required
def leadsource_edit(request, pk):
    obj = get_object_or_404(LeadSource, pk=pk, tenant=request.tenant)
    form = LeadSourceForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Lead source updated.")
        return redirect("leads:leadsource_detail", pk=obj.pk)
    return render(request, "leads/leadsource_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.name}", "mode": "edit"})


@tenant_admin_required
def leadsource_delete(request, pk):
    obj = get_object_or_404(LeadSource, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Lead source “{label}” deleted.")
    return redirect("leads:leadsource_list")


# ============================================================ nurture campaigns
@login_required
def nurturecampaign_list(request):
    qs = NurtureCampaign.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(goal__icontains=q))
    channel = request.GET.get("channel", "")
    if channel:
        qs = qs.filter(channel=channel)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "leads/nurturecampaign_list.html", {
        "page_title": "Lead Nurturing & Drip Campaigns", "page_obj": page_obj,
        "campaigns": page_obj.object_list, "channel_choices": NurtureCampaign.CHANNEL_CHOICES,
        "status_choices": NurtureCampaign.STATUS_CHOICES, "total": paginator.count,
    })


@tenant_admin_required
def nurturecampaign_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = NurtureCampaignForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Campaign created.")
        return redirect("leads:nurturecampaign_list")
    return render(request, "leads/nurturecampaign_form.html",
                  {"form": form, "page_title": "Add Campaign", "mode": "create"})


@login_required
def nurturecampaign_detail(request, pk):
    obj = get_object_or_404(NurtureCampaign, pk=pk, tenant=request.tenant)
    leads = obj.leads.all()[:20]
    return render(request, "leads/nurturecampaign_detail.html",
                  {"obj": obj, "leads": leads, "page_title": obj.name})


@tenant_admin_required
def nurturecampaign_edit(request, pk):
    obj = get_object_or_404(NurtureCampaign, pk=pk, tenant=request.tenant)
    form = NurtureCampaignForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Campaign updated.")
        return redirect("leads:nurturecampaign_detail", pk=obj.pk)
    return render(request, "leads/nurturecampaign_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.name}", "mode": "edit"})


@tenant_admin_required
def nurturecampaign_delete(request, pk):
    obj = get_object_or_404(NurtureCampaign, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Campaign “{label}” deleted.")
    return redirect("leads:nurturecampaign_list")


# ============================================================ leads
@login_required
def lead_list(request):
    qs = Lead.objects.filter(tenant=request.tenant).select_related("source", "campaign")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q)
            | Q(company__icontains=q) | Q(email__icontains=q) | Q(owner__icontains=q))
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    rating = request.GET.get("rating", "")
    if rating:
        qs = qs.filter(rating=rating)
    source = request.GET.get("source", "")
    if source:
        qs = qs.filter(source_id=source)
    paginator, page_obj = _page(request, qs)
    return render(request, "leads/lead_list.html", {
        "page_title": "Lead Capture & Ingestion", "page_obj": page_obj,
        "leads": page_obj.object_list, "status_choices": Lead.STATUS_CHOICES,
        "rating_choices": Lead.RATING_CHOICES,
        "sources": LeadSource.objects.filter(tenant=request.tenant),
        "total": paginator.count,
    })


@tenant_admin_required
def lead_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = LeadForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, f"Lead {obj.number} captured.")
        return redirect("leads:lead_list")
    return render(request, "leads/lead_form.html",
                  {"form": form, "page_title": "Add Lead", "mode": "create"})


@login_required
def lead_detail(request, pk):
    obj = get_object_or_404(
        Lead.objects.select_related("source", "campaign"), pk=pk, tenant=request.tenant)
    scores = obj.scores.all()[:20]
    conversions = obj.conversions.all()[:20]
    return render(request, "leads/lead_detail.html",
                  {"obj": obj, "scores": scores, "conversions": conversions, "page_title": obj.full_name})


@tenant_admin_required
def lead_edit(request, pk):
    obj = get_object_or_404(Lead, pk=pk, tenant=request.tenant)
    form = LeadForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Lead updated.")
        return redirect("leads:lead_detail", pk=obj.pk)
    return render(request, "leads/lead_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.full_name}", "mode": "edit"})


@tenant_admin_required
def lead_delete(request, pk):
    obj = get_object_or_404(Lead, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.number
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Lead {label} deleted.")
    return redirect("leads:lead_list")


# ============================================================ lead scores
@login_required
def leadscore_list(request):
    qs = LeadScore.objects.filter(tenant=request.tenant).select_related("lead")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(lead__first_name__icontains=q) | Q(lead__last_name__icontains=q)
            | Q(lead__number__icontains=q) | Q(reason__icontains=q))
    grade = request.GET.get("grade", "")
    if grade:
        qs = qs.filter(grade=grade)
    scoring_model = request.GET.get("scoring_model", "")
    if scoring_model:
        qs = qs.filter(scoring_model=scoring_model)
    paginator, page_obj = _page(request, qs)
    return render(request, "leads/leadscore_list.html", {
        "page_title": "Lead Scoring & Grading", "page_obj": page_obj,
        "scores": page_obj.object_list, "grade_choices": LeadScore.GRADE_CHOICES,
        "model_choices": LeadScore.MODEL_CHOICES, "total": paginator.count,
    })


@tenant_admin_required
def leadscore_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = LeadScoreForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Score recorded.")
        return redirect("leads:leadscore_list")
    return render(request, "leads/leadscore_form.html",
                  {"form": form, "page_title": "Add Score", "mode": "create"})


@login_required
def leadscore_detail(request, pk):
    obj = get_object_or_404(LeadScore.objects.select_related("lead"), pk=pk, tenant=request.tenant)
    return render(request, "leads/leadscore_detail.html", {"obj": obj, "page_title": str(obj)})


@tenant_admin_required
def leadscore_edit(request, pk):
    obj = get_object_or_404(LeadScore, pk=pk, tenant=request.tenant)
    form = LeadScoreForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Score updated.")
        return redirect("leads:leadscore_detail", pk=obj.pk)
    return render(request, "leads/leadscore_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit score", "mode": "edit"})


@tenant_admin_required
def leadscore_delete(request, pk):
    obj = get_object_or_404(LeadScore, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, "Score deleted.")
    return redirect("leads:leadscore_list")


# ============================================================ lead conversions
@login_required
def leadconversion_list(request):
    qs = LeadConversion.objects.filter(tenant=request.tenant).select_related("lead")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(lead__first_name__icontains=q)
            | Q(lead__last_name__icontains=q) | Q(assigned_to__icontains=q))
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    outcome = request.GET.get("outcome", "")
    if outcome:
        qs = qs.filter(outcome=outcome)
    paginator, page_obj = _page(request, qs)
    return render(request, "leads/leadconversion_list.html", {
        "page_title": "Lead Conversion & Handoff", "page_obj": page_obj,
        "conversions": page_obj.object_list, "status_choices": LeadConversion.STATUS_CHOICES,
        "outcome_choices": LeadConversion.OUTCOME_CHOICES, "total": paginator.count,
    })


@tenant_admin_required
def leadconversion_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = LeadConversionForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, f"Conversion {obj.number} created.")
        return redirect("leads:leadconversion_list")
    return render(request, "leads/leadconversion_form.html",
                  {"form": form, "page_title": "Add Conversion", "mode": "create"})


@login_required
def leadconversion_detail(request, pk):
    obj = get_object_or_404(
        LeadConversion.objects.select_related("lead"), pk=pk, tenant=request.tenant)
    return render(request, "leads/leadconversion_detail.html", {"obj": obj, "page_title": obj.number})


@tenant_admin_required
def leadconversion_edit(request, pk):
    obj = get_object_or_404(LeadConversion, pk=pk, tenant=request.tenant)
    form = LeadConversionForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Conversion updated.")
        return redirect("leads:leadconversion_detail", pk=obj.pk)
    return render(request, "leads/leadconversion_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.number}", "mode": "edit"})


@tenant_admin_required
def leadconversion_delete(request, pk):
    obj = get_object_or_404(LeadConversion, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.number
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Conversion {label} deleted.")
    return redirect("leads:leadconversion_list")
