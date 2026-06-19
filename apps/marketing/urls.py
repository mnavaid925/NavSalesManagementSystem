from django.urls import path

from . import views

app_name = "marketing"

urlpatterns = [
    # Campaign Influence & Attribution
    path("influence/", views.campaigninfluence_list, name="campaigninfluence_list"),
    path("influence/add/", views.campaigninfluence_create, name="campaigninfluence_create"),
    path("influence/<int:pk>/", views.campaigninfluence_detail, name="campaigninfluence_detail"),
    path("influence/<int:pk>/edit/", views.campaigninfluence_edit, name="campaigninfluence_edit"),
    path("influence/<int:pk>/delete/", views.campaigninfluence_delete, name="campaigninfluence_delete"),

    # MQL-to-SQL Tracking
    path("mql/", views.mqlhandoff_list, name="mqlhandoff_list"),
    path("mql/add/", views.mqlhandoff_create, name="mqlhandoff_create"),
    path("mql/<int:pk>/", views.mqlhandoff_detail, name="mqlhandoff_detail"),
    path("mql/<int:pk>/edit/", views.mqlhandoff_edit, name="mqlhandoff_edit"),
    path("mql/<int:pk>/delete/", views.mqlhandoff_delete, name="mqlhandoff_delete"),

    # Campaign Performance Integration
    path("performance/", views.campaignperformance_list, name="campaignperformance_list"),
    path("performance/add/", views.campaignperformance_create, name="campaignperformance_create"),
    path("performance/<int:pk>/", views.campaignperformance_detail, name="campaignperformance_detail"),
    path("performance/<int:pk>/edit/", views.campaignperformance_edit, name="campaignperformance_edit"),
    path("performance/<int:pk>/delete/", views.campaignperformance_delete, name="campaignperformance_delete"),

    # Content Performance & Engagement
    path("content/", views.contentengagement_list, name="contentengagement_list"),
    path("content/add/", views.contentengagement_create, name="contentengagement_create"),
    path("content/<int:pk>/", views.contentengagement_detail, name="contentengagement_detail"),
    path("content/<int:pk>/edit/", views.contentengagement_edit, name="contentengagement_edit"),
    path("content/<int:pk>/delete/", views.contentengagement_delete, name="contentengagement_delete"),

    # Event & Webinar Management
    path("events/", views.marketingevent_list, name="marketingevent_list"),
    path("events/add/", views.marketingevent_create, name="marketingevent_create"),
    path("events/<int:pk>/", views.marketingevent_detail, name="marketingevent_detail"),
    path("events/<int:pk>/edit/", views.marketingevent_edit, name="marketingevent_edit"),
    path("events/<int:pk>/delete/", views.marketingevent_delete, name="marketingevent_delete"),
]
