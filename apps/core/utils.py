"""Shared helpers for tenant-scoped apps."""
from .models import AuditLog


def log_action(request, action, instance=None, model_name="", detail=""):
    """Write an AuditLog row for the current tenant + user.

    Safe to call from any view: a missing tenant (e.g. superuser) is stored as
    null rather than raising.
    """
    user = None
    req_user = getattr(request, "user", None)
    if req_user is not None and req_user.is_authenticated:
        user = req_user
    AuditLog.objects.create(
        tenant=getattr(request, "tenant", None),
        user=user,
        action=action,
        model_name=model_name or (instance.__class__.__name__ if instance is not None else ""),
        object_repr=(str(instance)[:255] if instance is not None else ""),
        detail=(detail or "")[:255],
    )
