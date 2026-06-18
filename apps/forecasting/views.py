from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.decorators import tenant_admin_required
from apps.core.utils import log_action

from .forms import (
    ForecastAccuracyForm, ForecastAdjustmentForm, ForecastCategoryForm,
    ForecastForm, QuotaForm,
)
from .models import (
    Forecast, ForecastAccuracy, ForecastAdjustment, ForecastCategory, Quota,
)


def _no_tenant_redirect(request):
    messages.info(request, "Switch to a tenant workspace to manage this — the superuser has no tenant.")
    return redirect("dashboard:index")


def _page(request, qs, per_page=12):
    paginator = Paginator(qs, per_page)
    return paginator, paginator.get_page(request.GET.get("page"))


# ============================================================ forecast categories
@login_required
def forecastcategory_list(request):
    qs = ForecastCategory.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
    commitment = request.GET.get("commitment", "")
    if commitment:
        qs = qs.filter(commitment=commitment)
    active = request.GET.get("active", "")
    if active == "active":
        qs = qs.filter(is_active=True)
    elif active == "inactive":
        qs = qs.filter(is_active=False)
    paginator, page_obj = _page(request, qs)
    return render(request, "forecasting/forecastcategory_list.html", {
        "page_title": "Forecast Categories & Commitments", "page_obj": page_obj,
        "categories": page_obj.object_list, "commit_choices": ForecastCategory.COMMIT_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def forecastcategory_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = ForecastCategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Forecast category added.")
        return redirect("forecasting:forecastcategory_list")
    return render(request, "forecasting/forecastcategory_form.html",
                  {"form": form, "page_title": "Add Forecast Category", "mode": "create"})


@login_required
def forecastcategory_detail(request, pk):
    obj = get_object_or_404(ForecastCategory, pk=pk, tenant=request.tenant)
    return render(request, "forecasting/forecastcategory_detail.html", {"obj": obj, "page_title": obj.name})


@tenant_admin_required
def forecastcategory_edit(request, pk):
    obj = get_object_or_404(ForecastCategory, pk=pk, tenant=request.tenant)
    form = ForecastCategoryForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Forecast category updated.")
        return redirect("forecasting:forecastcategory_detail", pk=obj.pk)
    return render(request, "forecasting/forecastcategory_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.name}", "mode": "edit"})


@tenant_admin_required
def forecastcategory_delete(request, pk):
    obj = get_object_or_404(ForecastCategory, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Forecast category “{label}” deleted.")
    return redirect("forecasting:forecastcategory_list")


# ============================================================ forecasts
@login_required
def forecast_list(request):
    qs = Forecast.objects.filter(tenant=request.tenant).select_related("category")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(name__icontains=q) | Q(owner_name__icontains=q))
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    period_type = request.GET.get("period_type", "")
    if period_type:
        qs = qs.filter(period_type=period_type)
    category = request.GET.get("category", "")
    if category:
        qs = qs.filter(category_id=category)
    paginator, page_obj = _page(request, qs)
    return render(request, "forecasting/forecast_list.html", {
        "page_title": "AI-Powered Predictive Forecasting", "page_obj": page_obj,
        "forecasts": page_obj.object_list, "status_choices": Forecast.STATUS_CHOICES,
        "period_choices": Forecast.PERIOD_CHOICES,
        "categories": ForecastCategory.objects.filter(tenant=request.tenant),
        "total": paginator.count,
    })


@tenant_admin_required
def forecast_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = ForecastForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, f"Forecast {obj.number} created.")
        return redirect("forecasting:forecast_list")
    return render(request, "forecasting/forecast_form.html",
                  {"form": form, "page_title": "Add Forecast", "mode": "create"})


@login_required
def forecast_detail(request, pk):
    obj = get_object_or_404(Forecast.objects.select_related("category"), pk=pk, tenant=request.tenant)
    adjustments = obj.adjustments.filter(tenant=request.tenant)[:20]
    return render(request, "forecasting/forecast_detail.html",
                  {"obj": obj, "adjustments": adjustments, "page_title": obj.number or obj.name})


@tenant_admin_required
def forecast_edit(request, pk):
    obj = get_object_or_404(Forecast, pk=pk, tenant=request.tenant)
    form = ForecastForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Forecast updated.")
        return redirect("forecasting:forecast_detail", pk=obj.pk)
    return render(request, "forecasting/forecast_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.number or obj.name}", "mode": "edit"})


@tenant_admin_required
def forecast_delete(request, pk):
    obj = get_object_or_404(Forecast, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.number or obj.name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Forecast {label} deleted.")
    return redirect("forecasting:forecast_list")


# ============================================================ quotas
@login_required
def quota_list(request):
    qs = Quota.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(owner_name__icontains=q) | Q(period_label__icontains=q))
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    period_type = request.GET.get("period_type", "")
    if period_type:
        qs = qs.filter(period_type=period_type)
    paginator, page_obj = _page(request, qs)
    return render(request, "forecasting/quota_list.html", {
        "page_title": "Quota Management & Attainment", "page_obj": page_obj,
        "quotas": page_obj.object_list, "status_choices": Quota.STATUS_CHOICES,
        "period_choices": Quota.PERIOD_CHOICES, "total": paginator.count,
    })


@tenant_admin_required
def quota_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = QuotaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Quota created.")
        return redirect("forecasting:quota_list")
    return render(request, "forecasting/quota_form.html",
                  {"form": form, "page_title": "Add Quota", "mode": "create"})


@login_required
def quota_detail(request, pk):
    obj = get_object_or_404(Quota, pk=pk, tenant=request.tenant)
    return render(request, "forecasting/quota_detail.html", {"obj": obj, "page_title": str(obj)})


@tenant_admin_required
def quota_edit(request, pk):
    obj = get_object_or_404(Quota, pk=pk, tenant=request.tenant)
    form = QuotaForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Quota updated.")
        return redirect("forecasting:quota_detail", pk=obj.pk)
    return render(request, "forecasting/quota_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj}", "mode": "edit"})


@tenant_admin_required
def quota_delete(request, pk):
    obj = get_object_or_404(Quota, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, "Quota deleted.")
    return redirect("forecasting:quota_list")


# ============================================================ forecast adjustments
@login_required
def forecastadjustment_list(request):
    qs = ForecastAdjustment.objects.filter(tenant=request.tenant).select_related("forecast")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(adjusted_by__icontains=q) | Q(reason__icontains=q)
                       | Q(forecast__number__icontains=q))
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    adjustment_type = request.GET.get("adjustment_type", "")
    if adjustment_type:
        qs = qs.filter(adjustment_type=adjustment_type)
    paginator, page_obj = _page(request, qs)
    return render(request, "forecasting/forecastadjustment_list.html", {
        "page_title": "Forecast Rollups & Adjustments", "page_obj": page_obj,
        "adjustments": page_obj.object_list, "status_choices": ForecastAdjustment.STATUS_CHOICES,
        "type_choices": ForecastAdjustment.TYPE_CHOICES, "total": paginator.count,
    })


@tenant_admin_required
def forecastadjustment_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = ForecastAdjustmentForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Forecast adjustment added.")
        return redirect("forecasting:forecastadjustment_list")
    return render(request, "forecasting/forecastadjustment_form.html",
                  {"form": form, "page_title": "Add Forecast Adjustment", "mode": "create"})


@login_required
def forecastadjustment_detail(request, pk):
    obj = get_object_or_404(
        ForecastAdjustment.objects.select_related("forecast"), pk=pk, tenant=request.tenant)
    return render(request, "forecasting/forecastadjustment_detail.html",
                  {"obj": obj, "page_title": str(obj)})


@tenant_admin_required
def forecastadjustment_edit(request, pk):
    obj = get_object_or_404(ForecastAdjustment, pk=pk, tenant=request.tenant)
    form = ForecastAdjustmentForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Forecast adjustment updated.")
        return redirect("forecasting:forecastadjustment_detail", pk=obj.pk)
    return render(request, "forecasting/forecastadjustment_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj}", "mode": "edit"})


@tenant_admin_required
def forecastadjustment_delete(request, pk):
    obj = get_object_or_404(ForecastAdjustment, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, "Forecast adjustment deleted.")
    return redirect("forecasting:forecastadjustment_list")


# ============================================================ forecast accuracy
@login_required
def forecastaccuracy_list(request):
    qs = ForecastAccuracy.objects.filter(tenant=request.tenant).select_related("forecast")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(period_label__icontains=q) | Q(notes__icontains=q)
                       | Q(forecast__number__icontains=q))
    grade = request.GET.get("grade", "")
    if grade:
        qs = qs.filter(grade=grade)
    paginator, page_obj = _page(request, qs)
    return render(request, "forecasting/forecastaccuracy_list.html", {
        "page_title": "Forecast Accuracy & Variance Analysis", "page_obj": page_obj,
        "records": page_obj.object_list, "grade_choices": ForecastAccuracy.GRADE_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def forecastaccuracy_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = ForecastAccuracyForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Accuracy record added.")
        return redirect("forecasting:forecastaccuracy_list")
    return render(request, "forecasting/forecastaccuracy_form.html",
                  {"form": form, "page_title": "Add Accuracy Record", "mode": "create"})


@login_required
def forecastaccuracy_detail(request, pk):
    obj = get_object_or_404(
        ForecastAccuracy.objects.select_related("forecast"), pk=pk, tenant=request.tenant)
    return render(request, "forecasting/forecastaccuracy_detail.html",
                  {"obj": obj, "page_title": obj.period_label or "Accuracy record"})


@tenant_admin_required
def forecastaccuracy_edit(request, pk):
    obj = get_object_or_404(ForecastAccuracy, pk=pk, tenant=request.tenant)
    form = ForecastAccuracyForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Accuracy record updated.")
        return redirect("forecasting:forecastaccuracy_detail", pk=obj.pk)
    return render(request, "forecasting/forecastaccuracy_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.period_label or 'record'}", "mode": "edit"})


@tenant_admin_required
def forecastaccuracy_delete(request, pk):
    obj = get_object_or_404(ForecastAccuracy, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, "Accuracy record deleted.")
    return redirect("forecasting:forecastaccuracy_list")
