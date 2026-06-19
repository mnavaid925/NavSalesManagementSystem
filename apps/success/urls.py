from django.urls import path

from . import views

app_name = "success"

urlpatterns = [
    # Health Scoring & Risk Alerts
    path("health-scores/", views.healthscore_list, name="healthscore_list"),
    path("health-scores/add/", views.healthscore_create, name="healthscore_create"),
    path("health-scores/<int:pk>/", views.healthscore_detail, name="healthscore_detail"),
    path("health-scores/<int:pk>/edit/", views.healthscore_edit, name="healthscore_edit"),
    path("health-scores/<int:pk>/delete/", views.healthscore_delete, name="healthscore_delete"),

    # Renewal & Expansion Pipeline
    path("renewals/", views.renewal_list, name="renewal_list"),
    path("renewals/add/", views.renewal_create, name="renewal_create"),
    path("renewals/<int:pk>/", views.renewal_detail, name="renewal_detail"),
    path("renewals/<int:pk>/edit/", views.renewal_edit, name="renewal_edit"),
    path("renewals/<int:pk>/delete/", views.renewal_delete, name="renewal_delete"),

    # Onboarding & Implementation
    path("onboarding/", views.onboardingplan_list, name="onboardingplan_list"),
    path("onboarding/add/", views.onboardingplan_create, name="onboardingplan_create"),
    path("onboarding/<int:pk>/", views.onboardingplan_detail, name="onboardingplan_detail"),
    path("onboarding/<int:pk>/edit/", views.onboardingplan_edit, name="onboardingplan_edit"),
    path("onboarding/<int:pk>/delete/", views.onboardingplan_delete, name="onboardingplan_delete"),

    # Advocacy & Reference Management
    path("advocacy/", views.advocacy_list, name="advocacy_list"),
    path("advocacy/add/", views.advocacy_create, name="advocacy_create"),
    path("advocacy/<int:pk>/", views.advocacy_detail, name="advocacy_detail"),
    path("advocacy/<int:pk>/edit/", views.advocacy_edit, name="advocacy_edit"),
    path("advocacy/<int:pk>/delete/", views.advocacy_delete, name="advocacy_delete"),

    # Quarterly Business Reviews (QBRs)
    path("qbrs/", views.qbr_list, name="qbr_list"),
    path("qbrs/add/", views.qbr_create, name="qbr_create"),
    path("qbrs/<int:pk>/", views.qbr_detail, name="qbr_detail"),
    path("qbrs/<int:pk>/edit/", views.qbr_edit, name="qbr_edit"),
    path("qbrs/<int:pk>/delete/", views.qbr_delete, name="qbr_delete"),
]
