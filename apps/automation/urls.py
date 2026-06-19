from django.urls import path

from . import views

app_name = "automation"

urlpatterns = [
    # Visual Process Designer
    path("flows/", views.processflow_list, name="processflow_list"),
    path("flows/add/", views.processflow_create, name="processflow_create"),
    path("flows/<int:pk>/", views.processflow_detail, name="processflow_detail"),
    path("flows/<int:pk>/edit/", views.processflow_edit, name="processflow_edit"),
    path("flows/<int:pk>/delete/", views.processflow_delete, name="processflow_delete"),

    # Auto-Assignment Rules
    path("assignment-rules/", views.assignmentrule_list, name="assignmentrule_list"),
    path("assignment-rules/add/", views.assignmentrule_create, name="assignmentrule_create"),
    path("assignment-rules/<int:pk>/", views.assignmentrule_detail, name="assignmentrule_detail"),
    path("assignment-rules/<int:pk>/edit/", views.assignmentrule_edit, name="assignmentrule_edit"),
    path("assignment-rules/<int:pk>/delete/", views.assignmentrule_delete, name="assignmentrule_delete"),

    # Approval Workflows
    path("approval-workflows/", views.approvalworkflow_list, name="approvalworkflow_list"),
    path("approval-workflows/add/", views.approvalworkflow_create, name="approvalworkflow_create"),
    path("approval-workflows/<int:pk>/", views.approvalworkflow_detail, name="approvalworkflow_detail"),
    path("approval-workflows/<int:pk>/edit/", views.approvalworkflow_edit, name="approvalworkflow_edit"),
    path("approval-workflows/<int:pk>/delete/", views.approvalworkflow_delete, name="approvalworkflow_delete"),

    # Notification & Alert Engine
    path("alert-rules/", views.alertrule_list, name="alertrule_list"),
    path("alert-rules/add/", views.alertrule_create, name="alertrule_create"),
    path("alert-rules/<int:pk>/", views.alertrule_detail, name="alertrule_detail"),
    path("alert-rules/<int:pk>/edit/", views.alertrule_edit, name="alertrule_edit"),
    path("alert-rules/<int:pk>/delete/", views.alertrule_delete, name="alertrule_delete"),

    # Data Enrichment & Cleansing
    path("enrichment-rules/", views.enrichmentrule_list, name="enrichmentrule_list"),
    path("enrichment-rules/add/", views.enrichmentrule_create, name="enrichmentrule_create"),
    path("enrichment-rules/<int:pk>/", views.enrichmentrule_detail, name="enrichmentrule_detail"),
    path("enrichment-rules/<int:pk>/edit/", views.enrichmentrule_edit, name="enrichmentrule_edit"),
    path("enrichment-rules/<int:pk>/delete/", views.enrichmentrule_delete, name="enrichmentrule_delete"),
]
