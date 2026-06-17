from django.urls import path

from . import views

app_name = "opportunities"

urlpatterns = [
    # Pipeline stages
    path("stages/", views.pipelinestage_list, name="pipelinestage_list"),
    path("stages/add/", views.pipelinestage_create, name="pipelinestage_create"),
    path("stages/<int:pk>/", views.pipelinestage_detail, name="pipelinestage_detail"),
    path("stages/<int:pk>/edit/", views.pipelinestage_edit, name="pipelinestage_edit"),
    path("stages/<int:pk>/delete/", views.pipelinestage_delete, name="pipelinestage_delete"),

    # Opportunities
    path("opportunities/", views.opportunity_list, name="opportunity_list"),
    path("opportunities/add/", views.opportunity_create, name="opportunity_create"),
    path("opportunities/<int:pk>/", views.opportunity_detail, name="opportunity_detail"),
    path("opportunities/<int:pk>/edit/", views.opportunity_edit, name="opportunity_edit"),
    path("opportunities/<int:pk>/delete/", views.opportunity_delete, name="opportunity_delete"),

    # Opportunity activities
    path("activities/", views.opportunityactivity_list, name="opportunityactivity_list"),
    path("activities/add/", views.opportunityactivity_create, name="opportunityactivity_create"),
    path("activities/<int:pk>/", views.opportunityactivity_detail, name="opportunityactivity_detail"),
    path("activities/<int:pk>/edit/", views.opportunityactivity_edit, name="opportunityactivity_edit"),
    path("activities/<int:pk>/delete/", views.opportunityactivity_delete, name="opportunityactivity_delete"),

    # Competitors
    path("competitors/", views.competitor_list, name="competitor_list"),
    path("competitors/add/", views.competitor_create, name="competitor_create"),
    path("competitors/<int:pk>/", views.competitor_detail, name="competitor_detail"),
    path("competitors/<int:pk>/edit/", views.competitor_edit, name="competitor_edit"),
    path("competitors/<int:pk>/delete/", views.competitor_delete, name="competitor_delete"),

    # Deal collaborators
    path("collaborators/", views.dealcollaborator_list, name="dealcollaborator_list"),
    path("collaborators/add/", views.dealcollaborator_create, name="dealcollaborator_create"),
    path("collaborators/<int:pk>/", views.dealcollaborator_detail, name="dealcollaborator_detail"),
    path("collaborators/<int:pk>/edit/", views.dealcollaborator_edit, name="dealcollaborator_edit"),
    path("collaborators/<int:pk>/delete/", views.dealcollaborator_delete, name="dealcollaborator_delete"),
]
