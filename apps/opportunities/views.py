from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.core.decorators import tenant_admin_required
from apps.core.utils import log_action

from .forms import (
    CompetitorForm, DealCollaboratorForm, OpportunityActivityForm,
    OpportunityForm, PipelineStageForm,
)
from .models import (
    Competitor, DealCollaborator, Opportunity, OpportunityActivity, PipelineStage,
)


def _no_tenant_redirect(request):
    messages.info(request, "Switch to a tenant workspace to manage this — the superuser has no tenant.")
    return redirect("dashboard:index")


def _page(request, qs, per_page=12):
    paginator = Paginator(qs, per_page)
    return paginator, paginator.get_page(request.GET.get("page"))


# ============================================================ pipeline stages
@login_required
def pipelinestage_list(request):
    qs = PipelineStage.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
    stage_type = request.GET.get("stage_type", "")
    if stage_type:
        qs = qs.filter(stage_type=stage_type)
    paginator, page_obj = _page(request, qs)
    return render(request, "opportunities/pipelinestage_list.html", {
        "page_title": "Pipeline Visibility & Forecasting", "page_obj": page_obj,
        "stages": page_obj.object_list, "type_choices": PipelineStage.TYPE_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def pipelinestage_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = PipelineStageForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Pipeline stage added.")
        return redirect("opportunities:pipelinestage_list")
    return render(request, "opportunities/pipelinestage_form.html",
                  {"form": form, "page_title": "Add Pipeline Stage", "mode": "create"})


@login_required
def pipelinestage_detail(request, pk):
    obj = get_object_or_404(PipelineStage, pk=pk, tenant=request.tenant)
    opportunities = obj.opportunities.all()[:20]
    return render(request, "opportunities/pipelinestage_detail.html",
                  {"obj": obj, "opportunities": opportunities, "page_title": obj.name})


@tenant_admin_required
def pipelinestage_edit(request, pk):
    obj = get_object_or_404(PipelineStage, pk=pk, tenant=request.tenant)
    form = PipelineStageForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Pipeline stage updated.")
        return redirect("opportunities:pipelinestage_detail", pk=obj.pk)
    return render(request, "opportunities/pipelinestage_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.name}", "mode": "edit"})


@tenant_admin_required
@require_POST
def pipelinestage_delete(request, pk):
    obj = get_object_or_404(PipelineStage, pk=pk, tenant=request.tenant)
    label = obj.name
    log_action(request, "delete", instance=obj)
    obj.delete()
    messages.success(request, f"Pipeline stage “{label}” deleted.")
    return redirect("opportunities:pipelinestage_list")


# ============================================================ opportunities
@login_required
def opportunity_list(request):
    qs = Opportunity.objects.filter(tenant=request.tenant).select_related("stage")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(name__icontains=q)
            | Q(account_name__icontains=q) | Q(owner_name__icontains=q))
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    priority = request.GET.get("priority", "")
    if priority:
        qs = qs.filter(priority=priority)
    stage = request.GET.get("stage", "")
    if stage:
        qs = qs.filter(stage_id=stage)
    paginator, page_obj = _page(request, qs)
    return render(request, "opportunities/opportunity_list.html", {
        "page_title": "Opportunity Creation & Staging", "page_obj": page_obj,
        "opportunities": page_obj.object_list,
        "status_choices": Opportunity.STATUS_CHOICES,
        "priority_choices": Opportunity.PRIORITY_CHOICES,
        "stages": PipelineStage.objects.filter(tenant=request.tenant),
        "total": paginator.count,
    })


@tenant_admin_required
def opportunity_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = OpportunityForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, f"Opportunity {obj.number} created.")
        return redirect("opportunities:opportunity_list")
    return render(request, "opportunities/opportunity_form.html",
                  {"form": form, "page_title": "Add Opportunity", "mode": "create"})


@login_required
def opportunity_detail(request, pk):
    obj = get_object_or_404(
        Opportunity.objects.select_related("stage"), pk=pk, tenant=request.tenant)
    activities = obj.activities.all()[:20]
    competitors = obj.competitors.all()[:20]
    collaborators = obj.collaborators.all()[:20]
    return render(request, "opportunities/opportunity_detail.html", {
        "obj": obj, "activities": activities, "competitors": competitors,
        "collaborators": collaborators, "page_title": obj.name,
    })


@tenant_admin_required
def opportunity_edit(request, pk):
    obj = get_object_or_404(Opportunity, pk=pk, tenant=request.tenant)
    form = OpportunityForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Opportunity updated.")
        return redirect("opportunities:opportunity_detail", pk=obj.pk)
    return render(request, "opportunities/opportunity_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.name}", "mode": "edit"})


@tenant_admin_required
@require_POST
def opportunity_delete(request, pk):
    obj = get_object_or_404(Opportunity, pk=pk, tenant=request.tenant)
    label = obj.number
    log_action(request, "delete", instance=obj)
    obj.delete()
    messages.success(request, f"Opportunity {label} deleted.")
    return redirect("opportunities:opportunity_list")


# ============================================================ opportunity activities
@login_required
def opportunityactivity_list(request):
    qs = OpportunityActivity.objects.filter(tenant=request.tenant).select_related("opportunity")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(subject__icontains=q) | Q(performed_by__icontains=q) | Q(notes__icontains=q))
    activity_type = request.GET.get("activity_type", "")
    if activity_type:
        qs = qs.filter(activity_type=activity_type)
    outcome = request.GET.get("outcome", "")
    if outcome:
        qs = qs.filter(outcome=outcome)
    opportunity = request.GET.get("opportunity", "")
    if opportunity:
        qs = qs.filter(opportunity_id=opportunity)
    paginator, page_obj = _page(request, qs)
    return render(request, "opportunities/opportunityactivity_list.html", {
        "page_title": "Opportunity Tracking & Updates", "page_obj": page_obj,
        "activities": page_obj.object_list,
        "type_choices": OpportunityActivity.TYPE_CHOICES,
        "outcome_choices": OpportunityActivity.OUTCOME_CHOICES,
        "opportunities": Opportunity.objects.filter(tenant=request.tenant).only("id", "number", "name"),
        "total": paginator.count,
    })


@tenant_admin_required
def opportunityactivity_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = OpportunityActivityForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Activity logged.")
        return redirect("opportunities:opportunityactivity_list")
    return render(request, "opportunities/opportunityactivity_form.html",
                  {"form": form, "page_title": "Log Activity", "mode": "create"})


@login_required
def opportunityactivity_detail(request, pk):
    obj = get_object_or_404(
        OpportunityActivity.objects.select_related("opportunity"), pk=pk, tenant=request.tenant)
    return render(request, "opportunities/opportunityactivity_detail.html",
                  {"obj": obj, "page_title": obj.subject})


@tenant_admin_required
def opportunityactivity_edit(request, pk):
    obj = get_object_or_404(OpportunityActivity, pk=pk, tenant=request.tenant)
    form = OpportunityActivityForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Activity updated.")
        return redirect("opportunities:opportunityactivity_detail", pk=obj.pk)
    return render(request, "opportunities/opportunityactivity_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.subject}", "mode": "edit"})


@tenant_admin_required
@require_POST
def opportunityactivity_delete(request, pk):
    obj = get_object_or_404(OpportunityActivity, pk=pk, tenant=request.tenant)
    log_action(request, "delete", instance=obj)
    obj.delete()
    messages.success(request, "Activity deleted.")
    return redirect("opportunities:opportunityactivity_list")


# ============================================================ competitors
@login_required
def competitor_list(request):
    qs = Competitor.objects.filter(tenant=request.tenant).select_related("opportunity")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(name__icontains=q) | Q(strengths__icontains=q) | Q(weaknesses__icontains=q))
    threat_level = request.GET.get("threat_level", "")
    if threat_level:
        qs = qs.filter(threat_level=threat_level)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    opportunity = request.GET.get("opportunity", "")
    if opportunity:
        qs = qs.filter(opportunity_id=opportunity)
    paginator, page_obj = _page(request, qs)
    return render(request, "opportunities/competitor_list.html", {
        "page_title": "Competitive Intelligence", "page_obj": page_obj,
        "competitors": page_obj.object_list,
        "threat_choices": Competitor.THREAT_CHOICES,
        "status_choices": Competitor.STATUS_CHOICES,
        "opportunities": Opportunity.objects.filter(tenant=request.tenant).only("id", "number", "name"),
        "total": paginator.count,
    })


@tenant_admin_required
def competitor_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = CompetitorForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Competitor added.")
        return redirect("opportunities:competitor_list")
    return render(request, "opportunities/competitor_form.html",
                  {"form": form, "page_title": "Add Competitor", "mode": "create"})


@login_required
def competitor_detail(request, pk):
    obj = get_object_or_404(
        Competitor.objects.select_related("opportunity"), pk=pk, tenant=request.tenant)
    return render(request, "opportunities/competitor_detail.html",
                  {"obj": obj, "page_title": obj.name})


@tenant_admin_required
def competitor_edit(request, pk):
    obj = get_object_or_404(Competitor, pk=pk, tenant=request.tenant)
    form = CompetitorForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Competitor updated.")
        return redirect("opportunities:competitor_detail", pk=obj.pk)
    return render(request, "opportunities/competitor_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.name}", "mode": "edit"})


@tenant_admin_required
@require_POST
def competitor_delete(request, pk):
    obj = get_object_or_404(Competitor, pk=pk, tenant=request.tenant)
    label = obj.name
    log_action(request, "delete", instance=obj)
    obj.delete()
    messages.success(request, f"Competitor “{label}” deleted.")
    return redirect("opportunities:competitor_list")


# ============================================================ deal collaborators
@login_required
def dealcollaborator_list(request):
    qs = DealCollaborator.objects.filter(tenant=request.tenant).select_related("opportunity")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(member_name__icontains=q) | Q(email__icontains=q) | Q(contribution__icontains=q))
    team_role = request.GET.get("team_role", "")
    if team_role:
        qs = qs.filter(team_role=team_role)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    opportunity = request.GET.get("opportunity", "")
    if opportunity:
        qs = qs.filter(opportunity_id=opportunity)
    paginator, page_obj = _page(request, qs)
    return render(request, "opportunities/dealcollaborator_list.html", {
        "page_title": "Deal Collaboration & Team Selling", "page_obj": page_obj,
        "collaborators": page_obj.object_list,
        "role_choices": DealCollaborator.ROLE_CHOICES,
        "status_choices": DealCollaborator.STATUS_CHOICES,
        "opportunities": Opportunity.objects.filter(tenant=request.tenant).only("id", "number", "name"),
        "total": paginator.count,
    })


@tenant_admin_required
def dealcollaborator_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = DealCollaboratorForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Collaborator added to the deal.")
        return redirect("opportunities:dealcollaborator_list")
    return render(request, "opportunities/dealcollaborator_form.html",
                  {"form": form, "page_title": "Add Collaborator", "mode": "create"})


@login_required
def dealcollaborator_detail(request, pk):
    obj = get_object_or_404(
        DealCollaborator.objects.select_related("opportunity"), pk=pk, tenant=request.tenant)
    return render(request, "opportunities/dealcollaborator_detail.html",
                  {"obj": obj, "page_title": obj.member_name})


@tenant_admin_required
def dealcollaborator_edit(request, pk):
    obj = get_object_or_404(DealCollaborator, pk=pk, tenant=request.tenant)
    form = DealCollaboratorForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Collaborator updated.")
        return redirect("opportunities:dealcollaborator_detail", pk=obj.pk)
    return render(request, "opportunities/dealcollaborator_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.member_name}", "mode": "edit"})


@tenant_admin_required
@require_POST
def dealcollaborator_delete(request, pk):
    obj = get_object_or_404(DealCollaborator, pk=pk, tenant=request.tenant)
    label = obj.member_name
    log_action(request, "delete", instance=obj)
    obj.delete()
    messages.success(request, f"Collaborator “{label}” removed.")
    return redirect("opportunities:dealcollaborator_list")
