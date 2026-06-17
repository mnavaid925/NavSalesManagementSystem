from django.urls import path

from . import views

app_name = "enablement"

urlpatterns = [
    # Content Repository & Search
    path("content/", views.contentasset_list, name="contentasset_list"),
    path("content/add/", views.contentasset_create, name="contentasset_create"),
    path("content/<int:pk>/", views.contentasset_detail, name="contentasset_detail"),
    path("content/<int:pk>/edit/", views.contentasset_edit, name="contentasset_edit"),
    path("content/<int:pk>/delete/", views.contentasset_delete, name="contentasset_delete"),

    # Sales Playbooks & Guidance
    path("playbooks/", views.playbook_list, name="playbook_list"),
    path("playbooks/add/", views.playbook_create, name="playbook_create"),
    path("playbooks/<int:pk>/", views.playbook_detail, name="playbook_detail"),
    path("playbooks/<int:pk>/edit/", views.playbook_edit, name="playbook_edit"),
    path("playbooks/<int:pk>/delete/", views.playbook_delete, name="playbook_delete"),

    # Training & Certification Tracking
    path("training/", views.trainingrecord_list, name="trainingrecord_list"),
    path("training/add/", views.trainingrecord_create, name="trainingrecord_create"),
    path("training/<int:pk>/", views.trainingrecord_detail, name="trainingrecord_detail"),
    path("training/<int:pk>/edit/", views.trainingrecord_edit, name="trainingrecord_edit"),
    path("training/<int:pk>/delete/", views.trainingrecord_delete, name="trainingrecord_delete"),

    # Coaching & Call Recording
    path("calls/", views.callrecording_list, name="callrecording_list"),
    path("calls/add/", views.callrecording_create, name="callrecording_create"),
    path("calls/<int:pk>/", views.callrecording_detail, name="callrecording_detail"),
    path("calls/<int:pk>/edit/", views.callrecording_edit, name="callrecording_edit"),
    path("calls/<int:pk>/delete/", views.callrecording_delete, name="callrecording_delete"),

    # Competitive Intelligence Library
    path("battlecards/", views.competitivecard_list, name="competitivecard_list"),
    path("battlecards/add/", views.competitivecard_create, name="competitivecard_create"),
    path("battlecards/<int:pk>/", views.competitivecard_detail, name="competitivecard_detail"),
    path("battlecards/<int:pk>/edit/", views.competitivecard_edit, name="competitivecard_edit"),
    path("battlecards/<int:pk>/delete/", views.competitivecard_delete, name="competitivecard_delete"),
]
