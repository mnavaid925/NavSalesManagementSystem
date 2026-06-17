from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.decorators import tenant_admin_required
from apps.core.utils import log_action

from .forms import (
    ActivityForm, EmailLogForm, MeetingForm, SalesPlanForm, SalesTaskForm,
)
from .models import Activity, EmailLog, Meeting, SalesPlan, SalesTask


def _no_tenant_redirect(request):
    messages.info(request, "Switch to a tenant workspace to manage this — the superuser has no tenant.")
    return redirect("dashboard:index")


def _page(request, qs, per_page=12):
    paginator = Paginator(qs, per_page)
    return paginator, paginator.get_page(request.GET.get("page"))


# ============================================================ activities
@login_required
def activity_list(request):
    qs = Activity.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(subject__icontains=q) | Q(contact_name__icontains=q)
            | Q(company_name__icontains=q) | Q(notes__icontains=q)
        )
    activity_type = request.GET.get("activity_type", "")
    if activity_type:
        qs = qs.filter(activity_type=activity_type)
    outcome = request.GET.get("outcome", "")
    if outcome:
        qs = qs.filter(outcome=outcome)
    paginator, page_obj = _page(request, qs)
    return render(request, "activities/activity_list.html", {
        "page_title": "Activity Logging & Tracking", "page_obj": page_obj,
        "activities": page_obj.object_list,
        "type_choices": Activity.TYPE_CHOICES, "outcome_choices": Activity.OUTCOME_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def activity_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = ActivityForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Activity logged.")
        return redirect("activities:activity_list")
    return render(request, "activities/activity_form.html",
                  {"form": form, "page_title": "Log Activity", "mode": "create"})


@login_required
def activity_detail(request, pk):
    obj = get_object_or_404(Activity, pk=pk, tenant=request.tenant)
    return render(request, "activities/activity_detail.html", {"obj": obj, "page_title": obj.subject})


@tenant_admin_required
def activity_edit(request, pk):
    obj = get_object_or_404(Activity, pk=pk, tenant=request.tenant)
    form = ActivityForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Activity updated.")
        return redirect("activities:activity_detail", pk=obj.pk)
    return render(request, "activities/activity_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.subject}", "mode": "edit"})


@tenant_admin_required
def activity_delete(request, pk):
    obj = get_object_or_404(Activity, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.subject
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Activity “{label}” deleted.")
    return redirect("activities:activity_list")


# ============================================================ sales tasks
@login_required
def salestask_list(request):
    qs = SalesTask.objects.filter(tenant=request.tenant).select_related("activity")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(title__icontains=q) | Q(description__icontains=q)
            | Q(assigned_to__icontains=q) | Q(related_to__icontains=q)
        )
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    priority = request.GET.get("priority", "")
    if priority:
        qs = qs.filter(priority=priority)
    paginator, page_obj = _page(request, qs)
    return render(request, "activities/salestask_list.html", {
        "page_title": "Task & Follow-up Management", "page_obj": page_obj,
        "tasks": page_obj.object_list,
        "status_choices": SalesTask.STATUS_CHOICES, "priority_choices": SalesTask.PRIORITY_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def salestask_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = SalesTaskForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Task created.")
        return redirect("activities:salestask_list")
    return render(request, "activities/salestask_form.html",
                  {"form": form, "page_title": "Add Task", "mode": "create"})


@login_required
def salestask_detail(request, pk):
    obj = get_object_or_404(SalesTask.objects.select_related("activity"), pk=pk, tenant=request.tenant)
    return render(request, "activities/salestask_detail.html", {"obj": obj, "page_title": obj.title})


@tenant_admin_required
def salestask_edit(request, pk):
    obj = get_object_or_404(SalesTask, pk=pk, tenant=request.tenant)
    form = SalesTaskForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Task updated.")
        return redirect("activities:salestask_detail", pk=obj.pk)
    return render(request, "activities/salestask_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.title}", "mode": "edit"})


@tenant_admin_required
def salestask_delete(request, pk):
    obj = get_object_or_404(SalesTask, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.title
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Task “{label}” deleted.")
    return redirect("activities:salestask_list")


# ============================================================ meetings
@login_required
def meeting_list(request):
    qs = Meeting.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(title__icontains=q) | Q(attendees__icontains=q)
            | Q(location__icontains=q) | Q(organizer_name__icontains=q)
        )
    meeting_type = request.GET.get("meeting_type", "")
    if meeting_type:
        qs = qs.filter(meeting_type=meeting_type)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "activities/meeting_list.html", {
        "page_title": "Calendar & Meeting Scheduling", "page_obj": page_obj,
        "meetings": page_obj.object_list,
        "type_choices": Meeting.TYPE_CHOICES, "status_choices": Meeting.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def meeting_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = MeetingForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Meeting scheduled.")
        return redirect("activities:meeting_list")
    return render(request, "activities/meeting_form.html",
                  {"form": form, "page_title": "Schedule Meeting", "mode": "create"})


@login_required
def meeting_detail(request, pk):
    obj = get_object_or_404(Meeting, pk=pk, tenant=request.tenant)
    return render(request, "activities/meeting_detail.html", {"obj": obj, "page_title": obj.title})


@tenant_admin_required
def meeting_edit(request, pk):
    obj = get_object_or_404(Meeting, pk=pk, tenant=request.tenant)
    form = MeetingForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Meeting updated.")
        return redirect("activities:meeting_detail", pk=obj.pk)
    return render(request, "activities/meeting_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.title}", "mode": "edit"})


@tenant_admin_required
def meeting_delete(request, pk):
    obj = get_object_or_404(Meeting, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.title
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Meeting “{label}” deleted.")
    return redirect("activities:meeting_list")


# ============================================================ email logs
@login_required
def emaillog_list(request):
    qs = EmailLog.objects.filter(tenant=request.tenant).select_related("activity")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(subject__icontains=q) | Q(from_email__icontains=q)
            | Q(to_email__icontains=q) | Q(body__icontains=q)
        )
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    direction = request.GET.get("direction", "")
    if direction:
        qs = qs.filter(direction=direction)
    paginator, page_obj = _page(request, qs)
    return render(request, "activities/emaillog_list.html", {
        "page_title": "Email Integration & Tracking", "page_obj": page_obj,
        "emails": page_obj.object_list,
        "status_choices": EmailLog.STATUS_CHOICES, "direction_choices": EmailLog.DIRECTION_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def emaillog_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = EmailLogForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Email logged.")
        return redirect("activities:emaillog_list")
    return render(request, "activities/emaillog_form.html",
                  {"form": form, "page_title": "Log Email", "mode": "create"})


@login_required
def emaillog_detail(request, pk):
    obj = get_object_or_404(EmailLog.objects.select_related("activity"), pk=pk, tenant=request.tenant)
    return render(request, "activities/emaillog_detail.html", {"obj": obj, "page_title": obj.subject})


@tenant_admin_required
def emaillog_edit(request, pk):
    obj = get_object_or_404(EmailLog, pk=pk, tenant=request.tenant)
    form = EmailLogForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Email updated.")
        return redirect("activities:emaillog_detail", pk=obj.pk)
    return render(request, "activities/emaillog_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.subject}", "mode": "edit"})


@tenant_admin_required
def emaillog_delete(request, pk):
    obj = get_object_or_404(EmailLog, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.subject
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Email “{label}” deleted.")
    return redirect("activities:emaillog_list")


# ============================================================ sales plans
@login_required
def salesplan_list(request):
    qs = SalesPlan.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(title__icontains=q)
            | Q(owner_name__icontains=q) | Q(objectives__icontains=q)
        )
    period_type = request.GET.get("period_type", "")
    if period_type:
        qs = qs.filter(period_type=period_type)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "activities/salesplan_list.html", {
        "page_title": "Daily/Weekly Sales Planning", "page_obj": page_obj,
        "plans": page_obj.object_list,
        "period_choices": SalesPlan.PERIOD_CHOICES, "status_choices": SalesPlan.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def salesplan_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = SalesPlanForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, f"Sales plan {obj.number} created.")
        return redirect("activities:salesplan_list")
    return render(request, "activities/salesplan_form.html",
                  {"form": form, "page_title": "Add Sales Plan", "mode": "create"})


@login_required
def salesplan_detail(request, pk):
    obj = get_object_or_404(SalesPlan, pk=pk, tenant=request.tenant)
    return render(request, "activities/salesplan_detail.html", {"obj": obj, "page_title": obj.number})


@tenant_admin_required
def salesplan_edit(request, pk):
    obj = get_object_or_404(SalesPlan, pk=pk, tenant=request.tenant)
    form = SalesPlanForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Sales plan updated.")
        return redirect("activities:salesplan_detail", pk=obj.pk)
    return render(request, "activities/salesplan_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.number}", "mode": "edit"})


@tenant_admin_required
def salesplan_delete(request, pk):
    obj = get_object_or_404(SalesPlan, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.number
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Sales plan {label} deleted.")
    return redirect("activities:salesplan_list")
