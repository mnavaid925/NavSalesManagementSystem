from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.decorators import tenant_admin_required
from apps.core.utils import log_action

from .forms import (
    FulfillmentForm, OrderAmendmentForm, OrderForm, OrderLineForm, RevenueScheduleForm,
)
from .models import Fulfillment, Order, OrderAmendment, OrderLine, RevenueSchedule


def _no_tenant_redirect(request):
    messages.info(request, "Switch to a tenant workspace to manage this — the superuser has no tenant.")
    return redirect("dashboard:index")


def _page(request, qs, per_page=12):
    paginator = Paginator(qs, per_page)
    return paginator, paginator.get_page(request.GET.get("page"))


# ============================================================ orders
@login_required
def order_list(request):
    qs = Order.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(customer_name__icontains=q)
                       | Q(customer_email__icontains=q) | Q(notes__icontains=q))
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    channel = request.GET.get("channel", "")
    if channel:
        qs = qs.filter(channel=channel)
    paginator, page_obj = _page(request, qs)
    return render(request, "orders/order_list.html", {
        "page_title": "Order Capture & Validation", "page_obj": page_obj, "orders": page_obj.object_list,
        "status_choices": Order.STATUS_CHOICES, "channel_choices": Order.CHANNEL_CHOICES,
        "total": paginator.count,
    })


@login_required
def order_detail(request, pk):
    obj = get_object_or_404(
        Order.objects.prefetch_related("lines", "fulfillments", "amendments", "revenue_schedules"),
        pk=pk, tenant=request.tenant,
    )
    lines = obj.lines.all()
    fulfillments = obj.fulfillments.all()
    amendments = obj.amendments.all()
    schedules = obj.revenue_schedules.all()
    return render(request, "orders/order_detail.html", {
        "obj": obj, "page_title": str(obj), "lines": lines,
        "fulfillments": fulfillments, "amendments": amendments, "schedules": schedules,
    })


@tenant_admin_required
def order_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = OrderForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, f"Order {obj.number} created.")
        return redirect("orders:order_detail", pk=obj.pk)
    return render(request, "orders/order_form.html",
                  {"form": form, "page_title": "Add Order", "mode": "create"})


@tenant_admin_required
def order_edit(request, pk):
    obj = get_object_or_404(Order, pk=pk, tenant=request.tenant)
    form = OrderForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Order updated.")
        return redirect("orders:order_detail", pk=obj.pk)
    return render(request, "orders/order_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.number}", "mode": "edit"})


@tenant_admin_required
def order_delete(request, pk):
    obj = get_object_or_404(Order, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.number
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Order {label} deleted.")
    return redirect("orders:order_list")


# ============================================================ order lines
@login_required
def orderline_list(request):
    qs = OrderLine.objects.filter(tenant=request.tenant).select_related("order")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(product_name__icontains=q) | Q(sku__icontains=q)
                       | Q(order__number__icontains=q))
    order = request.GET.get("order", "")
    if order:
        qs = qs.filter(order_id=order)
    paginator, page_obj = _page(request, qs)
    return render(request, "orders/orderline_list.html", {
        "page_title": "Order Line Items", "page_obj": page_obj, "lines": page_obj.object_list,
        "orders": Order.objects.filter(tenant=request.tenant), "total": paginator.count,
    })


@login_required
def orderline_detail(request, pk):
    obj = get_object_or_404(OrderLine.objects.select_related("order"), pk=pk, tenant=request.tenant)
    return render(request, "orders/orderline_detail.html", {"obj": obj, "page_title": str(obj)})


@tenant_admin_required
def orderline_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = OrderLineForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Line item added.")
        return redirect("orders:orderline_detail", pk=obj.pk)
    return render(request, "orders/orderline_form.html",
                  {"form": form, "page_title": "Add Line Item", "mode": "create"})


@tenant_admin_required
def orderline_edit(request, pk):
    obj = get_object_or_404(OrderLine, pk=pk, tenant=request.tenant)
    form = OrderLineForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Line item updated.")
        return redirect("orders:orderline_detail", pk=obj.pk)
    return render(request, "orders/orderline_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj}", "mode": "edit"})


@tenant_admin_required
def orderline_delete(request, pk):
    obj = get_object_or_404(OrderLine, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, "Line item deleted.")
    return redirect("orders:orderline_list")


# ============================================================ fulfillments
@login_required
def fulfillment_list(request):
    qs = Fulfillment.objects.filter(tenant=request.tenant).select_related("order")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(tracking_number__icontains=q) | Q(warehouse__icontains=q)
                       | Q(order__number__icontains=q))
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    carrier = request.GET.get("carrier", "")
    if carrier:
        qs = qs.filter(carrier=carrier)
    paginator, page_obj = _page(request, qs)
    return render(request, "orders/fulfillment_list.html", {
        "page_title": "Order Fulfillment Tracking", "page_obj": page_obj, "fulfillments": page_obj.object_list,
        "status_choices": Fulfillment.STATUS_CHOICES, "carrier_choices": Fulfillment.CARRIER_CHOICES,
        "total": paginator.count,
    })


@login_required
def fulfillment_detail(request, pk):
    obj = get_object_or_404(Fulfillment.objects.select_related("order"), pk=pk, tenant=request.tenant)
    return render(request, "orders/fulfillment_detail.html", {"obj": obj, "page_title": str(obj)})


@tenant_admin_required
def fulfillment_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = FulfillmentForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Fulfillment recorded.")
        return redirect("orders:fulfillment_detail", pk=obj.pk)
    return render(request, "orders/fulfillment_form.html",
                  {"form": form, "page_title": "Add Fulfillment", "mode": "create"})


@tenant_admin_required
def fulfillment_edit(request, pk):
    obj = get_object_or_404(Fulfillment, pk=pk, tenant=request.tenant)
    form = FulfillmentForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Fulfillment updated.")
        return redirect("orders:fulfillment_detail", pk=obj.pk)
    return render(request, "orders/fulfillment_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj}", "mode": "edit"})


@tenant_admin_required
def fulfillment_delete(request, pk):
    obj = get_object_or_404(Fulfillment, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, "Fulfillment deleted.")
    return redirect("orders:fulfillment_list")


# ============================================================ amendments
@login_required
def orderamendment_list(request):
    qs = OrderAmendment.objects.filter(tenant=request.tenant).select_related("order")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(reason__icontains=q) | Q(requested_by__icontains=q)
                       | Q(order__number__icontains=q))
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    amendment_type = request.GET.get("amendment_type", "")
    if amendment_type:
        qs = qs.filter(amendment_type=amendment_type)
    order = request.GET.get("order", "")
    if order:
        qs = qs.filter(order_id=order)
    paginator, page_obj = _page(request, qs)
    return render(request, "orders/orderamendment_list.html", {
        "page_title": "Order Amendments & Cancellations", "page_obj": page_obj,
        "amendments": page_obj.object_list,
        "status_choices": OrderAmendment.STATUS_CHOICES, "type_choices": OrderAmendment.TYPE_CHOICES,
        "orders": Order.objects.filter(tenant=request.tenant),
        "total": paginator.count,
    })


@login_required
def orderamendment_detail(request, pk):
    obj = get_object_or_404(OrderAmendment.objects.select_related("order"), pk=pk, tenant=request.tenant)
    return render(request, "orders/orderamendment_detail.html", {"obj": obj, "page_title": str(obj)})


@tenant_admin_required
def orderamendment_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = OrderAmendmentForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Amendment logged.")
        return redirect("orders:orderamendment_detail", pk=obj.pk)
    return render(request, "orders/orderamendment_form.html",
                  {"form": form, "page_title": "Add Amendment", "mode": "create"})


@tenant_admin_required
def orderamendment_edit(request, pk):
    obj = get_object_or_404(OrderAmendment, pk=pk, tenant=request.tenant)
    form = OrderAmendmentForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Amendment updated.")
        return redirect("orders:orderamendment_detail", pk=obj.pk)
    return render(request, "orders/orderamendment_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj}", "mode": "edit"})


@tenant_admin_required
def orderamendment_delete(request, pk):
    obj = get_object_or_404(OrderAmendment, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, "Amendment deleted.")
    return redirect("orders:orderamendment_list")


# ============================================================ revenue schedules
@login_required
def revenueschedule_list(request):
    qs = RevenueSchedule.objects.filter(tenant=request.tenant).select_related("order")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(period_label__icontains=q) | Q(notes__icontains=q)
                       | Q(order__number__icontains=q))
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    method = request.GET.get("method", "")
    if method:
        qs = qs.filter(method=method)
    paginator, page_obj = _page(request, qs)
    return render(request, "orders/revenueschedule_list.html", {
        "page_title": "Revenue Recognition & Scheduling", "page_obj": page_obj,
        "schedules": page_obj.object_list,
        "status_choices": RevenueSchedule.STATUS_CHOICES, "method_choices": RevenueSchedule.METHOD_CHOICES,
        "total": paginator.count,
    })


@login_required
def revenueschedule_detail(request, pk):
    obj = get_object_or_404(RevenueSchedule.objects.select_related("order"), pk=pk, tenant=request.tenant)
    return render(request, "orders/revenueschedule_detail.html", {"obj": obj, "page_title": str(obj)})


@tenant_admin_required
def revenueschedule_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = RevenueScheduleForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Revenue schedule created.")
        return redirect("orders:revenueschedule_detail", pk=obj.pk)
    return render(request, "orders/revenueschedule_form.html",
                  {"form": form, "page_title": "Add Revenue Schedule", "mode": "create"})


@tenant_admin_required
def revenueschedule_edit(request, pk):
    obj = get_object_or_404(RevenueSchedule, pk=pk, tenant=request.tenant)
    form = RevenueScheduleForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Revenue schedule updated.")
        return redirect("orders:revenueschedule_detail", pk=obj.pk)
    return render(request, "orders/revenueschedule_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj}", "mode": "edit"})


@tenant_admin_required
def revenueschedule_delete(request, pk):
    obj = get_object_or_404(RevenueSchedule, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, "Revenue schedule deleted.")
    return redirect("orders:revenueschedule_list")
