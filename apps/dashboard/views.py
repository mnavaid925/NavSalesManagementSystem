import calendar
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render
from django.utils import timezone

from apps.accounts.models import User
from apps.tenants.models import Invoice, Subscription


def _pct_delta(current, previous):
    """Month-over-month percentage change, guarded against divide-by-zero."""
    current = Decimal(current or 0)
    previous = Decimal(previous or 0)
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round(float((current - previous) / previous * 100), 1)


@login_required
def index(request):
    tenant = request.tenant
    now = timezone.localtime(timezone.now())
    year = now.year

    context = {"page_title": "Dashboard", "today": now, "has_tenant": tenant is not None}

    if tenant is None:
        # Superuser / no-tenant: data is tenant-scoped, so prompt for a tenant login.
        return render(request, "dashboard/index.html", context)

    invoices = Invoice.objects.filter(tenant=tenant)
    paid = invoices.filter(status=Invoice.STATUS_PAID)

    # ---- month boundaries for deltas ----
    this_month = now.replace(day=1).date()
    if this_month.month == 1:
        last_month = this_month.replace(year=this_month.year - 1, month=12)
    else:
        last_month = this_month.replace(month=this_month.month - 1)

    total_revenue = paid.aggregate(t=Sum("amount"))["t"] or Decimal("0")
    rev_this = paid.filter(issued_on__gte=this_month).aggregate(t=Sum("amount"))["t"] or 0
    rev_last = paid.filter(issued_on__gte=last_month, issued_on__lt=this_month).aggregate(t=Sum("amount"))["t"] or 0

    active_subs = Subscription.objects.filter(
        tenant=tenant, status__in=[Subscription.STATUS_ACTIVE, Subscription.STATUS_TRIALING]
    ).count()
    subs_this = Subscription.objects.filter(tenant=tenant, started_on__gte=this_month).count()
    subs_last = Subscription.objects.filter(
        tenant=tenant, started_on__gte=last_month, started_on__lt=this_month).count()

    team = User.objects.filter(tenant=tenant)
    users_total = team.count()
    users_this = team.filter(date_joined__date__gte=this_month).count()
    users_last = team.filter(date_joined__date__gte=last_month, date_joined__date__lt=this_month).count()

    open_invoices = invoices.filter(
        status__in=[Invoice.STATUS_SENT, Invoice.STATUS_OVERDUE, Invoice.STATUS_DRAFT])
    open_count = open_invoices.count()
    open_amount = open_invoices.aggregate(t=Sum("amount"))["t"] or Decimal("0")

    # ---- revenue-by-month chart (current year, paid invoices) ----
    monthly = {row["m"].month: row["total"]
               for row in paid.filter(issued_on__year=year)
               .annotate(m=TruncMonth("issued_on")).values("m")
               .annotate(total=Sum("amount")).order_by("m")}
    chart_labels = [calendar.month_abbr[m] for m in range(1, 13)]
    chart_values = [float(monthly.get(m, 0) or 0) for m in range(1, 13)]
    peak_month = chart_labels[chart_values.index(max(chart_values))] if any(chart_values) else "—"

    # ---- sales overview gauge: revenue vs annual target ----
    annual_target = (Subscription.objects.filter(tenant=tenant).aggregate(
        t=Sum("monthly_amount"))["t"] or Decimal("0")) * 12
    attainment = float(min(100, (total_revenue / annual_target * 100))) if annual_target else 0.0

    context.update({
        "total_revenue": total_revenue,
        "revenue_delta": _pct_delta(rev_this, rev_last),
        "active_subs": active_subs,
        "subs_delta": _pct_delta(subs_this, subs_last),
        "users_total": users_total,
        "users_delta": _pct_delta(users_this, users_last),
        "open_count": open_count,
        "open_amount": open_amount,
        "chart_labels": chart_labels,
        "chart_values": chart_values,
        "peak_month": peak_month,
        "peak_value": max(chart_values) if chart_values else 0,
        "attainment": round(attainment, 1),
        "annual_target": annual_target,
        "recent_invoices": invoices.select_related("subscription").order_by("-issued_on", "-id")[:8],
    })
    return render(request, "dashboard/index.html", context)
