"""Shared view decorators."""
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def tenant_admin_required(view):
    """Allow only tenant admins (or superusers) to manage workspace data.

    Used for user/role/invite management and all Module-0 write operations
    (subscriptions, invoices, encryption keys, branding, health metrics).
    """

    @wraps(view)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not (request.user.is_superuser or getattr(request.user, "is_tenant_admin", False)):
            messages.error(request, "You don't have permission to manage your workspace.")
            return redirect("dashboard:index")
        return view(request, *args, **kwargs)

    return _wrapped
