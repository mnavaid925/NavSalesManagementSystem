from django.urls import path

from . import views

app_name = "activities"

urlpatterns = [
    # Activity Logging & Tracking
    path("activities/", views.activity_list, name="activity_list"),
    path("activities/add/", views.activity_create, name="activity_create"),
    path("activities/<int:pk>/", views.activity_detail, name="activity_detail"),
    path("activities/<int:pk>/edit/", views.activity_edit, name="activity_edit"),
    path("activities/<int:pk>/delete/", views.activity_delete, name="activity_delete"),

    # Task & Follow-up Management
    path("tasks/", views.salestask_list, name="salestask_list"),
    path("tasks/add/", views.salestask_create, name="salestask_create"),
    path("tasks/<int:pk>/", views.salestask_detail, name="salestask_detail"),
    path("tasks/<int:pk>/edit/", views.salestask_edit, name="salestask_edit"),
    path("tasks/<int:pk>/delete/", views.salestask_delete, name="salestask_delete"),

    # Calendar & Meeting Scheduling
    path("meetings/", views.meeting_list, name="meeting_list"),
    path("meetings/add/", views.meeting_create, name="meeting_create"),
    path("meetings/<int:pk>/", views.meeting_detail, name="meeting_detail"),
    path("meetings/<int:pk>/edit/", views.meeting_edit, name="meeting_edit"),
    path("meetings/<int:pk>/delete/", views.meeting_delete, name="meeting_delete"),

    # Email Integration & Tracking
    path("emails/", views.emaillog_list, name="emaillog_list"),
    path("emails/add/", views.emaillog_create, name="emaillog_create"),
    path("emails/<int:pk>/", views.emaillog_detail, name="emaillog_detail"),
    path("emails/<int:pk>/edit/", views.emaillog_edit, name="emaillog_edit"),
    path("emails/<int:pk>/delete/", views.emaillog_delete, name="emaillog_delete"),

    # Daily/Weekly Sales Planning
    path("plans/", views.salesplan_list, name="salesplan_list"),
    path("plans/add/", views.salesplan_create, name="salesplan_create"),
    path("plans/<int:pk>/", views.salesplan_detail, name="salesplan_detail"),
    path("plans/<int:pk>/edit/", views.salesplan_edit, name="salesplan_edit"),
    path("plans/<int:pk>/delete/", views.salesplan_delete, name="salesplan_delete"),
]
