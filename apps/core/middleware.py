"""Multi-tenancy middleware.

Sets ``request.tenant`` for every request:
  - authenticated, non-superuser  -> that user's tenant
  - superuser or anonymous         -> None (sees no tenant-scoped data, by design)

Every tenant-scoped view filters ``Model.objects.filter(tenant=request.tenant)``.
Must run AFTER ``AuthenticationMiddleware`` so ``request.user`` is populated.
"""


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated and not user.is_superuser:
            request.tenant = getattr(user, "tenant", None)
        else:
            request.tenant = None
        return self.get_response(request)
