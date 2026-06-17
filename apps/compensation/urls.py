from django.urls import path

from . import views

app_name = "compensation"

urlpatterns = [
    # Commission Plan Design
    path("plans/", views.commissionplan_list, name="commissionplan_list"),
    path("plans/add/", views.commissionplan_create, name="commissionplan_create"),
    path("plans/<int:pk>/", views.commissionplan_detail, name="commissionplan_detail"),
    path("plans/<int:pk>/edit/", views.commissionplan_edit, name="commissionplan_edit"),
    path("plans/<int:pk>/delete/", views.commissionplan_delete, name="commissionplan_delete"),

    # Real-Time Earnings Tracking
    path("earnings/", views.earning_list, name="earning_list"),
    path("earnings/add/", views.earning_create, name="earning_create"),
    path("earnings/<int:pk>/", views.earning_detail, name="earning_detail"),
    path("earnings/<int:pk>/edit/", views.earning_edit, name="earning_edit"),
    path("earnings/<int:pk>/delete/", views.earning_delete, name="earning_delete"),

    # Clawbacks & Adjustments
    path("clawbacks/", views.clawback_list, name="clawback_list"),
    path("clawbacks/add/", views.clawback_create, name="clawback_create"),
    path("clawbacks/<int:pk>/", views.clawback_detail, name="clawback_detail"),
    path("clawbacks/<int:pk>/edit/", views.clawback_edit, name="clawback_edit"),
    path("clawbacks/<int:pk>/delete/", views.clawback_delete, name="clawback_delete"),

    # Multi-Currency & Global Plans
    path("global-plans/", views.globalplanvariation_list, name="globalplanvariation_list"),
    path("global-plans/add/", views.globalplanvariation_create, name="globalplanvariation_create"),
    path("global-plans/<int:pk>/", views.globalplanvariation_detail, name="globalplanvariation_detail"),
    path("global-plans/<int:pk>/edit/", views.globalplanvariation_edit, name="globalplanvariation_edit"),
    path("global-plans/<int:pk>/delete/", views.globalplanvariation_delete, name="globalplanvariation_delete"),

    # Payout Processing & Integration
    path("payouts/", views.payout_list, name="payout_list"),
    path("payouts/add/", views.payout_create, name="payout_create"),
    path("payouts/<int:pk>/", views.payout_detail, name="payout_detail"),
    path("payouts/<int:pk>/edit/", views.payout_edit, name="payout_edit"),
    path("payouts/<int:pk>/delete/", views.payout_delete, name="payout_delete"),
]
