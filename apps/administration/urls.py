from django.urls import path

from . import views

app_name = "administration"

urlpatterns = [
    # Data Security & Privacy (security policies)
    path("policies/", views.securitypolicy_list, name="securitypolicy_list"),
    path("policies/add/", views.securitypolicy_create, name="securitypolicy_create"),
    path("policies/<int:pk>/", views.securitypolicy_detail, name="securitypolicy_detail"),
    path("policies/<int:pk>/edit/", views.securitypolicy_edit, name="securitypolicy_edit"),
    path("policies/<int:pk>/delete/", views.securitypolicy_delete, name="securitypolicy_delete"),

    # Data privacy rules
    path("privacy-rules/", views.dataprivacyrule_list, name="dataprivacyrule_list"),
    path("privacy-rules/add/", views.dataprivacyrule_create, name="dataprivacyrule_create"),
    path("privacy-rules/<int:pk>/", views.dataprivacyrule_detail, name="dataprivacyrule_detail"),
    path("privacy-rules/<int:pk>/edit/", views.dataprivacyrule_edit, name="dataprivacyrule_edit"),
    path("privacy-rules/<int:pk>/delete/", views.dataprivacyrule_delete, name="dataprivacyrule_delete"),

    # Compliance tracking
    path("compliance/", views.complianceitem_list, name="complianceitem_list"),
    path("compliance/add/", views.complianceitem_create, name="complianceitem_create"),
    path("compliance/<int:pk>/", views.complianceitem_detail, name="complianceitem_detail"),
    path("compliance/<int:pk>/edit/", views.complianceitem_edit, name="complianceitem_edit"),
    path("compliance/<int:pk>/delete/", views.complianceitem_delete, name="complianceitem_delete"),

    # Backup & Disaster Recovery
    path("backups/", views.backupjob_list, name="backupjob_list"),
    path("backups/add/", views.backupjob_create, name="backupjob_create"),
    path("backups/<int:pk>/", views.backupjob_detail, name="backupjob_detail"),
    path("backups/<int:pk>/edit/", views.backupjob_edit, name="backupjob_edit"),
    path("backups/<int:pk>/delete/", views.backupjob_delete, name="backupjob_delete"),

    # System Health & Performance
    path("health/", views.systemhealthmetric_list, name="systemhealthmetric_list"),
    path("health/add/", views.systemhealthmetric_create, name="systemhealthmetric_create"),
    path("health/<int:pk>/", views.systemhealthmetric_detail, name="systemhealthmetric_detail"),
    path("health/<int:pk>/edit/", views.systemhealthmetric_edit, name="systemhealthmetric_edit"),
    path("health/<int:pk>/delete/", views.systemhealthmetric_delete, name="systemhealthmetric_delete"),
]
