from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.decorators import tenant_admin_required
from apps.core.utils import log_action

from .forms import (
    AccountForm, AccountPlanForm, AccountTierForm, ContactForm, RelationshipMapForm,
)
from .models import Account, AccountPlan, AccountTier, Contact, RelationshipMap


def _no_tenant_redirect(request):
    messages.info(request, "Switch to a tenant workspace to manage this — the superuser has no tenant.")
    return redirect("dashboard:index")


def _page(request, qs, per_page=12):
    paginator = Paginator(qs, per_page)
    return paginator, paginator.get_page(request.GET.get("page"))


# ============================================================ account tiers
@login_required
def accounttier_list(request):
    qs = AccountTier.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
    segment = request.GET.get("segment", "")
    if segment:
        qs = qs.filter(segment=segment)
    active = request.GET.get("active", "")
    if active == "active":
        qs = qs.filter(is_active=True)
    elif active == "inactive":
        qs = qs.filter(is_active=False)
    paginator, page_obj = _page(request, qs)
    return render(request, "crm/accounttier_list.html", {
        "page_title": "Account Segmentation & Tiering", "page_obj": page_obj,
        "tiers": page_obj.object_list, "segment_choices": AccountTier.SEGMENT_CHOICES,
        "total": paginator.count,
    })


@login_required
def accounttier_detail(request, pk):
    obj = get_object_or_404(AccountTier, pk=pk, tenant=request.tenant)
    accounts = obj.accounts.filter(tenant=request.tenant)[:20]
    return render(request, "crm/accounttier_detail.html",
                  {"obj": obj, "accounts": accounts, "page_title": obj.name})


@tenant_admin_required
def accounttier_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = AccountTierForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Tier created.")
        return redirect("crm:accounttier_list")
    return render(request, "crm/accounttier_form.html",
                  {"form": form, "page_title": "Add Tier", "mode": "create"})


@tenant_admin_required
def accounttier_edit(request, pk):
    obj = get_object_or_404(AccountTier, pk=pk, tenant=request.tenant)
    form = AccountTierForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Tier updated.")
        return redirect("crm:accounttier_detail", pk=obj.pk)
    return render(request, "crm/accounttier_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.name}", "mode": "edit"})


@tenant_admin_required
def accounttier_delete(request, pk):
    obj = get_object_or_404(AccountTier, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Tier “{label}” deleted.")
    return redirect("crm:accounttier_list")


# ============================================================ accounts
@login_required
def account_list(request):
    qs = Account.objects.filter(tenant=request.tenant).select_related("parent", "tier")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(name__icontains=q) | Q(number__icontains=q)
            | Q(industry__icontains=q) | Q(billing_city__icontains=q)
        )
    account_type = request.GET.get("account_type", "")
    if account_type:
        qs = qs.filter(account_type=account_type)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    tier = request.GET.get("tier", "")
    if tier:
        qs = qs.filter(tier_id=tier)
    paginator, page_obj = _page(request, qs)
    return render(request, "crm/account_list.html", {
        "page_title": "Account Hierarchy & Parent-Child", "page_obj": page_obj,
        "accounts": page_obj.object_list, "type_choices": Account.TYPE_CHOICES,
        "status_choices": Account.STATUS_CHOICES,
        "tiers": AccountTier.objects.filter(tenant=request.tenant),
        "total": paginator.count,
    })


@login_required
def account_detail(request, pk):
    obj = get_object_or_404(
        Account.objects.select_related("parent", "tier"), pk=pk, tenant=request.tenant)
    children = obj.children.filter(tenant=request.tenant)
    contacts = obj.contacts.filter(tenant=request.tenant)[:20]
    plans = obj.account_plans.filter(tenant=request.tenant)[:20]
    return render(request, "crm/account_detail.html", {
        "obj": obj, "children": children, "contacts": contacts,
        "plans": plans, "page_title": obj.name,
    })


@tenant_admin_required
def account_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = AccountForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, f"Account {obj.number} created.")
        return redirect("crm:account_list")
    return render(request, "crm/account_form.html",
                  {"form": form, "page_title": "Add Account", "mode": "create"})


@tenant_admin_required
def account_edit(request, pk):
    obj = get_object_or_404(Account, pk=pk, tenant=request.tenant)
    form = AccountForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Account updated.")
        return redirect("crm:account_detail", pk=obj.pk)
    return render(request, "crm/account_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.name}", "mode": "edit"})


@tenant_admin_required
def account_delete(request, pk):
    obj = get_object_or_404(Account, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Account “{label}” deleted.")
    return redirect("crm:account_list")


# ============================================================ contacts
@login_required
def contact_list(request):
    qs = Contact.objects.filter(tenant=request.tenant).select_related("account")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q)
            | Q(email__icontains=q) | Q(title__icontains=q)
        )
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    enrichment = request.GET.get("enrichment_status", "")
    if enrichment:
        qs = qs.filter(enrichment_status=enrichment)
    account = request.GET.get("account", "")
    if account:
        qs = qs.filter(account_id=account)
    paginator, page_obj = _page(request, qs)
    return render(request, "crm/contact_list.html", {
        "page_title": "Contact Profiles & Enrichment", "page_obj": page_obj,
        "contacts": page_obj.object_list, "status_choices": Contact.STATUS_CHOICES,
        "enrichment_choices": Contact.ENRICH_CHOICES,
        "accounts": Account.objects.filter(tenant=request.tenant),
        "total": paginator.count,
    })


@login_required
def contact_detail(request, pk):
    obj = get_object_or_404(Contact.objects.select_related("account"), pk=pk, tenant=request.tenant)
    relationships = obj.relationships_from.filter(tenant=request.tenant).select_related("to_contact")[:20]
    return render(request, "crm/contact_detail.html",
                  {"obj": obj, "relationships": relationships, "page_title": obj.full_name})


@tenant_admin_required
def contact_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = ContactForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Contact added.")
        return redirect("crm:contact_list")
    return render(request, "crm/contact_form.html",
                  {"form": form, "page_title": "Add Contact", "mode": "create"})


@tenant_admin_required
def contact_edit(request, pk):
    obj = get_object_or_404(Contact, pk=pk, tenant=request.tenant)
    form = ContactForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Contact updated.")
        return redirect("crm:contact_detail", pk=obj.pk)
    return render(request, "crm/contact_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.full_name}", "mode": "edit"})


@tenant_admin_required
def contact_delete(request, pk):
    obj = get_object_or_404(Contact, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.full_name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Contact “{label}” deleted.")
    return redirect("crm:contact_list")


# ============================================================ relationship maps
@login_required
def relationshipmap_list(request):
    qs = RelationshipMap.objects.filter(tenant=request.tenant).select_related(
        "account", "from_contact", "to_contact")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(from_contact__first_name__icontains=q) | Q(from_contact__last_name__icontains=q)
            | Q(to_contact__first_name__icontains=q) | Q(to_contact__last_name__icontains=q)
            | Q(notes__icontains=q)
        )
    relationship_type = request.GET.get("relationship_type", "")
    if relationship_type:
        qs = qs.filter(relationship_type=relationship_type)
    strength = request.GET.get("strength", "")
    if strength:
        qs = qs.filter(strength=strength)
    account = request.GET.get("account", "")
    if account:
        qs = qs.filter(account_id=account)
    paginator, page_obj = _page(request, qs)
    return render(request, "crm/relationshipmap_list.html", {
        "page_title": "Relationship Mapping", "page_obj": page_obj,
        "relationships": page_obj.object_list, "type_choices": RelationshipMap.TYPE_CHOICES,
        "strength_choices": RelationshipMap.STRENGTH_CHOICES,
        "accounts": Account.objects.filter(tenant=request.tenant),
        "total": paginator.count,
    })


@login_required
def relationshipmap_detail(request, pk):
    obj = get_object_or_404(
        RelationshipMap.objects.select_related("account", "from_contact", "to_contact"),
        pk=pk, tenant=request.tenant)
    return render(request, "crm/relationshipmap_detail.html", {"obj": obj, "page_title": str(obj)})


@tenant_admin_required
def relationshipmap_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = RelationshipMapForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Relationship mapped.")
        return redirect("crm:relationshipmap_list")
    return render(request, "crm/relationshipmap_form.html",
                  {"form": form, "page_title": "Add Relationship", "mode": "create"})


@tenant_admin_required
def relationshipmap_edit(request, pk):
    obj = get_object_or_404(RelationshipMap, pk=pk, tenant=request.tenant)
    form = RelationshipMapForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Relationship updated.")
        return redirect("crm:relationshipmap_detail", pk=obj.pk)
    return render(request, "crm/relationshipmap_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj}", "mode": "edit"})


@tenant_admin_required
def relationshipmap_delete(request, pk):
    obj = get_object_or_404(RelationshipMap, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, "Relationship deleted.")
    return redirect("crm:relationshipmap_list")


# ============================================================ account plans
@login_required
def accountplan_list(request):
    qs = AccountPlan.objects.filter(tenant=request.tenant).select_related("account")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(title__icontains=q) | Q(number__icontains=q)
            | Q(objective__icontains=q) | Q(account__name__icontains=q)
        )
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    priority = request.GET.get("priority", "")
    if priority:
        qs = qs.filter(priority=priority)
    account = request.GET.get("account", "")
    if account:
        qs = qs.filter(account_id=account)
    paginator, page_obj = _page(request, qs)
    return render(request, "crm/accountplan_list.html", {
        "page_title": "Account Plans & Growth Strategies", "page_obj": page_obj,
        "plans": page_obj.object_list, "status_choices": AccountPlan.STATUS_CHOICES,
        "priority_choices": AccountPlan.PRIORITY_CHOICES,
        "accounts": Account.objects.filter(tenant=request.tenant),
        "total": paginator.count,
    })


@login_required
def accountplan_detail(request, pk):
    obj = get_object_or_404(AccountPlan.objects.select_related("account"), pk=pk, tenant=request.tenant)
    return render(request, "crm/accountplan_detail.html", {"obj": obj, "page_title": obj.title})


@tenant_admin_required
def accountplan_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = AccountPlanForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, f"Plan {obj.number} created.")
        return redirect("crm:accountplan_list")
    return render(request, "crm/accountplan_form.html",
                  {"form": form, "page_title": "Add Account Plan", "mode": "create"})


@tenant_admin_required
def accountplan_edit(request, pk):
    obj = get_object_or_404(AccountPlan, pk=pk, tenant=request.tenant)
    form = AccountPlanForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Plan updated.")
        return redirect("crm:accountplan_detail", pk=obj.pk)
    return render(request, "crm/accountplan_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.title}", "mode": "edit"})


@tenant_admin_required
def accountplan_delete(request, pk):
    obj = get_object_or_404(AccountPlan, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.number
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Plan {label} deleted.")
    return redirect("crm:accountplan_list")
