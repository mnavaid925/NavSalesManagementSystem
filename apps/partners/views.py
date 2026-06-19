from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.decorators import tenant_admin_required
from apps.core.utils import log_action

from .forms import (
    ChannelConflictForm, DealRegistrationForm, PartnerForm,
    PartnerCollateralForm, PartnerPerformanceForm,
)
from .models import (
    ChannelConflict, DealRegistration, Partner, PartnerCollateral, PartnerPerformance,
)


def _no_tenant_redirect(request):
    messages.info(request, "Switch to a tenant workspace to manage this — the superuser has no tenant.")
    return redirect("dashboard:index")


def _page(request, qs, per_page=12):
    paginator = Paginator(qs, per_page)
    return paginator, paginator.get_page(request.GET.get("page"))


# ============================================================ partners
@login_required
def partner_list(request):
    qs = Partner.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(region__icontains=q) | Q(contact_name__icontains=q))
    partner_type = request.GET.get("partner_type", "")
    if partner_type:
        qs = qs.filter(partner_type=partner_type)
    tier = request.GET.get("tier", "")
    if tier:
        qs = qs.filter(tier=tier)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "partners/partner_list.html", {
        "page_title": "Partner Recruitment & Onboarding", "page_obj": page_obj,
        "partners": page_obj.object_list,
        "type_choices": Partner.TYPE_CHOICES, "tier_choices": Partner.TIER_CHOICES,
        "status_choices": Partner.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def partner_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = PartnerForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Partner created.")
        return redirect("partners:partner_list")
    return render(request, "partners/partner_form.html",
                  {"form": form, "page_title": "Add Partner", "mode": "create"})


@login_required
def partner_detail(request, pk):
    obj = get_object_or_404(Partner, pk=pk, tenant=request.tenant)
    deals = obj.deal_registrations.filter(tenant=request.tenant)[:20]
    performances = obj.performances.filter(tenant=request.tenant)[:20]
    return render(request, "partners/partner_detail.html",
                  {"obj": obj, "deals": deals, "performances": performances, "page_title": obj.name})


@tenant_admin_required
def partner_edit(request, pk):
    obj = get_object_or_404(Partner, pk=pk, tenant=request.tenant)
    form = PartnerForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Partner updated.")
        return redirect("partners:partner_detail", pk=obj.pk)
    return render(request, "partners/partner_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.name}", "mode": "edit"})


@tenant_admin_required
def partner_delete(request, pk):
    obj = get_object_or_404(Partner, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Partner “{label}” deleted.")
    return redirect("partners:partner_list")


# ============================================================ deal registrations
@login_required
def dealregistration_list(request):
    qs = DealRegistration.objects.filter(tenant=request.tenant).select_related("partner")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(deal_name__icontains=q) | Q(customer_name__icontains=q))
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    partner = request.GET.get("partner", "")
    if partner.isdigit():
        qs = qs.filter(partner_id=partner)
    paginator, page_obj = _page(request, qs)
    return render(request, "partners/dealregistration_list.html", {
        "page_title": "Deal Registration & Protection", "page_obj": page_obj,
        "dealregistrations": page_obj.object_list,
        "status_choices": DealRegistration.STATUS_CHOICES,
        "partners": Partner.objects.filter(tenant=request.tenant),
        "total": paginator.count,
    })


@tenant_admin_required
def dealregistration_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = DealRegistrationForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, f"Deal {obj.number} registered.")
        return redirect("partners:dealregistration_list")
    return render(request, "partners/dealregistration_form.html",
                  {"form": form, "page_title": "Add Deal Registration", "mode": "create"})


@login_required
def dealregistration_detail(request, pk):
    obj = get_object_or_404(
        DealRegistration.objects.select_related("partner"), pk=pk, tenant=request.tenant)
    return render(request, "partners/dealregistration_detail.html",
                  {"obj": obj, "page_title": obj.number})


@tenant_admin_required
def dealregistration_edit(request, pk):
    obj = get_object_or_404(DealRegistration, pk=pk, tenant=request.tenant)
    form = DealRegistrationForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Deal registration updated.")
        return redirect("partners:dealregistration_detail", pk=obj.pk)
    return render(request, "partners/dealregistration_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.number}", "mode": "edit"})


@tenant_admin_required
def dealregistration_delete(request, pk):
    obj = get_object_or_404(DealRegistration, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.number
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Deal {label} deleted.")
    return redirect("partners:dealregistration_list")


# ============================================================ partner collateral
@login_required
def partnercollateral_list(request):
    qs = PartnerCollateral.objects.filter(tenant=request.tenant).select_related("partner")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(notes__icontains=q))
    asset_type = request.GET.get("asset_type", "")
    if asset_type:
        qs = qs.filter(asset_type=asset_type)
    access_level = request.GET.get("access_level", "")
    if access_level:
        qs = qs.filter(access_level=access_level)
    partner = request.GET.get("partner", "")
    if partner.isdigit():
        qs = qs.filter(partner_id=partner)
    paginator, page_obj = _page(request, qs)
    return render(request, "partners/partnercollateral_list.html", {
        "page_title": "Partner Portal & Collaboration", "page_obj": page_obj,
        "partnercollaterals": page_obj.object_list,
        "asset_type_choices": PartnerCollateral.ASSET_TYPE_CHOICES,
        "access_level_choices": PartnerCollateral.ACCESS_LEVEL_CHOICES,
        "partners": Partner.objects.filter(tenant=request.tenant),
        "total": paginator.count,
    })


@tenant_admin_required
def partnercollateral_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = PartnerCollateralForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Collateral added.")
        return redirect("partners:partnercollateral_list")
    return render(request, "partners/partnercollateral_form.html",
                  {"form": form, "page_title": "Add Collateral", "mode": "create"})


@login_required
def partnercollateral_detail(request, pk):
    obj = get_object_or_404(
        PartnerCollateral.objects.select_related("partner"), pk=pk, tenant=request.tenant)
    return render(request, "partners/partnercollateral_detail.html",
                  {"obj": obj, "page_title": obj.title})


@tenant_admin_required
def partnercollateral_edit(request, pk):
    obj = get_object_or_404(PartnerCollateral, pk=pk, tenant=request.tenant)
    form = PartnerCollateralForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Collateral updated.")
        return redirect("partners:partnercollateral_detail", pk=obj.pk)
    return render(request, "partners/partnercollateral_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.title}", "mode": "edit"})


@tenant_admin_required
def partnercollateral_delete(request, pk):
    obj = get_object_or_404(PartnerCollateral, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.title
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Collateral “{label}” deleted.")
    return redirect("partners:partnercollateral_list")


# ============================================================ partner performance
@login_required
def partnerperformance_list(request):
    qs = PartnerPerformance.objects.filter(tenant=request.tenant).select_related("partner")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(period_label__icontains=q))
    partner = request.GET.get("partner", "")
    if partner.isdigit():
        qs = qs.filter(partner_id=partner)
    paginator, page_obj = _page(request, qs)
    return render(request, "partners/partnerperformance_list.html", {
        "page_title": "Partner Performance Tracking", "page_obj": page_obj,
        "partnerperformances": page_obj.object_list,
        "partners": Partner.objects.filter(tenant=request.tenant),
        "total": paginator.count,
    })


@tenant_admin_required
def partnerperformance_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = PartnerPerformanceForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Performance record added.")
        return redirect("partners:partnerperformance_list")
    return render(request, "partners/partnerperformance_form.html",
                  {"form": form, "page_title": "Add Performance Record", "mode": "create"})


@login_required
def partnerperformance_detail(request, pk):
    obj = get_object_or_404(
        PartnerPerformance.objects.select_related("partner"), pk=pk, tenant=request.tenant)
    return render(request, "partners/partnerperformance_detail.html",
                  {"obj": obj, "page_title": str(obj)})


@tenant_admin_required
def partnerperformance_edit(request, pk):
    obj = get_object_or_404(PartnerPerformance, pk=pk, tenant=request.tenant)
    form = PartnerPerformanceForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Performance record updated.")
        return redirect("partners:partnerperformance_detail", pk=obj.pk)
    return render(request, "partners/partnerperformance_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj}", "mode": "edit"})


@tenant_admin_required
def partnerperformance_delete(request, pk):
    obj = get_object_or_404(PartnerPerformance, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = str(obj)
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Performance record “{label}” deleted.")
    return redirect("partners:partnerperformance_list")


# ============================================================ channel conflicts
@login_required
def channelconflict_list(request):
    qs = ChannelConflict.objects.filter(tenant=request.tenant).select_related("partner")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(account_name__icontains=q))
    conflict_type = request.GET.get("conflict_type", "")
    if conflict_type:
        qs = qs.filter(conflict_type=conflict_type)
    severity = request.GET.get("severity", "")
    if severity:
        qs = qs.filter(severity=severity)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "partners/channelconflict_list.html", {
        "page_title": "Channel Conflict Management", "page_obj": page_obj,
        "channelconflicts": page_obj.object_list,
        "type_choices": ChannelConflict.CONFLICT_TYPE_CHOICES,
        "severity_choices": ChannelConflict.SEVERITY_CHOICES,
        "status_choices": ChannelConflict.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def channelconflict_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = ChannelConflictForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, f"Conflict {obj.number} logged.")
        return redirect("partners:channelconflict_list")
    return render(request, "partners/channelconflict_form.html",
                  {"form": form, "page_title": "Add Channel Conflict", "mode": "create"})


@login_required
def channelconflict_detail(request, pk):
    obj = get_object_or_404(
        ChannelConflict.objects.select_related("partner"), pk=pk, tenant=request.tenant)
    return render(request, "partners/channelconflict_detail.html",
                  {"obj": obj, "page_title": obj.number})


@tenant_admin_required
def channelconflict_edit(request, pk):
    obj = get_object_or_404(ChannelConflict, pk=pk, tenant=request.tenant)
    form = ChannelConflictForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Conflict updated.")
        return redirect("partners:channelconflict_detail", pk=obj.pk)
    return render(request, "partners/channelconflict_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.number}", "mode": "edit"})


@tenant_admin_required
def channelconflict_delete(request, pk):
    obj = get_object_or_404(ChannelConflict, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.number
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Conflict {label} deleted.")
    return redirect("partners:channelconflict_list")
