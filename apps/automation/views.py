from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.decorators import tenant_admin_required
from apps.core.utils import log_action

from .forms import (
    AlertRuleForm, ApprovalWorkflowForm, AssignmentRuleForm, EnrichmentRuleForm, ProcessFlowForm,
)
from .models import (
    AlertRule, ApprovalWorkflow, AssignmentRule, EnrichmentRule, ProcessFlow,
)


def _no_tenant_redirect(request):
    messages.info(request, "Switch to a tenant workspace to manage this — the superuser has no tenant.")
    return redirect("dashboard:index")


def _page(request, qs, per_page=12):
    paginator = Paginator(qs, per_page)
    return paginator, paginator.get_page(request.GET.get("page"))


# ============================================================ process flows
@login_required
def processflow_list(request):
    qs = ProcessFlow.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
    trigger_event = request.GET.get("trigger_event", "")
    if trigger_event:
        qs = qs.filter(trigger_event=trigger_event)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "automation/processflow_list.html", {
        "page_title": "Visual Process Designer", "page_obj": page_obj,
        "processflows": page_obj.object_list,
        "trigger_choices": ProcessFlow.TRIGGER_EVENT_CHOICES,
        "status_choices": ProcessFlow.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def processflow_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = ProcessFlowForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Process flow created.")
        return redirect("automation:processflow_list")
    return render(request, "automation/processflow_form.html",
                  {"form": form, "page_title": "Add Process Flow", "mode": "create"})


@login_required
def processflow_detail(request, pk):
    obj = get_object_or_404(ProcessFlow, pk=pk, tenant=request.tenant)
    return render(request, "automation/processflow_detail.html",
                  {"obj": obj, "page_title": obj.name})


@tenant_admin_required
def processflow_edit(request, pk):
    obj = get_object_or_404(ProcessFlow, pk=pk, tenant=request.tenant)
    form = ProcessFlowForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Process flow updated.")
        return redirect("automation:processflow_detail", pk=obj.pk)
    return render(request, "automation/processflow_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.name}", "mode": "edit"})


@tenant_admin_required
def processflow_delete(request, pk):
    obj = get_object_or_404(ProcessFlow, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Process flow “{label}” deleted.")
    return redirect("automation:processflow_list")


# ============================================================ assignment rules
@login_required
def assignmentrule_list(request):
    qs = AssignmentRule.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q))
    entity = request.GET.get("entity", "")
    if entity:
        qs = qs.filter(entity=entity)
    assign_strategy = request.GET.get("assign_strategy", "")
    if assign_strategy:
        qs = qs.filter(assign_strategy=assign_strategy)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "automation/assignmentrule_list.html", {
        "page_title": "Auto-Assignment Rules", "page_obj": page_obj,
        "assignmentrules": page_obj.object_list,
        "entity_choices": AssignmentRule.ENTITY_CHOICES,
        "strategy_choices": AssignmentRule.ASSIGN_STRATEGY_CHOICES,
        "status_choices": AssignmentRule.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def assignmentrule_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = AssignmentRuleForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Assignment rule created.")
        return redirect("automation:assignmentrule_list")
    return render(request, "automation/assignmentrule_form.html",
                  {"form": form, "page_title": "Add Assignment Rule", "mode": "create"})


@login_required
def assignmentrule_detail(request, pk):
    obj = get_object_or_404(AssignmentRule, pk=pk, tenant=request.tenant)
    return render(request, "automation/assignmentrule_detail.html",
                  {"obj": obj, "page_title": obj.name})


@tenant_admin_required
def assignmentrule_edit(request, pk):
    obj = get_object_or_404(AssignmentRule, pk=pk, tenant=request.tenant)
    form = AssignmentRuleForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Assignment rule updated.")
        return redirect("automation:assignmentrule_detail", pk=obj.pk)
    return render(request, "automation/assignmentrule_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.name}", "mode": "edit"})


@tenant_admin_required
def assignmentrule_delete(request, pk):
    obj = get_object_or_404(AssignmentRule, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Assignment rule “{label}” deleted.")
    return redirect("automation:assignmentrule_list")


# ============================================================ approval workflows
@login_required
def approvalworkflow_list(request):
    qs = ApprovalWorkflow.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q))
    approval_type = request.GET.get("approval_type", "")
    if approval_type:
        qs = qs.filter(approval_type=approval_type)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "automation/approvalworkflow_list.html", {
        "page_title": "Approval Workflows", "page_obj": page_obj,
        "approvalworkflows": page_obj.object_list,
        "type_choices": ApprovalWorkflow.APPROVAL_TYPE_CHOICES,
        "status_choices": ApprovalWorkflow.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def approvalworkflow_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = ApprovalWorkflowForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Approval workflow created.")
        return redirect("automation:approvalworkflow_list")
    return render(request, "automation/approvalworkflow_form.html",
                  {"form": form, "page_title": "Add Approval Workflow", "mode": "create"})


@login_required
def approvalworkflow_detail(request, pk):
    obj = get_object_or_404(ApprovalWorkflow, pk=pk, tenant=request.tenant)
    return render(request, "automation/approvalworkflow_detail.html",
                  {"obj": obj, "page_title": obj.name})


@tenant_admin_required
def approvalworkflow_edit(request, pk):
    obj = get_object_or_404(ApprovalWorkflow, pk=pk, tenant=request.tenant)
    form = ApprovalWorkflowForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Approval workflow updated.")
        return redirect("automation:approvalworkflow_detail", pk=obj.pk)
    return render(request, "automation/approvalworkflow_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.name}", "mode": "edit"})


@tenant_admin_required
def approvalworkflow_delete(request, pk):
    obj = get_object_or_404(ApprovalWorkflow, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Approval workflow “{label}” deleted.")
    return redirect("automation:approvalworkflow_list")


# ============================================================ alert rules
@login_required
def alertrule_list(request):
    qs = AlertRule.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q))
    channel = request.GET.get("channel", "")
    if channel:
        qs = qs.filter(channel=channel)
    severity = request.GET.get("severity", "")
    if severity:
        qs = qs.filter(severity=severity)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "automation/alertrule_list.html", {
        "page_title": "Notification & Alert Engine", "page_obj": page_obj,
        "alertrules": page_obj.object_list,
        "channel_choices": AlertRule.CHANNEL_CHOICES,
        "severity_choices": AlertRule.SEVERITY_CHOICES,
        "status_choices": AlertRule.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def alertrule_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = AlertRuleForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Alert rule created.")
        return redirect("automation:alertrule_list")
    return render(request, "automation/alertrule_form.html",
                  {"form": form, "page_title": "Add Alert Rule", "mode": "create"})


@login_required
def alertrule_detail(request, pk):
    obj = get_object_or_404(AlertRule, pk=pk, tenant=request.tenant)
    return render(request, "automation/alertrule_detail.html",
                  {"obj": obj, "page_title": obj.name})


@tenant_admin_required
def alertrule_edit(request, pk):
    obj = get_object_or_404(AlertRule, pk=pk, tenant=request.tenant)
    form = AlertRuleForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Alert rule updated.")
        return redirect("automation:alertrule_detail", pk=obj.pk)
    return render(request, "automation/alertrule_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.name}", "mode": "edit"})


@tenant_admin_required
def alertrule_delete(request, pk):
    obj = get_object_or_404(AlertRule, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Alert rule “{label}” deleted.")
    return redirect("automation:alertrule_list")


# ============================================================ enrichment rules
@login_required
def enrichmentrule_list(request):
    qs = EnrichmentRule.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(target_field__icontains=q))
    data_source = request.GET.get("data_source", "")
    if data_source:
        qs = qs.filter(data_source=data_source)
    operation = request.GET.get("operation", "")
    if operation:
        qs = qs.filter(operation=operation)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "automation/enrichmentrule_list.html", {
        "page_title": "Data Enrichment & Cleansing", "page_obj": page_obj,
        "enrichmentrules": page_obj.object_list,
        "source_choices": EnrichmentRule.DATA_SOURCE_CHOICES,
        "operation_choices": EnrichmentRule.OPERATION_CHOICES,
        "status_choices": EnrichmentRule.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def enrichmentrule_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = EnrichmentRuleForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Enrichment rule created.")
        return redirect("automation:enrichmentrule_list")
    return render(request, "automation/enrichmentrule_form.html",
                  {"form": form, "page_title": "Add Enrichment Rule", "mode": "create"})


@login_required
def enrichmentrule_detail(request, pk):
    obj = get_object_or_404(EnrichmentRule, pk=pk, tenant=request.tenant)
    return render(request, "automation/enrichmentrule_detail.html",
                  {"obj": obj, "page_title": obj.name})


@tenant_admin_required
def enrichmentrule_edit(request, pk):
    obj = get_object_or_404(EnrichmentRule, pk=pk, tenant=request.tenant)
    form = EnrichmentRuleForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Enrichment rule updated.")
        return redirect("automation:enrichmentrule_detail", pk=obj.pk)
    return render(request, "automation/enrichmentrule_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.name}", "mode": "edit"})


@tenant_admin_required
def enrichmentrule_delete(request, pk):
    obj = get_object_or_404(EnrichmentRule, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Enrichment rule “{label}” deleted.")
    return redirect("automation:enrichmentrule_list")
