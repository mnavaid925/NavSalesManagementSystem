from django.urls import path

from . import views

app_name = "mobile"

urlpatterns = [
    # Mobile CRM Access
    path("devices/", views.mobiledevice_list, name="mobiledevice_list"),
    path("devices/add/", views.mobiledevice_create, name="mobiledevice_create"),
    path("devices/<int:pk>/", views.mobiledevice_detail, name="mobiledevice_detail"),
    path("devices/<int:pk>/edit/", views.mobiledevice_edit, name="mobiledevice_edit"),
    path("devices/<int:pk>/delete/", views.mobiledevice_delete, name="mobiledevice_delete"),

    # Field Sales Tools
    path("visits/", views.fieldvisit_list, name="fieldvisit_list"),
    path("visits/add/", views.fieldvisit_create, name="fieldvisit_create"),
    path("visits/<int:pk>/", views.fieldvisit_detail, name="fieldvisit_detail"),
    path("visits/<int:pk>/edit/", views.fieldvisit_edit, name="fieldvisit_edit"),
    path("visits/<int:pk>/delete/", views.fieldvisit_delete, name="fieldvisit_delete"),

    # Mobile Quoting & Approvals
    path("quotes/", views.mobilequote_list, name="mobilequote_list"),
    path("quotes/add/", views.mobilequote_create, name="mobilequote_create"),
    path("quotes/<int:pk>/", views.mobilequote_detail, name="mobilequote_detail"),
    path("quotes/<int:pk>/edit/", views.mobilequote_edit, name="mobilequote_edit"),
    path("quotes/<int:pk>/delete/", views.mobilequote_delete, name="mobilequote_delete"),

    # Voice & Call Integration
    path("calls/", views.callactivity_list, name="callactivity_list"),
    path("calls/add/", views.callactivity_create, name="callactivity_create"),
    path("calls/<int:pk>/", views.callactivity_detail, name="callactivity_detail"),
    path("calls/<int:pk>/edit/", views.callactivity_edit, name="callactivity_edit"),
    path("calls/<int:pk>/delete/", views.callactivity_delete, name="callactivity_delete"),

    # Mobile Dashboards & Alerts
    path("alerts/", views.mobilealert_list, name="mobilealert_list"),
    path("alerts/add/", views.mobilealert_create, name="mobilealert_create"),
    path("alerts/<int:pk>/", views.mobilealert_detail, name="mobilealert_detail"),
    path("alerts/<int:pk>/edit/", views.mobilealert_edit, name="mobilealert_edit"),
    path("alerts/<int:pk>/delete/", views.mobilealert_delete, name="mobilealert_delete"),
]
