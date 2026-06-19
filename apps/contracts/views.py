from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.decorators import tenant_admin_required
from apps.core.utils import log_action

from .forms import (
    ContractClauseForm, ContractForm, ContractObligationForm,
    RenewalScheduleForm, UsageRecordForm,
)
from .models import (
    Contract, ContractClause, ContractObligation, RenewalSchedule, UsageRecord,
)


def _no_tenant_redirect(request):
    messages.info(request, "Switch to a tenant workspace to manage this — the superuser has no tenant.")
    return redirect("dashboard:index")


def _page(request, qs, per_page=12):
    paginator = Paginator(qs, per_page)
    return paginator, paginator.get_page(request.GET.get("page"))


# ============================================================ contracts
@login_required
def contract_list(request):
    qs = Contract.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(title__icontains=q) | Q(account_name__icontains=q))
    contract_type = request.GET.get("contract_type", "")
    if contract_type:
        qs = qs.filter(contract_type=contract_type)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "contracts/contract_list.html", {
        "page_title": "Subscription Lifecycle", "page_obj": page_obj, "contracts": page_obj.object_list,
        "type_choices": Contract.TYPE_CHOICES, "status_choices": Contract.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def contract_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = ContractForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, f"Contract {obj.number} created.")
        return redirect("contracts:contract_list")
    return render(request, "contracts/contract_form.html",
                  {"form": form, "page_title": "Add Contract", "mode": "create"})


@login_required
def contract_detail(request, pk):
    obj = get_object_or_404(Contract, pk=pk, tenant=request.tenant)
    clauses = obj.clauses.filter(tenant=request.tenant)[:20]
    obligations = obj.obligations.filter(tenant=request.tenant)[:20]
    return render(request, "contracts/contract_detail.html",
                  {"obj": obj, "clauses": clauses, "obligations": obligations, "page_title": obj.number})


@tenant_admin_required
def contract_edit(request, pk):
    obj = get_object_or_404(Contract, pk=pk, tenant=request.tenant)
    form = ContractForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Contract updated.")
        return redirect("contracts:contract_detail", pk=obj.pk)
    return render(request, "contracts/contract_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.number}", "mode": "edit"})


@tenant_admin_required
def contract_delete(request, pk):
    obj = get_object_or_404(Contract, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.number
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Contract {label} deleted.")
    return redirect("contracts:contract_list")


# ============================================================ contract clauses
@login_required
def contractclause_list(request):
    qs = ContractClause.objects.filter(tenant=request.tenant).select_related("contract")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(body__icontains=q))
    clause_type = request.GET.get("clause_type", "")
    if clause_type:
        qs = qs.filter(clause_type=clause_type)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    contract = request.GET.get("contract", "")
    if contract.isdigit():
        qs = qs.filter(contract_id=contract)
    paginator, page_obj = _page(request, qs)
    return render(request, "contracts/contractclause_list.html", {
        "page_title": "Contract Authoring & Redlining", "page_obj": page_obj,
        "contractclauses": page_obj.object_list,
        "type_choices": ContractClause.CLAUSE_TYPE_CHOICES,
        "status_choices": ContractClause.STATUS_CHOICES,
        "contracts": Contract.objects.filter(tenant=request.tenant),
        "total": paginator.count,
    })


@tenant_admin_required
def contractclause_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = ContractClauseForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Clause created.")
        return redirect("contracts:contractclause_list")
    return render(request, "contracts/contractclause_form.html",
                  {"form": form, "page_title": "Add Clause", "mode": "create"})


@login_required
def contractclause_detail(request, pk):
    obj = get_object_or_404(
        ContractClause.objects.select_related("contract"), pk=pk, tenant=request.tenant)
    return render(request, "contracts/contractclause_detail.html",
                  {"obj": obj, "page_title": obj.title})


@tenant_admin_required
def contractclause_edit(request, pk):
    obj = get_object_or_404(ContractClause, pk=pk, tenant=request.tenant)
    form = ContractClauseForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Clause updated.")
        return redirect("contracts:contractclause_detail", pk=obj.pk)
    return render(request, "contracts/contractclause_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.title}", "mode": "edit"})


@tenant_admin_required
def contractclause_delete(request, pk):
    obj = get_object_or_404(ContractClause, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.title
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Clause “{label}” deleted.")
    return redirect("contracts:contractclause_list")


# ============================================================ renewal schedules
@login_required
def renewalschedule_list(request):
    qs = RenewalSchedule.objects.filter(tenant=request.tenant).select_related("contract")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(account_name__icontains=q) | Q(notes__icontains=q))
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    contract = request.GET.get("contract", "")
    if contract.isdigit():
        qs = qs.filter(contract_id=contract)
    paginator, page_obj = _page(request, qs)
    return render(request, "contracts/renewalschedule_list.html", {
        "page_title": "Renewal Automation", "page_obj": page_obj,
        "renewalschedules": page_obj.object_list,
        "status_choices": RenewalSchedule.STATUS_CHOICES,
        "contracts": Contract.objects.filter(tenant=request.tenant),
        "total": paginator.count,
    })


@tenant_admin_required
def renewalschedule_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = RenewalScheduleForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Renewal scheduled.")
        return redirect("contracts:renewalschedule_list")
    return render(request, "contracts/renewalschedule_form.html",
                  {"form": form, "page_title": "Add Renewal", "mode": "create"})


@login_required
def renewalschedule_detail(request, pk):
    obj = get_object_or_404(
        RenewalSchedule.objects.select_related("contract"), pk=pk, tenant=request.tenant)
    return render(request, "contracts/renewalschedule_detail.html",
                  {"obj": obj, "page_title": obj.account_name})


@tenant_admin_required
def renewalschedule_edit(request, pk):
    obj = get_object_or_404(RenewalSchedule, pk=pk, tenant=request.tenant)
    form = RenewalScheduleForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Renewal updated.")
        return redirect("contracts:renewalschedule_detail", pk=obj.pk)
    return render(request, "contracts/renewalschedule_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.account_name}", "mode": "edit"})


@tenant_admin_required
def renewalschedule_delete(request, pk):
    obj = get_object_or_404(RenewalSchedule, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.account_name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Renewal for “{label}” deleted.")
    return redirect("contracts:renewalschedule_list")


# ============================================================ usage records
@login_required
def usagerecord_list(request):
    qs = UsageRecord.objects.filter(tenant=request.tenant).select_related("contract")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(account_name__icontains=q) | Q(metric_name__icontains=q))
    unit = request.GET.get("unit", "")
    if unit:
        qs = qs.filter(unit=unit)
    contract = request.GET.get("contract", "")
    if contract.isdigit():
        qs = qs.filter(contract_id=contract)
    paginator, page_obj = _page(request, qs)
    return render(request, "contracts/usagerecord_list.html", {
        "page_title": "Usage-Based Billing", "page_obj": page_obj,
        "usagerecords": page_obj.object_list,
        "unit_choices": UsageRecord.UNIT_CHOICES,
        "contracts": Contract.objects.filter(tenant=request.tenant),
        "total": paginator.count,
    })


@tenant_admin_required
def usagerecord_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = UsageRecordForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Usage record created.")
        return redirect("contracts:usagerecord_list")
    return render(request, "contracts/usagerecord_form.html",
                  {"form": form, "page_title": "Add Usage Record", "mode": "create"})


@login_required
def usagerecord_detail(request, pk):
    obj = get_object_or_404(
        UsageRecord.objects.select_related("contract"), pk=pk, tenant=request.tenant)
    return render(request, "contracts/usagerecord_detail.html",
                  {"obj": obj, "page_title": str(obj)})


@tenant_admin_required
def usagerecord_edit(request, pk):
    obj = get_object_or_404(UsageRecord, pk=pk, tenant=request.tenant)
    form = UsageRecordForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Usage record updated.")
        return redirect("contracts:usagerecord_detail", pk=obj.pk)
    return render(request, "contracts/usagerecord_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj}", "mode": "edit"})


@tenant_admin_required
def usagerecord_delete(request, pk):
    obj = get_object_or_404(UsageRecord, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = str(obj)
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Usage record “{label}” deleted.")
    return redirect("contracts:usagerecord_list")


# ============================================================ contract obligations
@login_required
def contractobligation_list(request):
    qs = ContractObligation.objects.filter(tenant=request.tenant).select_related("contract")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(owner__icontains=q))
    obligation_type = request.GET.get("obligation_type", "")
    if obligation_type:
        qs = qs.filter(obligation_type=obligation_type)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    contract = request.GET.get("contract", "")
    if contract.isdigit():
        qs = qs.filter(contract_id=contract)
    paginator, page_obj = _page(request, qs)
    return render(request, "contracts/contractobligation_list.html", {
        "page_title": "Contract Compliance & Obligations", "page_obj": page_obj,
        "contractobligations": page_obj.object_list,
        "type_choices": ContractObligation.OBLIGATION_TYPE_CHOICES,
        "status_choices": ContractObligation.STATUS_CHOICES,
        "contracts": Contract.objects.filter(tenant=request.tenant),
        "total": paginator.count,
    })


@tenant_admin_required
def contractobligation_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = ContractObligationForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Obligation created.")
        return redirect("contracts:contractobligation_list")
    return render(request, "contracts/contractobligation_form.html",
                  {"form": form, "page_title": "Add Obligation", "mode": "create"})


@login_required
def contractobligation_detail(request, pk):
    obj = get_object_or_404(
        ContractObligation.objects.select_related("contract"), pk=pk, tenant=request.tenant)
    return render(request, "contracts/contractobligation_detail.html",
                  {"obj": obj, "page_title": obj.title})


@tenant_admin_required
def contractobligation_edit(request, pk):
    obj = get_object_or_404(ContractObligation, pk=pk, tenant=request.tenant)
    form = ContractObligationForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Obligation updated.")
        return redirect("contracts:contractobligation_detail", pk=obj.pk)
    return render(request, "contracts/contractobligation_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.title}", "mode": "edit"})


@tenant_admin_required
def contractobligation_delete(request, pk):
    obj = get_object_or_404(ContractObligation, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.title
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Obligation “{label}” deleted.")
    return redirect("contracts:contractobligation_list")
