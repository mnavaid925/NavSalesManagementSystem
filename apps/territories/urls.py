from django.urls import path

from . import views

app_name = "territories"

urlpatterns = [
    # Territory Design & Mapping
    path("territories/", views.territory_list, name="territory_list"),
    path("territories/add/", views.territory_create, name="territory_create"),
    path("territories/<int:pk>/", views.territory_detail, name="territory_detail"),
    path("territories/<int:pk>/edit/", views.territory_edit, name="territory_edit"),
    path("territories/<int:pk>/delete/", views.territory_delete, name="territory_delete"),

    # Territory Assignment & Rebalancing
    path("assignments/", views.territoryassignment_list, name="territoryassignment_list"),
    path("assignments/add/", views.territoryassignment_create, name="territoryassignment_create"),
    path("assignments/<int:pk>/", views.territoryassignment_detail, name="territoryassignment_detail"),
    path("assignments/<int:pk>/edit/", views.territoryassignment_edit, name="territoryassignment_edit"),
    path("assignments/<int:pk>/delete/", views.territoryassignment_delete, name="territoryassignment_delete"),

    # Quota Planning & Allocation
    path("quota-plans/", views.quotaplan_list, name="quotaplan_list"),
    path("quota-plans/add/", views.quotaplan_create, name="quotaplan_create"),
    path("quota-plans/<int:pk>/", views.quotaplan_detail, name="quotaplan_detail"),
    path("quota-plans/<int:pk>/edit/", views.quotaplan_edit, name="quotaplan_edit"),
    path("quota-plans/<int:pk>/delete/", views.quotaplan_delete, name="quotaplan_delete"),

    # Coverage Model Optimization
    path("coverage-models/", views.coveragemodel_list, name="coveragemodel_list"),
    path("coverage-models/add/", views.coveragemodel_create, name="coveragemodel_create"),
    path("coverage-models/<int:pk>/", views.coveragemodel_detail, name="coveragemodel_detail"),
    path("coverage-models/<int:pk>/edit/", views.coveragemodel_edit, name="coveragemodel_edit"),
    path("coverage-models/<int:pk>/delete/", views.coveragemodel_delete, name="coveragemodel_delete"),

    # Territory Performance Analytics
    path("performance/", views.territoryperformance_list, name="territoryperformance_list"),
    path("performance/add/", views.territoryperformance_create, name="territoryperformance_create"),
    path("performance/<int:pk>/", views.territoryperformance_detail, name="territoryperformance_detail"),
    path("performance/<int:pk>/edit/", views.territoryperformance_edit, name="territoryperformance_edit"),
    path("performance/<int:pk>/delete/", views.territoryperformance_delete, name="territoryperformance_delete"),
]
