from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.decorators import tenant_admin_required
from apps.core.utils import log_action

from .forms import (
    CallActivityForm, FieldVisitForm, MobileAlertForm, MobileDeviceForm, MobileQuoteForm,
)
from .models import (
    CallActivity, FieldVisit, MobileAlert, MobileDevice, MobileQuote,
)


def _no_tenant_redirect(request):
    messages.info(request, "Switch to a tenant workspace to manage this — the superuser has no tenant.")
    return redirect("dashboard:index")


def _page(request, qs, per_page=12):
    paginator = Paginator(qs, per_page)
    return paginator, paginator.get_page(request.GET.get("page"))


# ============================================================ mobile devices
@login_required
def mobiledevice_list(request):
    qs = MobileDevice.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(device_name__icontains=q) | Q(user_name__icontains=q))
    platform = request.GET.get("platform", "")
    if platform:
        qs = qs.filter(platform=platform)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "mobile/mobiledevice_list.html", {
        "page_title": "Mobile CRM Access", "page_obj": page_obj, "mobiledevices": page_obj.object_list,
        "platform_choices": MobileDevice.PLATFORM_CHOICES, "status_choices": MobileDevice.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def mobiledevice_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = MobileDeviceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Mobile device registered.")
        return redirect("mobile:mobiledevice_list")
    return render(request, "mobile/mobiledevice_form.html",
                  {"form": form, "page_title": "Add Mobile Device", "mode": "create"})


@login_required
def mobiledevice_detail(request, pk):
    obj = get_object_or_404(MobileDevice, pk=pk, tenant=request.tenant)
    return render(request, "mobile/mobiledevice_detail.html", {"obj": obj, "page_title": obj.device_name})


@tenant_admin_required
def mobiledevice_edit(request, pk):
    obj = get_object_or_404(MobileDevice, pk=pk, tenant=request.tenant)
    form = MobileDeviceForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Mobile device updated.")
        return redirect("mobile:mobiledevice_detail", pk=obj.pk)
    return render(request, "mobile/mobiledevice_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.device_name}", "mode": "edit"})


@tenant_admin_required
def mobiledevice_delete(request, pk):
    obj = get_object_or_404(MobileDevice, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.device_name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Device “{label}” deleted.")
    return redirect("mobile:mobiledevice_list")


# ============================================================ field visits
@login_required
def fieldvisit_list(request):
    qs = FieldVisit.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(rep_name__icontains=q) | Q(account_name__icontains=q))
    visit_type = request.GET.get("visit_type", "")
    if visit_type:
        qs = qs.filter(visit_type=visit_type)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "mobile/fieldvisit_list.html", {
        "page_title": "Field Sales Tools", "page_obj": page_obj, "fieldvisits": page_obj.object_list,
        "type_choices": FieldVisit.TYPE_CHOICES, "status_choices": FieldVisit.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def fieldvisit_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = FieldVisitForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, f"Field visit {obj.number} scheduled.")
        return redirect("mobile:fieldvisit_list")
    return render(request, "mobile/fieldvisit_form.html",
                  {"form": form, "page_title": "Add Field Visit", "mode": "create"})


@login_required
def fieldvisit_detail(request, pk):
    obj = get_object_or_404(FieldVisit, pk=pk, tenant=request.tenant)
    return render(request, "mobile/fieldvisit_detail.html", {"obj": obj, "page_title": obj.number})


@tenant_admin_required
def fieldvisit_edit(request, pk):
    obj = get_object_or_404(FieldVisit, pk=pk, tenant=request.tenant)
    form = FieldVisitForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Field visit updated.")
        return redirect("mobile:fieldvisit_detail", pk=obj.pk)
    return render(request, "mobile/fieldvisit_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.number}", "mode": "edit"})


@tenant_admin_required
def fieldvisit_delete(request, pk):
    obj = get_object_or_404(FieldVisit, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.number
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Field visit {label} deleted.")
    return redirect("mobile:fieldvisit_list")


# ============================================================ mobile quotes
@login_required
def mobilequote_list(request):
    qs = MobileQuote.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(rep_name__icontains=q) | Q(customer_name__icontains=q))
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "mobile/mobilequote_list.html", {
        "page_title": "Mobile Quoting & Approvals", "page_obj": page_obj, "mobilequotes": page_obj.object_list,
        "status_choices": MobileQuote.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def mobilequote_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = MobileQuoteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, f"Mobile quote {obj.number} created.")
        return redirect("mobile:mobilequote_list")
    return render(request, "mobile/mobilequote_form.html",
                  {"form": form, "page_title": "Add Mobile Quote", "mode": "create"})


@login_required
def mobilequote_detail(request, pk):
    obj = get_object_or_404(MobileQuote, pk=pk, tenant=request.tenant)
    return render(request, "mobile/mobilequote_detail.html", {"obj": obj, "page_title": obj.number})


@tenant_admin_required
def mobilequote_edit(request, pk):
    obj = get_object_or_404(MobileQuote, pk=pk, tenant=request.tenant)
    form = MobileQuoteForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Mobile quote updated.")
        return redirect("mobile:mobilequote_detail", pk=obj.pk)
    return render(request, "mobile/mobilequote_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.number}", "mode": "edit"})


@tenant_admin_required
def mobilequote_delete(request, pk):
    obj = get_object_or_404(MobileQuote, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.number
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Mobile quote {label} deleted.")
    return redirect("mobile:mobilequote_list")


# ============================================================ call activities
@login_required
def callactivity_list(request):
    qs = CallActivity.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(rep_name__icontains=q) | Q(contact_name__icontains=q))
    direction = request.GET.get("direction", "")
    if direction:
        qs = qs.filter(direction=direction)
    outcome = request.GET.get("outcome", "")
    if outcome:
        qs = qs.filter(outcome=outcome)
    paginator, page_obj = _page(request, qs)
    return render(request, "mobile/callactivity_list.html", {
        "page_title": "Voice & Call Integration", "page_obj": page_obj, "callactivities": page_obj.object_list,
        "direction_choices": CallActivity.DIRECTION_CHOICES, "outcome_choices": CallActivity.OUTCOME_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def callactivity_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = CallActivityForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Call activity logged.")
        return redirect("mobile:callactivity_list")
    return render(request, "mobile/callactivity_form.html",
                  {"form": form, "page_title": "Add Call Activity", "mode": "create"})


@login_required
def callactivity_detail(request, pk):
    obj = get_object_or_404(CallActivity, pk=pk, tenant=request.tenant)
    return render(request, "mobile/callactivity_detail.html", {"obj": obj, "page_title": str(obj)})


@tenant_admin_required
def callactivity_edit(request, pk):
    obj = get_object_or_404(CallActivity, pk=pk, tenant=request.tenant)
    form = CallActivityForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Call activity updated.")
        return redirect("mobile:callactivity_detail", pk=obj.pk)
    return render(request, "mobile/callactivity_form.html",
                  {"form": form, "obj": obj, "page_title": "Edit call activity", "mode": "edit"})


@tenant_admin_required
def callactivity_delete(request, pk):
    obj = get_object_or_404(CallActivity, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, "Call activity deleted.")
    return redirect("mobile:callactivity_list")


# ============================================================ mobile alerts
@login_required
def mobilealert_list(request):
    qs = MobileAlert.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(recipient__icontains=q))
    alert_type = request.GET.get("alert_type", "")
    if alert_type:
        qs = qs.filter(alert_type=alert_type)
    priority = request.GET.get("priority", "")
    if priority:
        qs = qs.filter(priority=priority)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "mobile/mobilealert_list.html", {
        "page_title": "Mobile Dashboards & Alerts", "page_obj": page_obj, "mobilealerts": page_obj.object_list,
        "type_choices": MobileAlert.TYPE_CHOICES, "priority_choices": MobileAlert.PRIORITY_CHOICES,
        "status_choices": MobileAlert.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def mobilealert_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = MobileAlertForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Mobile alert created.")
        return redirect("mobile:mobilealert_list")
    return render(request, "mobile/mobilealert_form.html",
                  {"form": form, "page_title": "Add Mobile Alert", "mode": "create"})


@login_required
def mobilealert_detail(request, pk):
    obj = get_object_or_404(MobileAlert, pk=pk, tenant=request.tenant)
    return render(request, "mobile/mobilealert_detail.html", {"obj": obj, "page_title": obj.title})


@tenant_admin_required
def mobilealert_edit(request, pk):
    obj = get_object_or_404(MobileAlert, pk=pk, tenant=request.tenant)
    form = MobileAlertForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Mobile alert updated.")
        return redirect("mobile:mobilealert_detail", pk=obj.pk)
    return render(request, "mobile/mobilealert_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.title}", "mode": "edit"})


@tenant_admin_required
def mobilealert_delete(request, pk):
    obj = get_object_or_404(MobileAlert, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.title
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Alert “{label}” deleted.")
    return redirect("mobile:mobilealert_list")
