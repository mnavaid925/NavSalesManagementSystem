from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.decorators import tenant_admin_required
from apps.core.utils import log_action

from .forms import (
    BenchmarkForm, ConversionFunnelForm, RepScorecardForm, SalesVelocityForm,
    WinLossAnalysisForm,
)
from .models import (
    Benchmark, ConversionFunnel, RepScorecard, SalesVelocity, WinLossAnalysis,
)


def _no_tenant_redirect(request):
    messages.info(request, "Switch to a tenant workspace to manage this — the superuser has no tenant.")
    return redirect("dashboard:index")


def _page(request, qs, per_page=12):
    paginator = Paginator(qs, per_page)
    return paginator, paginator.get_page(request.GET.get("page"))


# ============================================================ win/loss analysis
@login_required
def winlossanalysis_list(request):
    qs = WinLossAnalysis.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(deal_name__icontains=q) | Q(rep_name__icontains=q)
                       | Q(competitor__icontains=q))
    outcome = request.GET.get("outcome", "")
    if outcome:
        qs = qs.filter(outcome=outcome)
    reason_category = request.GET.get("reason_category", "")
    if reason_category:
        qs = qs.filter(reason_category=reason_category)
    paginator, page_obj = _page(request, qs)
    return render(request, "analytics/winlossanalysis_list.html", {
        "page_title": "Win/Loss Analysis", "page_obj": page_obj,
        "winlossanalysises": page_obj.object_list,
        "outcome_choices": WinLossAnalysis.OUTCOME_CHOICES,
        "reason_category_choices": WinLossAnalysis.REASON_CATEGORY_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def winlossanalysis_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = WinLossAnalysisForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Win/loss record created.")
        return redirect("analytics:winlossanalysis_list")
    return render(request, "analytics/winlossanalysis_form.html",
                  {"form": form, "page_title": "Add Win/Loss Record", "mode": "create"})


@login_required
def winlossanalysis_detail(request, pk):
    obj = get_object_or_404(WinLossAnalysis, pk=pk, tenant=request.tenant)
    return render(request, "analytics/winlossanalysis_detail.html",
                  {"obj": obj, "page_title": obj.deal_name})


@tenant_admin_required
def winlossanalysis_edit(request, pk):
    obj = get_object_or_404(WinLossAnalysis, pk=pk, tenant=request.tenant)
    form = WinLossAnalysisForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Win/loss record updated.")
        return redirect("analytics:winlossanalysis_detail", pk=obj.pk)
    return render(request, "analytics/winlossanalysis_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.deal_name}", "mode": "edit"})


@tenant_admin_required
def winlossanalysis_delete(request, pk):
    obj = get_object_or_404(WinLossAnalysis, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.deal_name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Win/loss record “{label}” deleted.")
    return redirect("analytics:winlossanalysis_list")


# ============================================================ sales velocity
@login_required
def salesvelocity_list(request):
    qs = SalesVelocity.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(period_label__icontains=q))
    segment = request.GET.get("segment", "")
    if segment:
        qs = qs.filter(segment=segment)
    paginator, page_obj = _page(request, qs)
    return render(request, "analytics/salesvelocity_list.html", {
        "page_title": "Sales Velocity & Cycle Time", "page_obj": page_obj,
        "salesvelocitys": page_obj.object_list,
        "segment_choices": SalesVelocity.SEGMENT_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def salesvelocity_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = SalesVelocityForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Sales velocity record created.")
        return redirect("analytics:salesvelocity_list")
    return render(request, "analytics/salesvelocity_form.html",
                  {"form": form, "page_title": "Add Velocity Record", "mode": "create"})


@login_required
def salesvelocity_detail(request, pk):
    obj = get_object_or_404(SalesVelocity, pk=pk, tenant=request.tenant)
    return render(request, "analytics/salesvelocity_detail.html",
                  {"obj": obj, "page_title": obj.period_label})


@tenant_admin_required
def salesvelocity_edit(request, pk):
    obj = get_object_or_404(SalesVelocity, pk=pk, tenant=request.tenant)
    form = SalesVelocityForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Sales velocity record updated.")
        return redirect("analytics:salesvelocity_detail", pk=obj.pk)
    return render(request, "analytics/salesvelocity_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.period_label}", "mode": "edit"})


@tenant_admin_required
def salesvelocity_delete(request, pk):
    obj = get_object_or_404(SalesVelocity, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.period_label
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Velocity record “{label}” deleted.")
    return redirect("analytics:salesvelocity_list")


# ============================================================ conversion funnel
@login_required
def conversionfunnel_list(request):
    qs = ConversionFunnel.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(stage_name__icontains=q) | Q(period_label__icontains=q))
    segment = request.GET.get("segment", "")
    if segment:
        qs = qs.filter(segment=segment)
    paginator, page_obj = _page(request, qs)
    return render(request, "analytics/conversionfunnel_list.html", {
        "page_title": "Conversion Funnel Analytics", "page_obj": page_obj,
        "conversionfunnels": page_obj.object_list,
        "segment_choices": ConversionFunnel.SEGMENT_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def conversionfunnel_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = ConversionFunnelForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Funnel stage record created.")
        return redirect("analytics:conversionfunnel_list")
    return render(request, "analytics/conversionfunnel_form.html",
                  {"form": form, "page_title": "Add Funnel Stage", "mode": "create"})


@login_required
def conversionfunnel_detail(request, pk):
    obj = get_object_or_404(ConversionFunnel, pk=pk, tenant=request.tenant)
    return render(request, "analytics/conversionfunnel_detail.html",
                  {"obj": obj, "page_title": obj.stage_name})


@tenant_admin_required
def conversionfunnel_edit(request, pk):
    obj = get_object_or_404(ConversionFunnel, pk=pk, tenant=request.tenant)
    form = ConversionFunnelForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Funnel stage record updated.")
        return redirect("analytics:conversionfunnel_detail", pk=obj.pk)
    return render(request, "analytics/conversionfunnel_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.stage_name}", "mode": "edit"})


@tenant_admin_required
def conversionfunnel_delete(request, pk):
    obj = get_object_or_404(ConversionFunnel, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.stage_name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Funnel stage “{label}” deleted.")
    return redirect("analytics:conversionfunnel_list")


# ============================================================ rep scorecards
@login_required
def repscorecard_list(request):
    qs = RepScorecard.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(rep_name__icontains=q) | Q(period_label__icontains=q))
    grade = request.GET.get("grade", "")
    if grade:
        qs = qs.filter(grade=grade)
    paginator, page_obj = _page(request, qs)
    return render(request, "analytics/repscorecard_list.html", {
        "page_title": "Rep Performance Scorecards", "page_obj": page_obj,
        "repscorecards": page_obj.object_list,
        "grade_choices": RepScorecard.GRADE_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def repscorecard_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = RepScorecardForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Scorecard created.")
        return redirect("analytics:repscorecard_list")
    return render(request, "analytics/repscorecard_form.html",
                  {"form": form, "page_title": "Add Scorecard", "mode": "create"})


@login_required
def repscorecard_detail(request, pk):
    obj = get_object_or_404(RepScorecard, pk=pk, tenant=request.tenant)
    return render(request, "analytics/repscorecard_detail.html",
                  {"obj": obj, "page_title": str(obj)})


@tenant_admin_required
def repscorecard_edit(request, pk):
    obj = get_object_or_404(RepScorecard, pk=pk, tenant=request.tenant)
    form = RepScorecardForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Scorecard updated.")
        return redirect("analytics:repscorecard_detail", pk=obj.pk)
    return render(request, "analytics/repscorecard_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj}", "mode": "edit"})


@tenant_admin_required
def repscorecard_delete(request, pk):
    obj = get_object_or_404(RepScorecard, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = str(obj)
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Scorecard “{label}” deleted.")
    return redirect("analytics:repscorecard_list")


# ============================================================ benchmarks
@login_required
def benchmark_list(request):
    qs = Benchmark.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(metric_name__icontains=q) | Q(period_label__icontains=q))
    category = request.GET.get("category", "")
    if category:
        qs = qs.filter(category=category)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "analytics/benchmark_list.html", {
        "page_title": "Benchmarking & Peer Comparison", "page_obj": page_obj,
        "benchmarks": page_obj.object_list,
        "category_choices": Benchmark.CATEGORY_CHOICES,
        "status_choices": Benchmark.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def benchmark_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = BenchmarkForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Benchmark created.")
        return redirect("analytics:benchmark_list")
    return render(request, "analytics/benchmark_form.html",
                  {"form": form, "page_title": "Add Benchmark", "mode": "create"})


@login_required
def benchmark_detail(request, pk):
    obj = get_object_or_404(Benchmark, pk=pk, tenant=request.tenant)
    return render(request, "analytics/benchmark_detail.html",
                  {"obj": obj, "page_title": obj.metric_name})


@tenant_admin_required
def benchmark_edit(request, pk):
    obj = get_object_or_404(Benchmark, pk=pk, tenant=request.tenant)
    form = BenchmarkForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Benchmark updated.")
        return redirect("analytics:benchmark_detail", pk=obj.pk)
    return render(request, "analytics/benchmark_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.metric_name}", "mode": "edit"})


@tenant_admin_required
def benchmark_delete(request, pk):
    obj = get_object_or_404(Benchmark, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.metric_name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Benchmark “{label}” deleted.")
    return redirect("analytics:benchmark_list")
