from django.urls import path

from . import views

app_name = "partners"

urlpatterns = [
    # Partner Recruitment & Onboarding
    path("partners/", views.partner_list, name="partner_list"),
    path("partners/add/", views.partner_create, name="partner_create"),
    path("partners/<int:pk>/", views.partner_detail, name="partner_detail"),
    path("partners/<int:pk>/edit/", views.partner_edit, name="partner_edit"),
    path("partners/<int:pk>/delete/", views.partner_delete, name="partner_delete"),

    # Deal Registration & Protection
    path("deals/", views.dealregistration_list, name="dealregistration_list"),
    path("deals/add/", views.dealregistration_create, name="dealregistration_create"),
    path("deals/<int:pk>/", views.dealregistration_detail, name="dealregistration_detail"),
    path("deals/<int:pk>/edit/", views.dealregistration_edit, name="dealregistration_edit"),
    path("deals/<int:pk>/delete/", views.dealregistration_delete, name="dealregistration_delete"),

    # Partner Portal & Collaboration
    path("collateral/", views.partnercollateral_list, name="partnercollateral_list"),
    path("collateral/add/", views.partnercollateral_create, name="partnercollateral_create"),
    path("collateral/<int:pk>/", views.partnercollateral_detail, name="partnercollateral_detail"),
    path("collateral/<int:pk>/edit/", views.partnercollateral_edit, name="partnercollateral_edit"),
    path("collateral/<int:pk>/delete/", views.partnercollateral_delete, name="partnercollateral_delete"),

    # Partner Performance Tracking
    path("performance/", views.partnerperformance_list, name="partnerperformance_list"),
    path("performance/add/", views.partnerperformance_create, name="partnerperformance_create"),
    path("performance/<int:pk>/", views.partnerperformance_detail, name="partnerperformance_detail"),
    path("performance/<int:pk>/edit/", views.partnerperformance_edit, name="partnerperformance_edit"),
    path("performance/<int:pk>/delete/", views.partnerperformance_delete, name="partnerperformance_delete"),

    # Channel Conflict Management
    path("conflicts/", views.channelconflict_list, name="channelconflict_list"),
    path("conflicts/add/", views.channelconflict_create, name="channelconflict_create"),
    path("conflicts/<int:pk>/", views.channelconflict_detail, name="channelconflict_detail"),
    path("conflicts/<int:pk>/edit/", views.channelconflict_edit, name="channelconflict_edit"),
    path("conflicts/<int:pk>/delete/", views.channelconflict_delete, name="channelconflict_delete"),
]
