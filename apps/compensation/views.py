from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.decorators import tenant_admin_required
from apps.core.utils import log_action

from .forms import (
    ClawbackForm, CommissionPlanForm, EarningForm, GlobalPlanVariationForm, PayoutForm,
)
from .models import (
    Clawback, CommissionPlan, Earning, GlobalPlanVariation, Payout,
)


def _no_tenant_redirect(request):
    messages.info(request, "Switch to a tenant workspace to manage this — the superuser has no tenant.")
    return redirect("dashboard:index")


def _page(request, qs, per_page=12):
    paginator = Paginator(qs, per_page)
    return paginator, paginator.get_page(request.GET.get("page"))


# ============================================================ commission plans
@login_required
def commissionplan_list(request):
    qs = CommissionPlan.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(code__icontains=q) | Q(description__icontains=q))
    plan_type = request.GET.get("plan_type", "")
    if plan_type:
        qs = qs.filter(plan_type=plan_type)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "compensation/commissionplan_list.html", {
        "page_title": "Commission Plan Design", "page_obj": page_obj, "plans": page_obj.object_list,
        "type_choices": CommissionPlan.TYPE_CHOICES, "status_choices": CommissionPlan.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def commissionplan_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = CommissionPlanForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Commission plan created.")
        return redirect("compensation:commissionplan_list")
    return render(request, "compensation/commissionplan_form.html",
                  {"form": form, "page_title": "Add Commission Plan", "mode": "create"})


@login_required
def commissionplan_detail(request, pk):
    obj = get_object_or_404(CommissionPlan, pk=pk, tenant=request.tenant)
    earnings = obj.earnings.filter(tenant=request.tenant)[:20]
    variations = obj.variations.filter(tenant=request.tenant)[:20]
    return render(request, "compensation/commissionplan_detail.html",
                  {"obj": obj, "earnings": earnings, "variations": variations, "page_title": obj.name})


@tenant_admin_required
def commissionplan_edit(request, pk):
    obj = get_object_or_404(CommissionPlan, pk=pk, tenant=request.tenant)
    form = CommissionPlanForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Commission plan updated.")
        return redirect("compensation:commissionplan_detail", pk=obj.pk)
    return render(request, "compensation/commissionplan_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.name}", "mode": "edit"})


@tenant_admin_required
def commissionplan_delete(request, pk):
    obj = get_object_or_404(CommissionPlan, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Commission plan “{label}” deleted.")
    return redirect("compensation:commissionplan_list")


# ============================================================ earnings
@login_required
def earning_list(request):
    qs = Earning.objects.filter(tenant=request.tenant).select_related("plan")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(rep_name__icontains=q) | Q(deal_reference__icontains=q))
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    plan = request.GET.get("plan", "")
    if plan:
        qs = qs.filter(plan_id=plan)
    paginator, page_obj = _page(request, qs)
    return render(request, "compensation/earning_list.html", {
        "page_title": "Real-Time Earnings Tracking", "page_obj": page_obj, "earnings": page_obj.object_list,
        "status_choices": Earning.STATUS_CHOICES,
        "plans": CommissionPlan.objects.filter(tenant=request.tenant),
        "total": paginator.count,
    })


@tenant_admin_required
def earning_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = EarningForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, f"Earning {obj.number} recorded.")
        return redirect("compensation:earning_list")
    return render(request, "compensation/earning_form.html",
                  {"form": form, "page_title": "Add Earning", "mode": "create"})


@login_required
def earning_detail(request, pk):
    obj = get_object_or_404(Earning.objects.select_related("plan"), pk=pk, tenant=request.tenant)
    clawbacks = obj.clawbacks.all()[:20]
    return render(request, "compensation/earning_detail.html",
                  {"obj": obj, "clawbacks": clawbacks, "page_title": obj.number})


@tenant_admin_required
def earning_edit(request, pk):
    obj = get_object_or_404(Earning, pk=pk, tenant=request.tenant)
    form = EarningForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Earning updated.")
        return redirect("compensation:earning_detail", pk=obj.pk)
    return render(request, "compensation/earning_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.number}", "mode": "edit"})


@tenant_admin_required
def earning_delete(request, pk):
    obj = get_object_or_404(Earning, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.number
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Earning {label} deleted.")
    return redirect("compensation:earning_list")


# ============================================================ clawbacks
@login_required
def clawback_list(request):
    qs = Clawback.objects.filter(tenant=request.tenant).select_related("earning")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(rep_name__icontains=q) | Q(notes__icontains=q))
    reason = request.GET.get("reason", "")
    if reason:
        qs = qs.filter(reason=reason)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "compensation/clawback_list.html", {
        "page_title": "Clawbacks & Adjustments", "page_obj": page_obj, "clawbacks": page_obj.object_list,
        "reason_choices": Clawback.REASON_CHOICES, "status_choices": Clawback.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def clawback_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = ClawbackForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Clawback recorded.")
        return redirect("compensation:clawback_list")
    return render(request, "compensation/clawback_form.html",
                  {"form": form, "page_title": "Add Clawback", "mode": "create"})


@login_required
def clawback_detail(request, pk):
    obj = get_object_or_404(Clawback.objects.select_related("earning"), pk=pk, tenant=request.tenant)
    return render(request, "compensation/clawback_detail.html", {"obj": obj, "page_title": str(obj)})


@tenant_admin_required
def clawback_edit(request, pk):
    obj = get_object_or_404(Clawback, pk=pk, tenant=request.tenant)
    form = ClawbackForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Clawback updated.")
        return redirect("compensation:clawback_detail", pk=obj.pk)
    return render(request, "compensation/clawback_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit clawback", "mode": "edit"})


@tenant_admin_required
def clawback_delete(request, pk):
    obj = get_object_or_404(Clawback, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, "Clawback deleted.")
    return redirect("compensation:clawback_list")


# ============================================================ global plan variations
@login_required
def globalplanvariation_list(request):
    qs = GlobalPlanVariation.objects.filter(tenant=request.tenant).select_related("plan")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(region__icontains=q) | Q(notes__icontains=q))
    currency = request.GET.get("currency", "")
    if currency:
        qs = qs.filter(currency=currency)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    plan = request.GET.get("plan", "")
    if plan:
        qs = qs.filter(plan_id=plan)
    paginator, page_obj = _page(request, qs)
    return render(request, "compensation/globalplanvariation_list.html", {
        "page_title": "Multi-Currency & Global Plans", "page_obj": page_obj,
        "variations": page_obj.object_list,
        "currency_choices": GlobalPlanVariation.CURRENCY_CHOICES,
        "status_choices": GlobalPlanVariation.STATUS_CHOICES,
        "plans": CommissionPlan.objects.filter(tenant=request.tenant),
        "total": paginator.count,
    })


@tenant_admin_required
def globalplanvariation_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = GlobalPlanVariationForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Global plan variation created.")
        return redirect("compensation:globalplanvariation_list")
    return render(request, "compensation/globalplanvariation_form.html",
                  {"form": form, "page_title": "Add Global Plan Variation", "mode": "create"})


@login_required
def globalplanvariation_detail(request, pk):
    obj = get_object_or_404(
        GlobalPlanVariation.objects.select_related("plan"), pk=pk, tenant=request.tenant)
    return render(request, "compensation/globalplanvariation_detail.html",
                  {"obj": obj, "page_title": str(obj)})


@tenant_admin_required
def globalplanvariation_edit(request, pk):
    obj = get_object_or_404(GlobalPlanVariation, pk=pk, tenant=request.tenant)
    form = GlobalPlanVariationForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Global plan variation updated.")
        return redirect("compensation:globalplanvariation_detail", pk=obj.pk)
    return render(request, "compensation/globalplanvariation_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj}", "mode": "edit"})


@tenant_admin_required
def globalplanvariation_delete(request, pk):
    obj = get_object_or_404(GlobalPlanVariation, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = str(obj)
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Variation “{label}” deleted.")
    return redirect("compensation:globalplanvariation_list")


# ============================================================ payouts
@login_required
def payout_list(request):
    qs = Payout.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(rep_name__icontains=q)
                       | Q(reference__icontains=q) | Q(period_label__icontains=q))
    method = request.GET.get("method", "")
    if method:
        qs = qs.filter(method=method)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "compensation/payout_list.html", {
        "page_title": "Payout Processing & Integration", "page_obj": page_obj,
        "payouts": page_obj.object_list,
        "method_choices": Payout.METHOD_CHOICES, "status_choices": Payout.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def payout_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = PayoutForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, f"Payout {obj.number} scheduled.")
        return redirect("compensation:payout_list")
    return render(request, "compensation/payout_form.html",
                  {"form": form, "page_title": "Add Payout", "mode": "create"})


@login_required
def payout_detail(request, pk):
    obj = get_object_or_404(Payout, pk=pk, tenant=request.tenant)
    return render(request, "compensation/payout_detail.html", {"obj": obj, "page_title": obj.number})


@tenant_admin_required
def payout_edit(request, pk):
    obj = get_object_or_404(Payout, pk=pk, tenant=request.tenant)
    form = PayoutForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Payout updated.")
        return redirect("compensation:payout_detail", pk=obj.pk)
    return render(request, "compensation/payout_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.number}", "mode": "edit"})


@tenant_admin_required
def payout_delete(request, pk):
    obj = get_object_or_404(Payout, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.number
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Payout {label} deleted.")
    return redirect("compensation:payout_list")
