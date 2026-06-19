from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.decorators import tenant_admin_required
from apps.core.utils import log_action

from .forms import (
    CustomFieldForm, LocalizationSettingForm, MethodologyConfigForm,
    PriceBookForm, ProductCatalogForm,
)
from .models import (
    CustomField, LocalizationSetting, MethodologyConfig, PriceBook, ProductCatalog,
)


def _no_tenant_redirect(request):
    messages.info(request, "Switch to a tenant workspace to manage this — the superuser has no tenant.")
    return redirect("dashboard:index")


def _page(request, qs, per_page=12):
    paginator = Paginator(qs, per_page)
    return paginator, paginator.get_page(request.GET.get("page"))


# ============================================================ product catalog
@login_required
def productcatalog_list(request):
    qs = ProductCatalog.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(sku__icontains=q) | Q(description__icontains=q))
    category = request.GET.get("category", "")
    if category:
        qs = qs.filter(category=category)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "masterdata/productcatalog_list.html", {
        "page_title": "Product Catalog & Pricing", "page_obj": page_obj,
        "productcatalogs": page_obj.object_list,
        "category_choices": ProductCatalog.CATEGORY_CHOICES,
        "status_choices": ProductCatalog.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def productcatalog_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = ProductCatalogForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Product created.")
        return redirect("masterdata:productcatalog_list")
    return render(request, "masterdata/productcatalog_form.html",
                  {"form": form, "page_title": "Add Product", "mode": "create"})


@login_required
def productcatalog_detail(request, pk):
    obj = get_object_or_404(ProductCatalog, pk=pk, tenant=request.tenant)
    return render(request, "masterdata/productcatalog_detail.html",
                  {"obj": obj, "page_title": obj.name})


@tenant_admin_required
def productcatalog_edit(request, pk):
    obj = get_object_or_404(ProductCatalog, pk=pk, tenant=request.tenant)
    form = ProductCatalogForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Product updated.")
        return redirect("masterdata:productcatalog_detail", pk=obj.pk)
    return render(request, "masterdata/productcatalog_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.name}", "mode": "edit"})


@tenant_admin_required
def productcatalog_delete(request, pk):
    obj = get_object_or_404(ProductCatalog, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Product “{label}” deleted.")
    return redirect("masterdata:productcatalog_list")


# ============================================================ custom fields
@login_required
def customfield_list(request):
    qs = CustomField.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(field_key__icontains=q))
    object_type = request.GET.get("object_type", "")
    if object_type:
        qs = qs.filter(object_type=object_type)
    field_type = request.GET.get("field_type", "")
    if field_type:
        qs = qs.filter(field_type=field_type)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "masterdata/customfield_list.html", {
        "page_title": "Custom Fields & Objects", "page_obj": page_obj,
        "customfields": page_obj.object_list,
        "object_type_choices": CustomField.OBJECT_TYPE_CHOICES,
        "field_type_choices": CustomField.FIELD_TYPE_CHOICES,
        "status_choices": CustomField.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def customfield_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = CustomFieldForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Custom field created.")
        return redirect("masterdata:customfield_list")
    return render(request, "masterdata/customfield_form.html",
                  {"form": form, "page_title": "Add Custom Field", "mode": "create"})


@login_required
def customfield_detail(request, pk):
    obj = get_object_or_404(CustomField, pk=pk, tenant=request.tenant)
    return render(request, "masterdata/customfield_detail.html",
                  {"obj": obj, "page_title": obj.name})


@tenant_admin_required
def customfield_edit(request, pk):
    obj = get_object_or_404(CustomField, pk=pk, tenant=request.tenant)
    form = CustomFieldForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Custom field updated.")
        return redirect("masterdata:customfield_detail", pk=obj.pk)
    return render(request, "masterdata/customfield_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.name}", "mode": "edit"})


@tenant_admin_required
def customfield_delete(request, pk):
    obj = get_object_or_404(CustomField, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Custom field “{label}” deleted.")
    return redirect("masterdata:customfield_list")


# ============================================================ methodology config
@login_required
def methodologyconfig_list(request):
    qs = MethodologyConfig.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
    methodology = request.GET.get("methodology", "")
    if methodology:
        qs = qs.filter(methodology=methodology)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "masterdata/methodologyconfig_list.html", {
        "page_title": "Sales Methodology Configuration", "page_obj": page_obj,
        "methodologyconfigs": page_obj.object_list,
        "methodology_choices": MethodologyConfig.METHODOLOGY_CHOICES,
        "status_choices": MethodologyConfig.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def methodologyconfig_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = MethodologyConfigForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Methodology configuration created.")
        return redirect("masterdata:methodologyconfig_list")
    return render(request, "masterdata/methodologyconfig_form.html",
                  {"form": form, "page_title": "Add Methodology Configuration", "mode": "create"})


@login_required
def methodologyconfig_detail(request, pk):
    obj = get_object_or_404(MethodologyConfig, pk=pk, tenant=request.tenant)
    return render(request, "masterdata/methodologyconfig_detail.html",
                  {"obj": obj, "page_title": obj.name})


@tenant_admin_required
def methodologyconfig_edit(request, pk):
    obj = get_object_or_404(MethodologyConfig, pk=pk, tenant=request.tenant)
    form = MethodologyConfigForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Methodology configuration updated.")
        return redirect("masterdata:methodologyconfig_detail", pk=obj.pk)
    return render(request, "masterdata/methodologyconfig_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.name}", "mode": "edit"})


@tenant_admin_required
def methodologyconfig_delete(request, pk):
    obj = get_object_or_404(MethodologyConfig, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Methodology configuration “{label}” deleted.")
    return redirect("masterdata:methodologyconfig_list")


# ============================================================ price books
@login_required
def pricebook_list(request):
    qs = PriceBook.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(region__icontains=q) | Q(description__icontains=q))
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "masterdata/pricebook_list.html", {
        "page_title": "Price Books", "page_obj": page_obj,
        "pricebooks": page_obj.object_list,
        "status_choices": PriceBook.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def pricebook_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = PriceBookForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Price book created.")
        return redirect("masterdata:pricebook_list")
    return render(request, "masterdata/pricebook_form.html",
                  {"form": form, "page_title": "Add Price Book", "mode": "create"})


@login_required
def pricebook_detail(request, pk):
    obj = get_object_or_404(PriceBook, pk=pk, tenant=request.tenant)
    return render(request, "masterdata/pricebook_detail.html",
                  {"obj": obj, "page_title": obj.name})


@tenant_admin_required
def pricebook_edit(request, pk):
    obj = get_object_or_404(PriceBook, pk=pk, tenant=request.tenant)
    form = PriceBookForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Price book updated.")
        return redirect("masterdata:pricebook_detail", pk=obj.pk)
    return render(request, "masterdata/pricebook_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.name}", "mode": "edit"})


@tenant_admin_required
def pricebook_delete(request, pk):
    obj = get_object_or_404(PriceBook, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Price book “{label}” deleted.")
    return redirect("masterdata:pricebook_list")


# ============================================================ localization settings
@login_required
def localizationsetting_list(request):
    qs = LocalizationSetting.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(language_code__icontains=q) | Q(language_name__icontains=q)
                       | Q(locale__icontains=q))
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "masterdata/localizationsetting_list.html", {
        "page_title": "Localization & Multi-Language", "page_obj": page_obj,
        "localizationsettings": page_obj.object_list,
        "status_choices": LocalizationSetting.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def localizationsetting_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = LocalizationSettingForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Localization setting created.")
        return redirect("masterdata:localizationsetting_list")
    return render(request, "masterdata/localizationsetting_form.html",
                  {"form": form, "page_title": "Add Localization Setting", "mode": "create"})


@login_required
def localizationsetting_detail(request, pk):
    obj = get_object_or_404(LocalizationSetting, pk=pk, tenant=request.tenant)
    return render(request, "masterdata/localizationsetting_detail.html",
                  {"obj": obj, "page_title": obj.language_name})


@tenant_admin_required
def localizationsetting_edit(request, pk):
    obj = get_object_or_404(LocalizationSetting, pk=pk, tenant=request.tenant)
    form = LocalizationSettingForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Localization setting updated.")
        return redirect("masterdata:localizationsetting_detail", pk=obj.pk)
    return render(request, "masterdata/localizationsetting_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.language_name}", "mode": "edit"})


@tenant_admin_required
def localizationsetting_delete(request, pk):
    obj = get_object_or_404(LocalizationSetting, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.language_name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Localization setting “{label}” deleted.")
    return redirect("masterdata:localizationsetting_list")
