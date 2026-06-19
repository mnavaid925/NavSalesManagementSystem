from django.urls import path

from . import views

app_name = "contracts"

urlpatterns = [
    # Subscription Lifecycle
    path("contracts/", views.contract_list, name="contract_list"),
    path("contracts/add/", views.contract_create, name="contract_create"),
    path("contracts/<int:pk>/", views.contract_detail, name="contract_detail"),
    path("contracts/<int:pk>/edit/", views.contract_edit, name="contract_edit"),
    path("contracts/<int:pk>/delete/", views.contract_delete, name="contract_delete"),

    # Contract Authoring & Redlining
    path("clauses/", views.contractclause_list, name="contractclause_list"),
    path("clauses/add/", views.contractclause_create, name="contractclause_create"),
    path("clauses/<int:pk>/", views.contractclause_detail, name="contractclause_detail"),
    path("clauses/<int:pk>/edit/", views.contractclause_edit, name="contractclause_edit"),
    path("clauses/<int:pk>/delete/", views.contractclause_delete, name="contractclause_delete"),

    # Renewal Automation
    path("renewals/", views.renewalschedule_list, name="renewalschedule_list"),
    path("renewals/add/", views.renewalschedule_create, name="renewalschedule_create"),
    path("renewals/<int:pk>/", views.renewalschedule_detail, name="renewalschedule_detail"),
    path("renewals/<int:pk>/edit/", views.renewalschedule_edit, name="renewalschedule_edit"),
    path("renewals/<int:pk>/delete/", views.renewalschedule_delete, name="renewalschedule_delete"),

    # Usage-Based Billing
    path("usage/", views.usagerecord_list, name="usagerecord_list"),
    path("usage/add/", views.usagerecord_create, name="usagerecord_create"),
    path("usage/<int:pk>/", views.usagerecord_detail, name="usagerecord_detail"),
    path("usage/<int:pk>/edit/", views.usagerecord_edit, name="usagerecord_edit"),
    path("usage/<int:pk>/delete/", views.usagerecord_delete, name="usagerecord_delete"),

    # Contract Compliance & Obligations
    path("obligations/", views.contractobligation_list, name="contractobligation_list"),
    path("obligations/add/", views.contractobligation_create, name="contractobligation_create"),
    path("obligations/<int:pk>/", views.contractobligation_detail, name="contractobligation_detail"),
    path("obligations/<int:pk>/edit/", views.contractobligation_edit, name="contractobligation_edit"),
    path("obligations/<int:pk>/delete/", views.contractobligation_delete, name="contractobligation_delete"),
]
