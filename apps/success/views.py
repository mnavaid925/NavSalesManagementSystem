from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.decorators import tenant_admin_required
from apps.core.utils import log_action

from .forms import (
    AdvocacyForm, HealthScoreForm, OnboardingPlanForm, QBRForm, RenewalForm,
)
from .models import (
    Advocacy, HealthScore, OnboardingPlan, QBR, Renewal,
)


def _no_tenant_redirect(request):
    messages.info(request, "Switch to a tenant workspace to manage this — the superuser has no tenant.")
    return redirect("dashboard:index")


def _page(request, qs, per_page=12):
    paginator = Paginator(qs, per_page)
    return paginator, paginator.get_page(request.GET.get("page"))


# ============================================================ health scores
@login_required
def healthscore_list(request):
    qs = HealthScore.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(account_name__icontains=q) | Q(owner__icontains=q) | Q(notes__icontains=q))
    risk_level = request.GET.get("risk_level", "")
    if risk_level:
        qs = qs.filter(risk_level=risk_level)
    trend = request.GET.get("trend", "")
    if trend:
        qs = qs.filter(trend=trend)
    paginator, page_obj = _page(request, qs)
    return render(request, "success/healthscore_list.html", {
        "page_title": "Health Scoring & Risk Alerts", "page_obj": page_obj,
        "healthscores": page_obj.object_list,
        "risk_level_choices": HealthScore.RISK_LEVEL_CHOICES,
        "trend_choices": HealthScore.TREND_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def healthscore_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = HealthScoreForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Health score created.")
        return redirect("success:healthscore_list")
    return render(request, "success/healthscore_form.html",
                  {"form": form, "page_title": "Add Health Score", "mode": "create"})


@login_required
def healthscore_detail(request, pk):
    obj = get_object_or_404(HealthScore, pk=pk, tenant=request.tenant)
    return render(request, "success/healthscore_detail.html", {"obj": obj, "page_title": obj.account_name})


@tenant_admin_required
def healthscore_edit(request, pk):
    obj = get_object_or_404(HealthScore, pk=pk, tenant=request.tenant)
    form = HealthScoreForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Health score updated.")
        return redirect("success:healthscore_detail", pk=obj.pk)
    return render(request, "success/healthscore_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.account_name}", "mode": "edit"})


@tenant_admin_required
def healthscore_delete(request, pk):
    obj = get_object_or_404(HealthScore, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.account_name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Health score “{label}” deleted.")
    return redirect("success:healthscore_list")


# ============================================================ renewals
@login_required
def renewal_list(request):
    qs = Renewal.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(account_name__icontains=q) | Q(owner__icontains=q))
    renewal_type = request.GET.get("renewal_type", "")
    if renewal_type:
        qs = qs.filter(renewal_type=renewal_type)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "success/renewal_list.html", {
        "page_title": "Renewal & Expansion Pipeline", "page_obj": page_obj,
        "renewals": page_obj.object_list,
        "type_choices": Renewal.RENEWAL_TYPE_CHOICES, "status_choices": Renewal.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def renewal_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = RenewalForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, f"Renewal {obj.number} created.")
        return redirect("success:renewal_list")
    return render(request, "success/renewal_form.html",
                  {"form": form, "page_title": "Add Renewal", "mode": "create"})


@login_required
def renewal_detail(request, pk):
    obj = get_object_or_404(Renewal, pk=pk, tenant=request.tenant)
    return render(request, "success/renewal_detail.html", {"obj": obj, "page_title": obj.number})


@tenant_admin_required
def renewal_edit(request, pk):
    obj = get_object_or_404(Renewal, pk=pk, tenant=request.tenant)
    form = RenewalForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Renewal updated.")
        return redirect("success:renewal_detail", pk=obj.pk)
    return render(request, "success/renewal_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.number}", "mode": "edit"})


@tenant_admin_required
def renewal_delete(request, pk):
    obj = get_object_or_404(Renewal, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.number
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Renewal {label} deleted.")
    return redirect("success:renewal_list")


# ============================================================ onboarding plans
@login_required
def onboardingplan_list(request):
    qs = OnboardingPlan.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(account_name__icontains=q) | Q(plan_name__icontains=q) | Q(owner__icontains=q))
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "success/onboardingplan_list.html", {
        "page_title": "Onboarding & Implementation", "page_obj": page_obj,
        "onboardingplans": page_obj.object_list,
        "status_choices": OnboardingPlan.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def onboardingplan_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = OnboardingPlanForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Onboarding plan created.")
        return redirect("success:onboardingplan_list")
    return render(request, "success/onboardingplan_form.html",
                  {"form": form, "page_title": "Add Onboarding Plan", "mode": "create"})


@login_required
def onboardingplan_detail(request, pk):
    obj = get_object_or_404(OnboardingPlan, pk=pk, tenant=request.tenant)
    return render(request, "success/onboardingplan_detail.html", {"obj": obj, "page_title": obj.plan_name})


@tenant_admin_required
def onboardingplan_edit(request, pk):
    obj = get_object_or_404(OnboardingPlan, pk=pk, tenant=request.tenant)
    form = OnboardingPlanForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Onboarding plan updated.")
        return redirect("success:onboardingplan_detail", pk=obj.pk)
    return render(request, "success/onboardingplan_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.plan_name}", "mode": "edit"})


@tenant_admin_required
def onboardingplan_delete(request, pk):
    obj = get_object_or_404(OnboardingPlan, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.plan_name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Onboarding plan “{label}” deleted.")
    return redirect("success:onboardingplan_list")


# ============================================================ advocacy
@login_required
def advocacy_list(request):
    qs = Advocacy.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(account_name__icontains=q) | Q(contact_name__icontains=q))
    advocacy_type = request.GET.get("advocacy_type", "")
    if advocacy_type:
        qs = qs.filter(advocacy_type=advocacy_type)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "success/advocacy_list.html", {
        "page_title": "Advocacy & Reference Management", "page_obj": page_obj,
        "advocacies": page_obj.object_list,
        "type_choices": Advocacy.ADVOCACY_TYPE_CHOICES, "status_choices": Advocacy.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def advocacy_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = AdvocacyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Advocate recorded.")
        return redirect("success:advocacy_list")
    return render(request, "success/advocacy_form.html",
                  {"form": form, "page_title": "Add Advocate", "mode": "create"})


@login_required
def advocacy_detail(request, pk):
    obj = get_object_or_404(Advocacy, pk=pk, tenant=request.tenant)
    return render(request, "success/advocacy_detail.html", {"obj": obj, "page_title": str(obj)})


@tenant_admin_required
def advocacy_edit(request, pk):
    obj = get_object_or_404(Advocacy, pk=pk, tenant=request.tenant)
    form = AdvocacyForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Advocate updated.")
        return redirect("success:advocacy_detail", pk=obj.pk)
    return render(request, "success/advocacy_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj}", "mode": "edit"})


@tenant_admin_required
def advocacy_delete(request, pk):
    obj = get_object_or_404(Advocacy, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = str(obj)
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Advocate “{label}” deleted.")
    return redirect("success:advocacy_list")


# ============================================================ QBRs
@login_required
def qbr_list(request):
    qs = QBR.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(account_name__icontains=q) | Q(period_label__icontains=q))
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    sentiment = request.GET.get("sentiment", "")
    if sentiment:
        qs = qs.filter(sentiment=sentiment)
    paginator, page_obj = _page(request, qs)
    return render(request, "success/qbr_list.html", {
        "page_title": "Quarterly Business Reviews", "page_obj": page_obj,
        "qbrs": page_obj.object_list,
        "status_choices": QBR.STATUS_CHOICES, "sentiment_choices": QBR.SENTIMENT_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def qbr_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = QBRForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "QBR created.")
        return redirect("success:qbr_list")
    return render(request, "success/qbr_form.html",
                  {"form": form, "page_title": "Add QBR", "mode": "create"})


@login_required
def qbr_detail(request, pk):
    obj = get_object_or_404(QBR, pk=pk, tenant=request.tenant)
    return render(request, "success/qbr_detail.html", {"obj": obj, "page_title": str(obj)})


@tenant_admin_required
def qbr_edit(request, pk):
    obj = get_object_or_404(QBR, pk=pk, tenant=request.tenant)
    form = QBRForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "QBR updated.")
        return redirect("success:qbr_detail", pk=obj.pk)
    return render(request, "success/qbr_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj}", "mode": "edit"})


@tenant_admin_required
def qbr_delete(request, pk):
    obj = get_object_or_404(QBR, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = str(obj)
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"QBR “{label}” deleted.")
    return redirect("success:qbr_list")
