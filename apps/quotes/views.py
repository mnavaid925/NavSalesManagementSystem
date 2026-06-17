from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.decorators import tenant_admin_required
from apps.core.utils import log_action

from .forms import (
    PricingRuleForm, ProposalForm, QuoteForm, QuoteLineItemForm, QuoteVersionForm,
)
from .models import PricingRule, Proposal, Quote, QuoteLineItem, QuoteVersion


def _no_tenant_redirect(request):
    messages.info(request, "Switch to a tenant workspace to manage this — the superuser has no tenant.")
    return redirect("dashboard:index")


def _page(request, qs, per_page=12):
    paginator = Paginator(qs, per_page)
    return paginator, paginator.get_page(request.GET.get("page"))


# ============================================================ quotes
@login_required
def quote_list(request):
    qs = Quote.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(title__icontains=q)
            | Q(account_name__icontains=q) | Q(contact_name__icontains=q)
        )
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    currency = request.GET.get("currency", "")
    if currency:
        qs = qs.filter(currency=currency)
    paginator, page_obj = _page(request, qs)
    return render(request, "quotes/quote_list.html", {
        "page_title": "Quote Configuration (CPQ)", "page_obj": page_obj, "quotes": page_obj.object_list,
        "status_choices": Quote.STATUS_CHOICES, "currency_choices": Quote.CURRENCY_CHOICES,
        "total": paginator.count,
    })


@login_required
def quote_detail(request, pk):
    obj = get_object_or_404(Quote, pk=pk, tenant=request.tenant)
    line_items = obj.line_items.all()
    versions = obj.versions.all()
    proposals = obj.proposals.all()
    return render(request, "quotes/quote_detail.html", {
        "obj": obj, "line_items": line_items, "versions": versions,
        "proposals": proposals, "page_title": str(obj),
    })


@tenant_admin_required
def quote_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = QuoteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, f"Quote {obj.number} created.")
        return redirect("quotes:quote_detail", pk=obj.pk)
    return render(request, "quotes/quote_form.html",
                  {"form": form, "page_title": "Add Quote", "mode": "create"})


@tenant_admin_required
def quote_edit(request, pk):
    obj = get_object_or_404(Quote, pk=pk, tenant=request.tenant)
    form = QuoteForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Quote updated.")
        return redirect("quotes:quote_detail", pk=obj.pk)
    return render(request, "quotes/quote_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.number}", "mode": "edit"})


@tenant_admin_required
def quote_delete(request, pk):
    obj = get_object_or_404(Quote, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.number
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Quote {label} deleted.")
    return redirect("quotes:quote_list")


# ============================================================ quote line items
@login_required
def quotelineitem_list(request):
    qs = QuoteLineItem.objects.filter(tenant=request.tenant).select_related("quote")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(product_name__icontains=q) | Q(sku__icontains=q) | Q(description__icontains=q)
        )
    unit = request.GET.get("unit", "")
    if unit:
        qs = qs.filter(unit=unit)
    quote = request.GET.get("quote", "")
    if quote:
        qs = qs.filter(quote_id=quote)
    paginator, page_obj = _page(request, qs)
    return render(request, "quotes/quotelineitem_list.html", {
        "page_title": "CPQ Line Items", "page_obj": page_obj, "line_items": page_obj.object_list,
        "unit_choices": QuoteLineItem.UNIT_CHOICES,
        "quotes": Quote.objects.filter(tenant=request.tenant),
        "total": paginator.count,
    })


@login_required
def quotelineitem_detail(request, pk):
    obj = get_object_or_404(QuoteLineItem.objects.select_related("quote"), pk=pk, tenant=request.tenant)
    return render(request, "quotes/quotelineitem_detail.html", {"obj": obj, "page_title": str(obj)})


@tenant_admin_required
def quotelineitem_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = QuoteLineItemForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Line item added.")
        return redirect("quotes:quotelineitem_detail", pk=obj.pk)
    return render(request, "quotes/quotelineitem_form.html",
                  {"form": form, "page_title": "Add Line Item", "mode": "create"})


@tenant_admin_required
def quotelineitem_edit(request, pk):
    obj = get_object_or_404(QuoteLineItem, pk=pk, tenant=request.tenant)
    form = QuoteLineItemForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Line item updated.")
        return redirect("quotes:quotelineitem_detail", pk=obj.pk)
    return render(request, "quotes/quotelineitem_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.product_name}", "mode": "edit"})


@tenant_admin_required
def quotelineitem_delete(request, pk):
    obj = get_object_or_404(QuoteLineItem, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, "Line item deleted.")
    return redirect("quotes:quotelineitem_list")


# ============================================================ pricing rules
@login_required
def pricingrule_list(request):
    qs = PricingRule.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
    rule_type = request.GET.get("rule_type", "")
    if rule_type:
        qs = qs.filter(rule_type=rule_type)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    approval_level = request.GET.get("approval_level", "")
    if approval_level:
        qs = qs.filter(approval_level=approval_level)
    paginator, page_obj = _page(request, qs)
    return render(request, "quotes/pricingrule_list.html", {
        "page_title": "Pricing & Discount Approval", "page_obj": page_obj, "rules": page_obj.object_list,
        "rule_choices": PricingRule.RULE_CHOICES, "status_choices": PricingRule.STATUS_CHOICES,
        "approval_choices": PricingRule.APPROVAL_CHOICES, "total": paginator.count,
    })


@login_required
def pricingrule_detail(request, pk):
    obj = get_object_or_404(PricingRule, pk=pk, tenant=request.tenant)
    return render(request, "quotes/pricingrule_detail.html", {"obj": obj, "page_title": obj.name})


@tenant_admin_required
def pricingrule_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = PricingRuleForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Pricing rule created.")
        return redirect("quotes:pricingrule_detail", pk=obj.pk)
    return render(request, "quotes/pricingrule_form.html",
                  {"form": form, "page_title": "Add Pricing Rule", "mode": "create"})


@tenant_admin_required
def pricingrule_edit(request, pk):
    obj = get_object_or_404(PricingRule, pk=pk, tenant=request.tenant)
    form = PricingRuleForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Pricing rule updated.")
        return redirect("quotes:pricingrule_detail", pk=obj.pk)
    return render(request, "quotes/pricingrule_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.name}", "mode": "edit"})


@tenant_admin_required
def pricingrule_delete(request, pk):
    obj = get_object_or_404(PricingRule, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Pricing rule “{label}” deleted.")
    return redirect("quotes:pricingrule_list")


# ============================================================ proposals
@login_required
def proposal_list(request):
    qs = Proposal.objects.filter(tenant=request.tenant).select_related("quote")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(title__icontains=q) | Q(prepared_by__icontains=q) | Q(executive_summary__icontains=q)
        )
    template = request.GET.get("template", "")
    if template:
        qs = qs.filter(template=template)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    quote = request.GET.get("quote", "")
    if quote:
        qs = qs.filter(quote_id=quote)
    paginator, page_obj = _page(request, qs)
    return render(request, "quotes/proposal_list.html", {
        "page_title": "Proposal Generation & Templating", "page_obj": page_obj, "proposals": page_obj.object_list,
        "template_choices": Proposal.TEMPLATE_CHOICES, "status_choices": Proposal.STATUS_CHOICES,
        "quotes": Quote.objects.filter(tenant=request.tenant), "total": paginator.count,
    })


@login_required
def proposal_detail(request, pk):
    obj = get_object_or_404(Proposal.objects.select_related("quote"), pk=pk, tenant=request.tenant)
    return render(request, "quotes/proposal_detail.html", {"obj": obj, "page_title": obj.title})


@tenant_admin_required
def proposal_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = ProposalForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Proposal created.")
        return redirect("quotes:proposal_detail", pk=obj.pk)
    return render(request, "quotes/proposal_form.html",
                  {"form": form, "page_title": "Add Proposal", "mode": "create"})


@tenant_admin_required
def proposal_edit(request, pk):
    obj = get_object_or_404(Proposal, pk=pk, tenant=request.tenant)
    form = ProposalForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Proposal updated.")
        return redirect("quotes:proposal_detail", pk=obj.pk)
    return render(request, "quotes/proposal_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.title}", "mode": "edit"})


@tenant_admin_required
def proposal_delete(request, pk):
    obj = get_object_or_404(Proposal, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.title
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Proposal “{label}” deleted.")
    return redirect("quotes:proposal_list")


# ============================================================ quote versions
@login_required
def quoteversion_list(request):
    qs = QuoteVersion.objects.filter(tenant=request.tenant).select_related("quote")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(change_summary__icontains=q) | Q(snapshot_notes__icontains=q))
    change_type = request.GET.get("change_type", "")
    if change_type:
        qs = qs.filter(change_type=change_type)
    quote = request.GET.get("quote", "")
    if quote:
        qs = qs.filter(quote_id=quote)
    paginator, page_obj = _page(request, qs)
    return render(request, "quotes/quoteversion_list.html", {
        "page_title": "Quote Versioning & Comparison", "page_obj": page_obj, "versions": page_obj.object_list,
        "change_choices": QuoteVersion.CHANGE_CHOICES,
        "quotes": Quote.objects.filter(tenant=request.tenant), "total": paginator.count,
    })


@login_required
def quoteversion_detail(request, pk):
    obj = get_object_or_404(QuoteVersion.objects.select_related("quote"), pk=pk, tenant=request.tenant)
    return render(request, "quotes/quoteversion_detail.html", {"obj": obj, "page_title": str(obj)})


@tenant_admin_required
def quoteversion_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = QuoteVersionForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Quote version recorded.")
        return redirect("quotes:quoteversion_detail", pk=obj.pk)
    return render(request, "quotes/quoteversion_form.html",
                  {"form": form, "page_title": "Add Quote Version", "mode": "create"})


@tenant_admin_required
def quoteversion_edit(request, pk):
    obj = get_object_or_404(QuoteVersion, pk=pk, tenant=request.tenant)
    form = QuoteVersionForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Quote version updated.")
        return redirect("quotes:quoteversion_detail", pk=obj.pk)
    return render(request, "quotes/quoteversion_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit v{obj.version_number}", "mode": "edit"})


@tenant_admin_required
def quoteversion_delete(request, pk):
    obj = get_object_or_404(QuoteVersion, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, "Quote version deleted.")
    return redirect("quotes:quoteversion_list")
