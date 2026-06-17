from django.urls import path

from . import views

app_name = "quotes"

urlpatterns = [
    # Quotes (CPQ)
    path("quotes/", views.quote_list, name="quote_list"),
    path("quotes/add/", views.quote_create, name="quote_create"),
    path("quotes/<int:pk>/", views.quote_detail, name="quote_detail"),
    path("quotes/<int:pk>/edit/", views.quote_edit, name="quote_edit"),
    path("quotes/<int:pk>/delete/", views.quote_delete, name="quote_delete"),

    # Quote line items
    path("line-items/", views.quotelineitem_list, name="quotelineitem_list"),
    path("line-items/add/", views.quotelineitem_create, name="quotelineitem_create"),
    path("line-items/<int:pk>/", views.quotelineitem_detail, name="quotelineitem_detail"),
    path("line-items/<int:pk>/edit/", views.quotelineitem_edit, name="quotelineitem_edit"),
    path("line-items/<int:pk>/delete/", views.quotelineitem_delete, name="quotelineitem_delete"),

    # Pricing rules
    path("pricing-rules/", views.pricingrule_list, name="pricingrule_list"),
    path("pricing-rules/add/", views.pricingrule_create, name="pricingrule_create"),
    path("pricing-rules/<int:pk>/", views.pricingrule_detail, name="pricingrule_detail"),
    path("pricing-rules/<int:pk>/edit/", views.pricingrule_edit, name="pricingrule_edit"),
    path("pricing-rules/<int:pk>/delete/", views.pricingrule_delete, name="pricingrule_delete"),

    # Proposals
    path("proposals/", views.proposal_list, name="proposal_list"),
    path("proposals/add/", views.proposal_create, name="proposal_create"),
    path("proposals/<int:pk>/", views.proposal_detail, name="proposal_detail"),
    path("proposals/<int:pk>/edit/", views.proposal_edit, name="proposal_edit"),
    path("proposals/<int:pk>/delete/", views.proposal_delete, name="proposal_delete"),

    # Quote versions
    path("versions/", views.quoteversion_list, name="quoteversion_list"),
    path("versions/add/", views.quoteversion_create, name="quoteversion_create"),
    path("versions/<int:pk>/", views.quoteversion_detail, name="quoteversion_detail"),
    path("versions/<int:pk>/edit/", views.quoteversion_edit, name="quoteversion_edit"),
    path("versions/<int:pk>/delete/", views.quoteversion_delete, name="quoteversion_delete"),
]
