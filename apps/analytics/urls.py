from django.urls import path

from . import views

app_name = "analytics"

urlpatterns = [
    # Win/Loss Analysis
    path("win-loss/", views.winlossanalysis_list, name="winlossanalysis_list"),
    path("win-loss/add/", views.winlossanalysis_create, name="winlossanalysis_create"),
    path("win-loss/<int:pk>/", views.winlossanalysis_detail, name="winlossanalysis_detail"),
    path("win-loss/<int:pk>/edit/", views.winlossanalysis_edit, name="winlossanalysis_edit"),
    path("win-loss/<int:pk>/delete/", views.winlossanalysis_delete, name="winlossanalysis_delete"),

    # Sales Velocity & Cycle Time
    path("velocity/", views.salesvelocity_list, name="salesvelocity_list"),
    path("velocity/add/", views.salesvelocity_create, name="salesvelocity_create"),
    path("velocity/<int:pk>/", views.salesvelocity_detail, name="salesvelocity_detail"),
    path("velocity/<int:pk>/edit/", views.salesvelocity_edit, name="salesvelocity_edit"),
    path("velocity/<int:pk>/delete/", views.salesvelocity_delete, name="salesvelocity_delete"),

    # Conversion Funnel Analytics
    path("funnel/", views.conversionfunnel_list, name="conversionfunnel_list"),
    path("funnel/add/", views.conversionfunnel_create, name="conversionfunnel_create"),
    path("funnel/<int:pk>/", views.conversionfunnel_detail, name="conversionfunnel_detail"),
    path("funnel/<int:pk>/edit/", views.conversionfunnel_edit, name="conversionfunnel_edit"),
    path("funnel/<int:pk>/delete/", views.conversionfunnel_delete, name="conversionfunnel_delete"),

    # Rep Performance Scorecards
    path("scorecards/", views.repscorecard_list, name="repscorecard_list"),
    path("scorecards/add/", views.repscorecard_create, name="repscorecard_create"),
    path("scorecards/<int:pk>/", views.repscorecard_detail, name="repscorecard_detail"),
    path("scorecards/<int:pk>/edit/", views.repscorecard_edit, name="repscorecard_edit"),
    path("scorecards/<int:pk>/delete/", views.repscorecard_delete, name="repscorecard_delete"),

    # Benchmarking & Peer Comparison
    path("benchmarks/", views.benchmark_list, name="benchmark_list"),
    path("benchmarks/add/", views.benchmark_create, name="benchmark_create"),
    path("benchmarks/<int:pk>/", views.benchmark_detail, name="benchmark_detail"),
    path("benchmarks/<int:pk>/edit/", views.benchmark_edit, name="benchmark_edit"),
    path("benchmarks/<int:pk>/delete/", views.benchmark_delete, name="benchmark_delete"),
]
