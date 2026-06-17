from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.dashboard.urls")),
    path("auth/", include("apps.accounts.urls")),
    path("core/", include("apps.core.urls")),
    path("tenant/", include("apps.tenants.urls")),
    path("leads/", include("apps.leads.urls")),
    path("opportunities/", include("apps.opportunities.urls")),
    path("crm/", include("apps.crm.urls")),
    path("forecasting/", include("apps.forecasting.urls")),
    path("quotes/", include("apps.quotes.urls")),
    path("orders/", include("apps.orders.urls")),
    path("territories/", include("apps.territories.urls")),
    path("activities/", include("apps.activities.urls")),
    path("enablement/", include("apps.enablement.urls")),
    path("compensation/", include("apps.compensation.urls")),
]
