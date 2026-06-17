from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.dashboard.urls")),
    path("auth/", include("apps.accounts.urls")),
    path("core/", include("apps.core.urls")),
    path("tenant/", include("apps.tenants.urls")),
]
