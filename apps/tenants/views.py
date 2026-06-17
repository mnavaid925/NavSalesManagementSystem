from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.core.decorators import tenant_admin_required
from apps.core.utils import log_action

from .forms import (
    BrandingSettingForm, EncryptionKeyForm, HealthMetricForm,
    InvoiceForm, OnboardingStepForm, SubscriptionForm,
)
from .models import (
    BrandingSetting, EncryptionKey, HealthMetric, Invoice, OnboardingStep, Subscription,
)


def _no_tenant_redirect(request):
    messages.info(request, "Switch to a tenant workspace to manage this — the superuser has no tenant.")
    return redirect("dashboard:index")


def _page(request, qs, per_page=12):
    paginator = Paginator(qs, per_page)
    return paginator, paginator.get_page(request.GET.get("page"))


# ============================================================ overview
@login_required
def overview(request):
    tenant = request.tenant
    ctx = {"page_title": "Tenant & Subscription", "has_tenant": tenant is not None}
    if tenant is not None:
        invoices = Invoice.objects.filter(tenant=tenant)
        steps = OnboardingStep.objects.filter(tenant=tenant)
        ctx.update({
            "onboarding_total": steps.count(),
            "onboarding_done": steps.filter(status=OnboardingStep.STATUS_DONE).count(),
            "active_subs": Subscription.objects.filter(
                tenant=tenant, status__in=[Subscription.STATUS_ACTIVE, Subscription.STATUS_TRIALING]).count(),
            "paid_revenue": invoices.filter(status=Invoice.STATUS_PAID).aggregate(t=Sum("amount"))["t"] or Decimal("0"),
            "open_invoices": invoices.exclude(status=Invoice.STATUS_PAID).count(),
            "keys_active": EncryptionKey.objects.filter(tenant=tenant, status=EncryptionKey.STATUS_ACTIVE).count(),
            "branding_count": BrandingSetting.objects.filter(tenant=tenant).count(),
            "metrics_alerting": HealthMetric.objects.filter(
                tenant=tenant, status__in=[HealthMetric.STATUS_WARNING, HealthMetric.STATUS_CRITICAL]).count(),
        })
    return render(request, "tenants/overview.html", ctx)


# ============================================================ onboarding steps
@login_required
def onboardingstep_list(request):
    qs = OnboardingStep.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "tenants/onboardingstep_list.html", {
        "page_title": "Tenant Onboarding", "page_obj": page_obj, "steps": page_obj.object_list,
        "status_choices": OnboardingStep.STATUS_CHOICES, "total": paginator.count,
    })


@tenant_admin_required
def onboardingstep_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = OnboardingStepForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Onboarding step added.")
        return redirect("tenants:onboardingstep_list")
    return render(request, "tenants/onboardingstep_form.html",
                  {"form": form, "page_title": "Add Onboarding Step", "mode": "create"})


@login_required
def onboardingstep_detail(request, pk):
    obj = get_object_or_404(OnboardingStep, pk=pk, tenant=request.tenant)
    return render(request, "tenants/onboardingstep_detail.html", {"obj": obj, "page_title": obj.title})


@tenant_admin_required
def onboardingstep_edit(request, pk):
    obj = get_object_or_404(OnboardingStep, pk=pk, tenant=request.tenant)
    form = OnboardingStepForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Onboarding step updated.")
        return redirect("tenants:onboardingstep_detail", pk=obj.pk)
    return render(request, "tenants/onboardingstep_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.title}", "mode": "edit"})


@tenant_admin_required
def onboardingstep_delete(request, pk):
    obj = get_object_or_404(OnboardingStep, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, "Onboarding step deleted.")
    return redirect("tenants:onboardingstep_list")


# ============================================================ subscriptions
@login_required
def subscription_list(request):
    qs = Subscription.objects.filter(tenant=request.tenant)
    plan = request.GET.get("plan", "")
    if plan:
        qs = qs.filter(plan=plan)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "tenants/subscription_list.html", {
        "page_title": "Subscription & Billing", "page_obj": page_obj, "subscriptions": page_obj.object_list,
        "plan_choices": Subscription.PLAN_CHOICES, "status_choices": Subscription.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def subscription_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = SubscriptionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Subscription created.")
        return redirect("tenants:subscription_list")
    return render(request, "tenants/subscription_form.html",
                  {"form": form, "page_title": "Add Subscription", "mode": "create"})


@login_required
def subscription_detail(request, pk):
    obj = get_object_or_404(Subscription, pk=pk, tenant=request.tenant)
    invoices = obj.invoices.all()[:20]
    return render(request, "tenants/subscription_detail.html",
                  {"obj": obj, "invoices": invoices, "page_title": str(obj)})


@tenant_admin_required
def subscription_edit(request, pk):
    obj = get_object_or_404(Subscription, pk=pk, tenant=request.tenant)
    form = SubscriptionForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Subscription updated.")
        return redirect("tenants:subscription_detail", pk=obj.pk)
    return render(request, "tenants/subscription_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj}", "mode": "edit"})


@tenant_admin_required
def subscription_delete(request, pk):
    obj = get_object_or_404(Subscription, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, "Subscription deleted.")
    return redirect("tenants:subscription_list")


# ============================================================ invoices
@login_required
def invoice_list(request):
    qs = Invoice.objects.filter(tenant=request.tenant).select_related("subscription")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(notes__icontains=q))
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "tenants/invoice_list.html", {
        "page_title": "Invoices", "page_obj": page_obj, "invoices": page_obj.object_list,
        "status_choices": Invoice.STATUS_CHOICES, "total": paginator.count,
    })


@tenant_admin_required
def invoice_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = InvoiceForm(request.POST or None, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, f"Invoice {obj.number} created.")
        return redirect("tenants:invoice_list")
    return render(request, "tenants/invoice_form.html",
                  {"form": form, "page_title": "Add Invoice", "mode": "create"})


@login_required
def invoice_detail(request, pk):
    obj = get_object_or_404(Invoice.objects.select_related("subscription"), pk=pk, tenant=request.tenant)
    return render(request, "tenants/invoice_detail.html", {"obj": obj, "page_title": obj.number})


@tenant_admin_required
def invoice_edit(request, pk):
    obj = get_object_or_404(Invoice, pk=pk, tenant=request.tenant)
    form = InvoiceForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Invoice updated.")
        return redirect("tenants:invoice_detail", pk=obj.pk)
    return render(request, "tenants/invoice_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.number}", "mode": "edit"})


@tenant_admin_required
def invoice_delete(request, pk):
    obj = get_object_or_404(Invoice, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.number
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Invoice {label} deleted.")
    return redirect("tenants:invoice_list")


# ============================================================ encryption keys
@login_required
def encryptionkey_list(request):
    qs = EncryptionKey.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(label__icontains=q)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    algorithm = request.GET.get("algorithm", "")
    if algorithm:
        qs = qs.filter(algorithm=algorithm)
    paginator, page_obj = _page(request, qs)
    return render(request, "tenants/encryptionkey_list.html", {
        "page_title": "Tenant Isolation & Security", "page_obj": page_obj, "keys": page_obj.object_list,
        "status_choices": EncryptionKey.STATUS_CHOICES, "algo_choices": EncryptionKey.ALGO_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def encryptionkey_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = EncryptionKeyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        plaintext, prefix, hashed = EncryptionKey.generate_secret()
        obj.key_prefix = prefix
        obj.hashed_key = hashed
        obj.save()
        log_action(request, "create", instance=obj, detail="Encryption key generated")
        # WARNING: the plaintext is surfaced ONCE on the detail page via a pop-once
        # session key — NOT a flash message (which would persist in the session store). (L20/L25)
        request.session["_key_reveal"] = {"pk": obj.pk, "secret": plaintext}
        messages.success(request, f"Key “{obj.label}” created — copy the secret below now; it won't be shown again.")
        return redirect("tenants:encryptionkey_detail", pk=obj.pk)
    return render(request, "tenants/encryptionkey_form.html",
                  {"form": form, "page_title": "Generate Key", "mode": "create"})


@login_required
def encryptionkey_detail(request, pk):
    obj = get_object_or_404(EncryptionKey, pk=pk, tenant=request.tenant)
    reveal = request.session.pop("_key_reveal", None)
    plaintext_once = reveal["secret"] if reveal and reveal.get("pk") == obj.pk else None
    return render(request, "tenants/encryptionkey_detail.html",
                  {"obj": obj, "page_title": obj.label, "plaintext_once": plaintext_once})


@tenant_admin_required
def encryptionkey_edit(request, pk):
    obj = get_object_or_404(EncryptionKey, pk=pk, tenant=request.tenant)
    form = EncryptionKeyForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Key updated.")
        return redirect("tenants:encryptionkey_detail", pk=obj.pk)
    return render(request, "tenants/encryptionkey_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.label}", "mode": "edit"})


@tenant_admin_required
def encryptionkey_rotate(request, pk):
    obj = get_object_or_404(EncryptionKey, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        plaintext, prefix, hashed = EncryptionKey.generate_secret()
        obj.key_prefix = prefix
        obj.hashed_key = hashed
        obj.status = EncryptionKey.STATUS_ACTIVE
        obj.last_rotated_at = timezone.now()
        obj.save()
        log_action(request, "update", instance=obj, detail="Encryption key rotated")
        request.session["_key_reveal"] = {"pk": obj.pk, "secret": plaintext}
        messages.success(request, "Key rotated — copy the new secret below now; it won't be shown again.")
    return redirect("tenants:encryptionkey_detail", pk=obj.pk)


@tenant_admin_required
def encryptionkey_delete(request, pk):
    obj = get_object_or_404(EncryptionKey, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.label
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Key “{label}” revoked & deleted.")
    return redirect("tenants:encryptionkey_list")


# ============================================================ branding
@login_required
def brandingsetting_list(request):
    qs = BrandingSetting.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(name__icontains=q)
    theme = request.GET.get("theme", "")
    if theme:
        qs = qs.filter(theme=theme)
    paginator, page_obj = _page(request, qs)
    return render(request, "tenants/brandingsetting_list.html", {
        "page_title": "Custom Branding", "page_obj": page_obj, "profiles": page_obj.object_list,
        "theme_choices": BrandingSetting.THEME_CHOICES, "total": paginator.count,
    })


@tenant_admin_required
def brandingsetting_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = BrandingSettingForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Branding profile created.")
        return redirect("tenants:brandingsetting_list")
    return render(request, "tenants/brandingsetting_form.html",
                  {"form": form, "page_title": "Add Branding Profile", "mode": "create"})


@login_required
def brandingsetting_detail(request, pk):
    obj = get_object_or_404(BrandingSetting, pk=pk, tenant=request.tenant)
    return render(request, "tenants/brandingsetting_detail.html", {"obj": obj, "page_title": obj.name})


@tenant_admin_required
def brandingsetting_edit(request, pk):
    obj = get_object_or_404(BrandingSetting, pk=pk, tenant=request.tenant)
    form = BrandingSettingForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Branding profile updated.")
        return redirect("tenants:brandingsetting_detail", pk=obj.pk)
    return render(request, "tenants/brandingsetting_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.name}", "mode": "edit"})


@tenant_admin_required
def brandingsetting_delete(request, pk):
    obj = get_object_or_404(BrandingSetting, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Branding profile “{label}” deleted.")
    return redirect("tenants:brandingsetting_list")


# ============================================================ health metrics
@login_required
def healthmetric_list(request):
    qs = HealthMetric.objects.filter(tenant=request.tenant)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(metric_name__icontains=q)
    category = request.GET.get("category", "")
    if category:
        qs = qs.filter(category=category)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    paginator, page_obj = _page(request, qs)
    return render(request, "tenants/healthmetric_list.html", {
        "page_title": "Tenant Health Monitoring", "page_obj": page_obj, "metrics": page_obj.object_list,
        "category_choices": HealthMetric.CATEGORY_CHOICES, "status_choices": HealthMetric.STATUS_CHOICES,
        "total": paginator.count,
    })


@tenant_admin_required
def healthmetric_create(request):
    if request.tenant is None:
        return _no_tenant_redirect(request)
    form = HealthMetricForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, "create", instance=obj)
        messages.success(request, "Metric recorded.")
        return redirect("tenants:healthmetric_list")
    return render(request, "tenants/healthmetric_form.html",
                  {"form": form, "page_title": "Record Metric", "mode": "create"})


@login_required
def healthmetric_detail(request, pk):
    obj = get_object_or_404(HealthMetric, pk=pk, tenant=request.tenant)
    return render(request, "tenants/healthmetric_detail.html", {"obj": obj, "page_title": obj.metric_name})


@tenant_admin_required
def healthmetric_edit(request, pk):
    obj = get_object_or_404(HealthMetric, pk=pk, tenant=request.tenant)
    form = HealthMetricForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", instance=obj)
        messages.success(request, "Metric updated.")
        return redirect("tenants:healthmetric_detail", pk=obj.pk)
    return render(request, "tenants/healthmetric_form.html",
                  {"form": form, "obj": obj, "page_title": f"Edit {obj.metric_name}", "mode": "edit"})


@tenant_admin_required
def healthmetric_delete(request, pk):
    obj = get_object_or_404(HealthMetric, pk=pk, tenant=request.tenant)
    if request.method == "POST":
        label = obj.metric_name
        log_action(request, "delete", instance=obj)
        obj.delete()
        messages.success(request, f"Metric “{label}” deleted.")
    return redirect("tenants:healthmetric_list")
