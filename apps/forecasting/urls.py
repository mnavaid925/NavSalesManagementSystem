from django.urls import path

from . import views

app_name = "forecasting"

urlpatterns = [
    # Forecast Categories & Commitments
    path("categories/", views.forecastcategory_list, name="forecastcategory_list"),
    path("categories/add/", views.forecastcategory_create, name="forecastcategory_create"),
    path("categories/<int:pk>/", views.forecastcategory_detail, name="forecastcategory_detail"),
    path("categories/<int:pk>/edit/", views.forecastcategory_edit, name="forecastcategory_edit"),
    path("categories/<int:pk>/delete/", views.forecastcategory_delete, name="forecastcategory_delete"),

    # AI-Powered Predictive Forecasting (Forecasts)
    path("forecasts/", views.forecast_list, name="forecast_list"),
    path("forecasts/add/", views.forecast_create, name="forecast_create"),
    path("forecasts/<int:pk>/", views.forecast_detail, name="forecast_detail"),
    path("forecasts/<int:pk>/edit/", views.forecast_edit, name="forecast_edit"),
    path("forecasts/<int:pk>/delete/", views.forecast_delete, name="forecast_delete"),

    # Quota Management & Attainment
    path("quotas/", views.quota_list, name="quota_list"),
    path("quotas/add/", views.quota_create, name="quota_create"),
    path("quotas/<int:pk>/", views.quota_detail, name="quota_detail"),
    path("quotas/<int:pk>/edit/", views.quota_edit, name="quota_edit"),
    path("quotas/<int:pk>/delete/", views.quota_delete, name="quota_delete"),

    # Forecast Rollups & Adjustments
    path("adjustments/", views.forecastadjustment_list, name="forecastadjustment_list"),
    path("adjustments/add/", views.forecastadjustment_create, name="forecastadjustment_create"),
    path("adjustments/<int:pk>/", views.forecastadjustment_detail, name="forecastadjustment_detail"),
    path("adjustments/<int:pk>/edit/", views.forecastadjustment_edit, name="forecastadjustment_edit"),
    path("adjustments/<int:pk>/delete/", views.forecastadjustment_delete, name="forecastadjustment_delete"),

    # Forecast Accuracy & Variance Analysis
    path("accuracy/", views.forecastaccuracy_list, name="forecastaccuracy_list"),
    path("accuracy/add/", views.forecastaccuracy_create, name="forecastaccuracy_create"),
    path("accuracy/<int:pk>/", views.forecastaccuracy_detail, name="forecastaccuracy_detail"),
    path("accuracy/<int:pk>/edit/", views.forecastaccuracy_edit, name="forecastaccuracy_edit"),
    path("accuracy/<int:pk>/delete/", views.forecastaccuracy_delete, name="forecastaccuracy_delete"),
]
