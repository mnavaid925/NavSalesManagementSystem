from django.urls import path

from . import views

app_name = "leads"

urlpatterns = [
    # Leads (Lead Capture & Ingestion)
    path("", views.lead_list, name="lead_list"),
    path("add/", views.lead_create, name="lead_create"),
    path("<int:pk>/", views.lead_detail, name="lead_detail"),
    path("<int:pk>/edit/", views.lead_edit, name="lead_edit"),
    path("<int:pk>/delete/", views.lead_delete, name="lead_delete"),

    # Lead scores (Lead Scoring & Grading)
    path("scores/", views.leadscore_list, name="leadscore_list"),
    path("scores/add/", views.leadscore_create, name="leadscore_create"),
    path("scores/<int:pk>/", views.leadscore_detail, name="leadscore_detail"),
    path("scores/<int:pk>/edit/", views.leadscore_edit, name="leadscore_edit"),
    path("scores/<int:pk>/delete/", views.leadscore_delete, name="leadscore_delete"),

    # Lead sources (Lead Qualification & Routing)
    path("sources/", views.leadsource_list, name="leadsource_list"),
    path("sources/add/", views.leadsource_create, name="leadsource_create"),
    path("sources/<int:pk>/", views.leadsource_detail, name="leadsource_detail"),
    path("sources/<int:pk>/edit/", views.leadsource_edit, name="leadsource_edit"),
    path("sources/<int:pk>/delete/", views.leadsource_delete, name="leadsource_delete"),

    # Nurture campaigns (Lead Nurturing & Drip Campaigns)
    path("campaigns/", views.nurturecampaign_list, name="nurturecampaign_list"),
    path("campaigns/add/", views.nurturecampaign_create, name="nurturecampaign_create"),
    path("campaigns/<int:pk>/", views.nurturecampaign_detail, name="nurturecampaign_detail"),
    path("campaigns/<int:pk>/edit/", views.nurturecampaign_edit, name="nurturecampaign_edit"),
    path("campaigns/<int:pk>/delete/", views.nurturecampaign_delete, name="nurturecampaign_delete"),

    # Lead conversions (Lead Conversion & Handoff)
    path("conversions/", views.leadconversion_list, name="leadconversion_list"),
    path("conversions/add/", views.leadconversion_create, name="leadconversion_create"),
    path("conversions/<int:pk>/", views.leadconversion_detail, name="leadconversion_detail"),
    path("conversions/<int:pk>/edit/", views.leadconversion_edit, name="leadconversion_edit"),
    path("conversions/<int:pk>/delete/", views.leadconversion_delete, name="leadconversion_delete"),
]
