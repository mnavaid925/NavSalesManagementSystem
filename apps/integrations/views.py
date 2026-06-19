from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.decorators import tenant_admin_required
from apps.core.utils import log_action

from .forms import (
    ApiKeyForm, ConnectorForm, SyncJobForm, SyncLogForm, WebhookForm,
)
from .models import ApiKey, Connector, SyncJob, SyncLog, Webhook


def _no_tenant_redirect(request):
    messages.info(request, "Switch to a tenant workspace to manage this — the superuser has no tenant.")
    return redirect("dashboard:index")


def _page(request, qs, per_page=12):
    paginator = Paginator(qs, per_page)
    return paginator, paginator.get_page(request.GET.get("page"))


# ============================================================ connectors
@login_required
def connector_list(request):
    qs = Connector.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(provider__icontains=q))
    category = request.GET.get("category", "")
    if category:
        qs = qs.filter(category=category)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "integrations/connector_list.html", {
        "page_title": "ERP Integration", "page_obj": page_obj, "connectors": page_obj.object_list,
        "category_choices": Connector.CATEGORY_CHOICES, "status_choices": Connector.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def connector_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = ConnectorForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Connector created.")
        return redirect("integrations:connector_list")
    return render(request, "integrations/connector_form.html",
                  {"form": form, "page_title": "Add Connector", "mode": "create"})


@login_required
def connector_detail(request, pk):
    obj = get_object_or_404(Connector, pk=pk, tenant=request.tenant)
    sync_jobs = obj.sync_jobs.filter(tenant=request.tenant)[:20]
    return render(request, "integrations/connector_detail.html",
                  {"obj": obj, "sync_jobs": sync_jobs, "page_title": obj.name})


@tenant_admin_required
def connector_edit(request, pk):
    obj = get_object_or_404(Connector, pk=pk, tenant=request.tenant)
    form = ConnectorForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Connector updated.")
        return redirect("integrations:connector_detail", pk=obj.pk)
    return render(request, "integrations/connector_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.name}", "mode": "edit"})


@tenant_admin_required
def connector_delete(request, pk):
    obj = get_object_or_404(Connector, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Connector “{label}” deleted.")
    return redirect("integrations:connector_list")


# ============================================================ sync jobs
@login_required
def syncjob_list(request):
    qs = SyncJob.objects.filter(tenant=request.tenant).select_related("connector")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(name__icontains=q))
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    connector = request.GET.get("connector", "")
    if connector.isdigit():
        qs = qs.filter(connector_id=connector)
    paginator, page_obj = _page(request, qs)
    return render(request, "integrations/syncjob_list.html", {
        "page_title": "Marketing Automation", "page_obj": page_obj, "syncjobs": page_obj.object_list,
        "status_choices": SyncJob.STATUS_CHOICES,
        "connectors": Connector.objects.filter(tenant=request.tenant),
        "total": paginator.count,
    })


@tenant_admin_required
def syncjob_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = SyncJobForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, f"Sync job {obj.number} created.")
        return redirect("integrations:syncjob_list")
    return render(request, "integrations/syncjob_form.html",
                  {"form": form, "page_title": "Add Sync Job", "mode": "create"})


@login_required
def syncjob_detail(request, pk):
    obj = get_object_or_404(SyncJob.objects.select_related("connector"), pk=pk, tenant=request.tenant)
    logs = obj.logs.filter(tenant=request.tenant)[:20]
    return render(request, "integrations/syncjob_detail.html",
                  {"obj": obj, "logs": logs, "page_title": obj.number})


@tenant_admin_required
def syncjob_edit(request, pk):
    obj = get_object_or_404(SyncJob, pk=pk, tenant=request.tenant)
    form = SyncJobForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Sync job updated.")
        return redirect("integrations:syncjob_detail", pk=obj.pk)
    return render(request, "integrations/syncjob_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.number}", "mode": "edit"})


@tenant_admin_required
def syncjob_delete(request, pk):
    obj = get_object_or_404(SyncJob, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.number
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Sync job {label} deleted.")
    return redirect("integrations:syncjob_list")


# ============================================================ sync logs
@login_required
def synclog_list(request):
    qs = SyncLog.objects.filter(tenant=request.tenant).select_related("job")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(message__icontains=q))
    level = request.GET.get("level", "")
    if level:
        qs = qs.filter(level=level)
    job = request.GET.get("job", "")
    if job.isdigit():
        qs = qs.filter(job_id=job)
    paginator, page_obj = _page(request, qs)
    return render(request, "integrations/synclog_list.html", {
        "page_title": "Communication Platforms", "page_obj": page_obj, "synclogs": page_obj.object_list,
        "level_choices": SyncLog.LEVEL_CHOICES,
        "jobs": SyncJob.objects.filter(tenant=request.tenant),
        "total": paginator.count,
    })


@tenant_admin_required
def synclog_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = SyncLogForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Log entry recorded.")
        return redirect("integrations:synclog_list")
    return render(request, "integrations/synclog_form.html",
                  {"form": form, "page_title": "Add Log Entry", "mode": "create"})


@login_required
def synclog_detail(request, pk):
    obj = get_object_or_404(SyncLog.objects.select_related("job"), pk=pk, tenant=request.tenant)
    return render(request, "integrations/synclog_detail.html", {"obj": obj, "page_title": str(obj)})


@tenant_admin_required
def synclog_edit(request, pk):
    obj = get_object_or_404(SyncLog, pk=pk, tenant=request.tenant)
    form = SyncLogForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Log entry updated.")
        return redirect("integrations:synclog_detail", pk=obj.pk)
    return render(request, "integrations/synclog_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit log #{obj.pk}", "mode": "edit"})


@tenant_admin_required
def synclog_delete(request, pk):
    obj = get_object_or_404(SyncLog, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, "Log entry deleted.")
    return redirect("integrations:synclog_list")


# ============================================================ webhooks
@login_required
def webhook_list(request):
    qs = Webhook.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(target_url__icontains=q))
    event_type = request.GET.get("event_type", "")
    if event_type:
        qs = qs.filter(event_type=event_type)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "integrations/webhook_list.html", {
        "page_title": "Business Intelligence", "page_obj": page_obj, "webhooks": page_obj.object_list,
        "event_choices": Webhook.EVENT_CHOICES, "status_choices": Webhook.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def webhook_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = WebhookForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Webhook created.")
        return redirect("integrations:webhook_list")
    return render(request, "integrations/webhook_form.html",
                  {"form": form, "page_title": "Add Webhook", "mode": "create"})


@login_required
def webhook_detail(request, pk):
    obj = get_object_or_404(Webhook, pk=pk, tenant=request.tenant)
    return render(request, "integrations/webhook_detail.html", {"obj": obj, "page_title": obj.name})


@tenant_admin_required
def webhook_edit(request, pk):
    obj = get_object_or_404(Webhook, pk=pk, tenant=request.tenant)
    form = WebhookForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Webhook updated.")
        return redirect("integrations:webhook_detail", pk=obj.pk)
    return render(request, "integrations/webhook_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.name}", "mode": "edit"})


@tenant_admin_required
def webhook_delete(request, pk):
    obj = get_object_or_404(Webhook, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Webhook “{label}” deleted.")
    return redirect("integrations:webhook_list")


# ============================================================ api keys
@login_required
def apikey_list(request):
    qs = ApiKey.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(key_prefix__icontains=q) | Q(scopes__icontains=q))
    environment = request.GET.get("environment", "")
    if environment:
        qs = qs.filter(environment=environment)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "integrations/apikey_list.html", {
        "page_title": "E-Signature & Document", "page_obj": page_obj, "apikeys": page_obj.object_list,
        "environment_choices": ApiKey.ENVIRONMENT_CHOICES, "status_choices": ApiKey.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def apikey_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = ApiKeyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "API key generated.")
        return redirect("integrations:apikey_list")
    return render(request, "integrations/apikey_form.html",
                  {"form": form, "page_title": "Add API Key", "mode": "create"})


@login_required
def apikey_detail(request, pk):
    obj = get_object_or_404(ApiKey, pk=pk, tenant=request.tenant)
    return render(request, "integrations/apikey_detail.html", {"obj": obj, "page_title": obj.name})


@tenant_admin_required
def apikey_edit(request, pk):
    obj = get_object_or_404(ApiKey, pk=pk, tenant=request.tenant)
    form = ApiKeyForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "API key updated.")
        return redirect("integrations:apikey_detail", pk=obj.pk)
    return render(request, "integrations/apikey_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.name}", "mode": "edit"})


@tenant_admin_required
def apikey_delete(request, pk):
    obj = get_object_or_404(ApiKey, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"API key “{label}” deleted.")
    return redirect("integrations:apikey_list")
