from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from .models import AuditLog
from .navigation import lookup_submodule


@login_required
def roadmap(request, module, sub):
    """Placeholder page for sub-modules that are on the roadmap but not built yet."""
    module_name, sub_name = lookup_submodule(module, sub)
    context = {
        "page_title": sub_name or "On the roadmap",
        "module_number": module,
        "module_name": module_name,
        "sub_name": sub_name,
    }
    return render(request, "core/roadmap.html", context)


@login_required
def audit_log(request):
    """Read-only, tenant-scoped audit trail (Module 0 / Module 20 sub-module)."""
    qs = AuditLog.objects.filter(tenant=request.tenant).select_related("user")

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(model_name__icontains=q) | Q(object_repr__icontains=q) | Q(detail__icontains=q)
        )

    action = request.GET.get("action", "")
    if action:
        qs = qs.filter(action=action)

    paginator = Paginator(qs, 25)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_title": "Audit Log",
        "page_obj": page_obj,
        "logs": page_obj.object_list,
        "action_choices": AuditLog.ACTION_CHOICES,
        "total": paginator.count,
    }
    return render(request, "core/audit_log.html", context)
