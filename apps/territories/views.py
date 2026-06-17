from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.decorators import tenant_admin_required
from apps.core.utils import log_action

from .forms import (
    CoverageModelForm, QuotaPlanForm, TerritoryAssignmentForm,
    TerritoryForm, TerritoryPerformanceForm,
)
from .models import (
    CoverageModel, QuotaPlan, Territory, TerritoryAssignment, TerritoryPerformance,
)


def _no_tenant_redirect(request):
    messages.info(request, "Switch to a tenant workspace to manage this — the superuser has no tenant.")
    return redirect("dashboard:index")


def _page(request, qs, per_page=12):
    paginator = Paginator(qs, per_page)
    return paginator, paginator.get_page(request.GET.get("page"))


# ============================================================ territories
@login_required
def territory_list(request):
    qs = Territory.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(code__icontains=q)
                       | Q(region__icontains=q) | Q(country__icontains=q)
                       | Q(description__icontains=q))
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    territory_type = request.GET.get("territory_type", "")
    if territory_type:
        qs = qs.filter(territory_type=territory_type)
    paginator, page_obj = _page(request, qs)
    return render(request, "territories/territory_list.html", {
        "page_title": "Territory Design & Mapping", "page_obj": page_obj,
        "territories": page_obj.object_list,
        "status_choices": Territory.STATUS_CHOICES, "type_choices": Territory.TYPE_CHOICES,
        "total": paginator.count,
    })


@login_required
def territory_detail(request, pk):
    obj = get_object_or_404(Territory, pk=pk, tenant=request.tenant)
    assignments = obj.assignments.all()[:20]
    quota_plans = obj.quota_plans.all()[:20]
    snapshots = obj.performance_snapshots.all()[:20]
    return render(request, "territories/territory_detail.html", {
        "obj": obj, "page_title": obj.name,
        "assignments": assignments, "quota_plans": quota_plans, "snapshots": snapshots,
    })


@tenant_admin_required
def territory_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = TerritoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Territory created.")
        return redirect("territories:territory_detail", pk=obj.pk)
    return render(request, "territories/territory_form.html",
                  {"form": form, "page_title": "Add Territory", "mode": "create"})


@tenant_admin_required
def territory_edit(request, pk):
    obj = get_object_or_404(Territory, pk=pk, tenant=request.tenant)
    form = TerritoryForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Territory updated.")
        return redirect("territories:territory_detail", pk=obj.pk)
    return render(request, "territories/territory_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.name}", "mode": "edit"})


@tenant_admin_required
def territory_delete(request, pk):
    obj = get_object_or_404(Territory, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Territory “{label}” deleted.")
    return redirect("territories:territory_list")


# ============================================================ territory assignments
@login_required
def territoryassignment_list(request):
    qs = TerritoryAssignment.objects.filter(tenant=request.tenant).select_related("territory")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(rep_name__icontains=q) | Q(rep_email__icontains=q)
                       | Q(territory__name__icontains=q) | Q(notes__icontains=q))
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    role = request.GET.get("assignment_role", "")
    if role:
        qs = qs.filter(assignment_role=role)
    territory = request.GET.get("territory", "")
    if territory:
        qs = qs.filter(territory_id=territory)
    paginator, page_obj = _page(request, qs)
    return render(request, "territories/territoryassignment_list.html", {
        "page_title": "Territory Assignment & Rebalancing", "page_obj": page_obj,
        "assignments": page_obj.object_list,
        "status_choices": TerritoryAssignment.STATUS_CHOICES,
        "role_choices": TerritoryAssignment.ROLE_CHOICES,
        "territories": Territory.objects.filter(tenant=request.tenant),
        "total": paginator.count,
    })


@login_required
def territoryassignment_detail(request, pk):
    obj = get_object_or_404(
        TerritoryAssignment.objects.select_related("territory"), pk=pk, tenant=request.tenant)
    return render(request, "territories/territoryassignment_detail.html",
                  {"obj": obj, "page_title": str(obj)})


@tenant_admin_required
def territoryassignment_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = TerritoryAssignmentForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Assignment created.")
        return redirect("territories:territoryassignment_detail", pk=obj.pk)
    return render(request, "territories/territoryassignment_form.html",
                  {"form": form, "page_title": "Add Assignment", "mode": "create"})


@tenant_admin_required
def territoryassignment_edit(request, pk):
    obj = get_object_or_404(TerritoryAssignment, pk=pk, tenant=request.tenant)
    form = TerritoryAssignmentForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Assignment updated.")
        return redirect("territories:territoryassignment_detail", pk=obj.pk)
    return render(request, "territories/territoryassignment_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj}", "mode": "edit"})


@tenant_admin_required
def territoryassignment_delete(request, pk):
    obj = get_object_or_404(TerritoryAssignment, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, "Assignment deleted.")
    return redirect("territories:territoryassignment_list")


# ============================================================ quota plans
@login_required
def quotaplan_list(request):
    qs = QuotaPlan.objects.filter(tenant=request.tenant).select_related("territory")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(name__icontains=q)
                       | Q(territory__name__icontains=q) | Q(notes__icontains=q))
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    period = request.GET.get("period_type", "")
    if period:
        qs = qs.filter(period_type=period)
    territory = request.GET.get("territory", "")
    if territory:
        qs = qs.filter(territory_id=territory)
    paginator, page_obj = _page(request, qs)
    return render(request, "territories/quotaplan_list.html", {
        "page_title": "Quota Planning & Allocation", "page_obj": page_obj,
        "quota_plans": page_obj.object_list,
        "status_choices": QuotaPlan.STATUS_CHOICES,
        "period_choices": QuotaPlan.PERIOD_CHOICES,
        "territories": Territory.objects.filter(tenant=request.tenant),
        "total": paginator.count,
    })


@login_required
def quotaplan_detail(request, pk):
    obj = get_object_or_404(
        QuotaPlan.objects.select_related("territory"), pk=pk, tenant=request.tenant)
    return render(request, "territories/quotaplan_detail.html",
                  {"obj": obj, "page_title": obj.number or obj.name})


@tenant_admin_required
def quotaplan_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = QuotaPlanForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, f"Quota plan {obj.number} created.")
        return redirect("territories:quotaplan_detail", pk=obj.pk)
    return render(request, "territories/quotaplan_form.html",
                  {"form": form, "page_title": "Add Quota Plan", "mode": "create"})


@tenant_admin_required
def quotaplan_edit(request, pk):
    obj = get_object_or_404(QuotaPlan, pk=pk, tenant=request.tenant)
    form = QuotaPlanForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Quota plan updated.")
        return redirect("territories:quotaplan_detail", pk=obj.pk)
    return render(request, "territories/quotaplan_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.number}", "mode": "edit"})


@tenant_admin_required
def quotaplan_delete(request, pk):
    obj = get_object_or_404(QuotaPlan, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.number
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Quota plan {label} deleted.")
    return redirect("territories:quotaplan_list")


# ============================================================ coverage models
@login_required
def coveragemodel_list(request):
    qs = CoverageModel.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    model_type = request.GET.get("model_type", "")
    if model_type:
        qs = qs.filter(model_type=model_type)
    paginator, page_obj = _page(request, qs)
    return render(request, "territories/coveragemodel_list.html", {
        "page_title": "Coverage Model Optimization", "page_obj": page_obj,
        "models": page_obj.object_list,
        "status_choices": CoverageModel.STATUS_CHOICES,
        "type_choices": CoverageModel.MODEL_CHOICES,
        "total": paginator.count,
    })


@login_required
def coveragemodel_detail(request, pk):
    obj = get_object_or_404(CoverageModel, pk=pk, tenant=request.tenant)
    return render(request, "territories/coveragemodel_detail.html",
                  {"obj": obj, "page_title": obj.name})


@tenant_admin_required
def coveragemodel_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = CoverageModelForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Coverage model created.")
        return redirect("territories:coveragemodel_detail", pk=obj.pk)
    return render(request, "territories/coveragemodel_form.html",
                  {"form": form, "page_title": "Add Coverage Model", "mode": "create"})


@tenant_admin_required
def coveragemodel_edit(request, pk):
    obj = get_object_or_404(CoverageModel, pk=pk, tenant=request.tenant)
    form = CoverageModelForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Coverage model updated.")
        return redirect("territories:coveragemodel_detail", pk=obj.pk)
    return render(request, "territories/coveragemodel_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.name}", "mode": "edit"})


@tenant_admin_required
def coveragemodel_delete(request, pk):
    obj = get_object_or_404(CoverageModel, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Coverage model “{label}” deleted.")
    return redirect("territories:coveragemodel_list")


# ============================================================ territory performance
@login_required
def territoryperformance_list(request):
    qs = TerritoryPerformance.objects.filter(tenant=request.tenant).select_related("territory")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(period_label__icontains=q) | Q(territory__name__icontains=q))
    rating = request.GET.get("rating", "")
    if rating:
        qs = qs.filter(rating=rating)
    period = request.GET.get("period_type", "")
    if period:
        qs = qs.filter(period_type=period)
    territory = request.GET.get("territory", "")
    if territory:
        qs = qs.filter(territory_id=territory)
    paginator, page_obj = _page(request, qs)
    return render(request, "territories/territoryperformance_list.html", {
        "page_title": "Territory Performance Analytics", "page_obj": page_obj,
        "snapshots": page_obj.object_list,
        "rating_choices": TerritoryPerformance.RATING_CHOICES,
        "period_choices": TerritoryPerformance.PERIOD_CHOICES,
        "territories": Territory.objects.filter(tenant=request.tenant),
        "total": paginator.count,
    })


@login_required
def territoryperformance_detail(request, pk):
    obj = get_object_or_404(
        TerritoryPerformance.objects.select_related("territory"), pk=pk, tenant=request.tenant)
    return render(request, "territories/territoryperformance_detail.html",
                  {"obj": obj, "page_title": str(obj)})


@tenant_admin_required
def territoryperformance_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = TerritoryPerformanceForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Performance snapshot recorded.")
        return redirect("territories:territoryperformance_detail", pk=obj.pk)
    return render(request, "territories/territoryperformance_form.html",
                  {"form": form, "page_title": "Add Performance Snapshot", "mode": "create"})


@tenant_admin_required
def territoryperformance_edit(request, pk):
    obj = get_object_or_404(TerritoryPerformance, pk=pk, tenant=request.tenant)
    form = TerritoryPerformanceForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Performance snapshot updated.")
        return redirect("territories:territoryperformance_detail", pk=obj.pk)
    return render(request, "territories/territoryperformance_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj}", "mode": "edit"})


@tenant_admin_required
def territoryperformance_delete(request, pk):
    obj = get_object_or_404(TerritoryPerformance, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, "Performance snapshot deleted.")
    return redirect("territories:territoryperformance_list")
