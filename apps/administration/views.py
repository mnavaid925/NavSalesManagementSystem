from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.decorators import tenant_admin_required
from apps.core.utils import log_action

from .forms import (
    BackupJobForm, ComplianceItemForm, DataPrivacyRuleForm, SecurityPolicyForm,
    SystemHealthMetricForm,
)
from .models import (
    BackupJob, ComplianceItem, DataPrivacyRule, SecurityPolicy, SystemHealthMetric,
)


def _no_tenant_redirect(request):
    messages.info(request, "Switch to a tenant workspace to manage this — the superuser has no tenant.")
    return redirect("dashboard:index")


def _page(request, qs, per_page=12):
    paginator = Paginator(qs, per_page)
    return paginator, paginator.get_page(request.GET.get("page"))


# ============================================================ security policies
@login_required
def securitypolicy_list(request):
    qs = SecurityPolicy.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
    policy_type = request.GET.get("policy_type", "")
    if policy_type:
        qs = qs.filter(policy_type=policy_type)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    severity = request.GET.get("severity", "")
    if severity:
        qs = qs.filter(severity=severity)
    paginator, page_obj = _page(request, qs)
    return render(request, "administration/securitypolicy_list.html", {
        "page_title": "Data Security & Privacy", "page_obj": page_obj,
        "securitypolicys": page_obj.object_list,
        "type_choices": SecurityPolicy.POLICY_TYPE_CHOICES,
        "status_choices": SecurityPolicy.STATUS_CHOICES,
        "severity_choices": SecurityPolicy.SEVERITY_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def securitypolicy_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = SecurityPolicyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Security policy created.")
        return redirect("administration:securitypolicy_list")
    return render(request, "administration/securitypolicy_form.html",
                  {"form": form, "page_title": "Add Security Policy", "mode": "create"})


@login_required
def securitypolicy_detail(request, pk):
    obj = get_object_or_404(SecurityPolicy, pk=pk, tenant=request.tenant)
    return render(request, "administration/securitypolicy_detail.html",
                  {"obj": obj, "page_title": obj.name})


@tenant_admin_required
def securitypolicy_edit(request, pk):
    obj = get_object_or_404(SecurityPolicy, pk=pk, tenant=request.tenant)
    form = SecurityPolicyForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Security policy updated.")
        return redirect("administration:securitypolicy_detail", pk=obj.pk)
    return render(request, "administration/securitypolicy_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.name}", "mode": "edit"})


@tenant_admin_required
def securitypolicy_delete(request, pk):
    obj = get_object_or_404(SecurityPolicy, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Security policy “{label}” deleted.")
    return redirect("administration:securitypolicy_list")


# ============================================================ data privacy rules
@login_required
def dataprivacyrule_list(request):
    qs = DataPrivacyRule.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q))
    regulation = request.GET.get("regulation", "")
    if regulation:
        qs = qs.filter(regulation=regulation)
    data_category = request.GET.get("data_category", "")
    if data_category:
        qs = qs.filter(data_category=data_category)
    action = request.GET.get("action", "")
    if action:
        qs = qs.filter(action=action)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "administration/dataprivacyrule_list.html", {
        "page_title": "Data Privacy Rules", "page_obj": page_obj,
        "dataprivacyrules": page_obj.object_list,
        "regulation_choices": DataPrivacyRule.REGULATION_CHOICES,
        "category_choices": DataPrivacyRule.DATA_CATEGORY_CHOICES,
        "action_choices": DataPrivacyRule.ACTION_CHOICES,
        "status_choices": DataPrivacyRule.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def dataprivacyrule_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = DataPrivacyRuleForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Privacy rule created.")
        return redirect("administration:dataprivacyrule_list")
    return render(request, "administration/dataprivacyrule_form.html",
                  {"form": form, "page_title": "Add Privacy Rule", "mode": "create"})


@login_required
def dataprivacyrule_detail(request, pk):
    obj = get_object_or_404(DataPrivacyRule, pk=pk, tenant=request.tenant)
    return render(request, "administration/dataprivacyrule_detail.html",
                  {"obj": obj, "page_title": obj.name})


@tenant_admin_required
def dataprivacyrule_edit(request, pk):
    obj = get_object_or_404(DataPrivacyRule, pk=pk, tenant=request.tenant)
    form = DataPrivacyRuleForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Privacy rule updated.")
        return redirect("administration:dataprivacyrule_detail", pk=obj.pk)
    return render(request, "administration/dataprivacyrule_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.name}", "mode": "edit"})


@tenant_admin_required
def dataprivacyrule_delete(request, pk):
    obj = get_object_or_404(DataPrivacyRule, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Privacy rule “{label}” deleted.")
    return redirect("administration:dataprivacyrule_list")


# ============================================================ compliance items
@login_required
def complianceitem_list(request):
    qs = ComplianceItem.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(owner__icontains=q))
    framework = request.GET.get("framework", "")
    if framework:
        qs = qs.filter(framework=framework)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    severity = request.GET.get("severity", "")
    if severity:
        qs = qs.filter(severity=severity)
    paginator, page_obj = _page(request, qs)
    return render(request, "administration/complianceitem_list.html", {
        "page_title": "Compliance Tracking", "page_obj": page_obj,
        "complianceitems": page_obj.object_list,
        "framework_choices": ComplianceItem.FRAMEWORK_CHOICES,
        "status_choices": ComplianceItem.STATUS_CHOICES,
        "severity_choices": ComplianceItem.SEVERITY_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def complianceitem_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = ComplianceItemForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Compliance item created.")
        return redirect("administration:complianceitem_list")
    return render(request, "administration/complianceitem_form.html",
                  {"form": form, "page_title": "Add Compliance Item", "mode": "create"})


@login_required
def complianceitem_detail(request, pk):
    obj = get_object_or_404(ComplianceItem, pk=pk, tenant=request.tenant)
    return render(request, "administration/complianceitem_detail.html",
                  {"obj": obj, "page_title": obj.title})


@tenant_admin_required
def complianceitem_edit(request, pk):
    obj = get_object_or_404(ComplianceItem, pk=pk, tenant=request.tenant)
    form = ComplianceItemForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Compliance item updated.")
        return redirect("administration:complianceitem_detail", pk=obj.pk)
    return render(request, "administration/complianceitem_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.title}", "mode": "edit"})


@tenant_admin_required
def complianceitem_delete(request, pk):
    obj = get_object_or_404(ComplianceItem, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.title
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Compliance item “{label}” deleted.")
    return redirect("administration:complianceitem_list")


# ============================================================ backup jobs
@login_required
def backupjob_list(request):
    qs = BackupJob.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(name__icontains=q))
    backup_type = request.GET.get("backup_type", "")
    if backup_type:
        qs = qs.filter(backup_type=backup_type)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "administration/backupjob_list.html", {
        "page_title": "Backup & Disaster Recovery", "page_obj": page_obj,
        "backupjobs": page_obj.object_list,
        "type_choices": BackupJob.BACKUP_TYPE_CHOICES,
        "status_choices": BackupJob.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def backupjob_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = BackupJobForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, f"Backup job {obj.number} created.")
        return redirect("administration:backupjob_list")
    return render(request, "administration/backupjob_form.html",
                  {"form": form, "page_title": "Add Backup Job", "mode": "create"})


@login_required
def backupjob_detail(request, pk):
    obj = get_object_or_404(BackupJob, pk=pk, tenant=request.tenant)
    return render(request, "administration/backupjob_detail.html",
                  {"obj": obj, "page_title": obj.number})


@tenant_admin_required
def backupjob_edit(request, pk):
    obj = get_object_or_404(BackupJob, pk=pk, tenant=request.tenant)
    form = BackupJobForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Backup job updated.")
        return redirect("administration:backupjob_detail", pk=obj.pk)
    return render(request, "administration/backupjob_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.number}", "mode": "edit"})


@tenant_admin_required
def backupjob_delete(request, pk):
    obj = get_object_or_404(BackupJob, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.number
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Backup job {label} deleted.")
    return redirect("administration:backupjob_list")


# ============================================================ system health metrics
@login_required
def systemhealthmetric_list(request):
    qs = SystemHealthMetric.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(metric_name__icontains=q))
    category = request.GET.get("category", "")
    if category:
        qs = qs.filter(category=category)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "administration/systemhealthmetric_list.html", {
        "page_title": "System Health & Performance", "page_obj": page_obj,
        "systemhealthmetrics": page_obj.object_list,
        "category_choices": SystemHealthMetric.CATEGORY_CHOICES,
        "status_choices": SystemHealthMetric.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def systemhealthmetric_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = SystemHealthMetricForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Health metric recorded.")
        return redirect("administration:systemhealthmetric_list")
    return render(request, "administration/systemhealthmetric_form.html",
                  {"form": form, "page_title": "Add Health Metric", "mode": "create"})


@login_required
def systemhealthmetric_detail(request, pk):
    obj = get_object_or_404(SystemHealthMetric, pk=pk, tenant=request.tenant)
    return render(request, "administration/systemhealthmetric_detail.html",
                  {"obj": obj, "page_title": obj.metric_name})


@tenant_admin_required
def systemhealthmetric_edit(request, pk):
    obj = get_object_or_404(SystemHealthMetric, pk=pk, tenant=request.tenant)
    form = SystemHealthMetricForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Health metric updated.")
        return redirect("administration:systemhealthmetric_detail", pk=obj.pk)
    return render(request, "administration/systemhealthmetric_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.metric_name}", "mode": "edit"})


@tenant_admin_required
def systemhealthmetric_delete(request, pk):
    obj = get_object_or_404(SystemHealthMetric, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.metric_name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Health metric “{label}” deleted.")
    return redirect("administration:systemhealthmetric_list")
