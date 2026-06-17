from django.urls import path

from . import views

app_name = "crm"

urlpatterns = [
    # Accounts (Account Hierarchy & Parent-Child)
    path("accounts/", views.account_list, name="account_list"),
    path("accounts/add/", views.account_create, name="account_create"),
    path("accounts/<int:pk>/", views.account_detail, name="account_detail"),
    path("accounts/<int:pk>/edit/", views.account_edit, name="account_edit"),
    path("accounts/<int:pk>/delete/", views.account_delete, name="account_delete"),

    # Contacts (Contact Profiles & Enrichment)
    path("contacts/", views.contact_list, name="contact_list"),
    path("contacts/add/", views.contact_create, name="contact_create"),
    path("contacts/<int:pk>/", views.contact_detail, name="contact_detail"),
    path("contacts/<int:pk>/edit/", views.contact_edit, name="contact_edit"),
    path("contacts/<int:pk>/delete/", views.contact_delete, name="contact_delete"),

    # Relationship maps (Relationship Mapping)
    path("relationships/", views.relationshipmap_list, name="relationshipmap_list"),
    path("relationships/add/", views.relationshipmap_create, name="relationshipmap_create"),
    path("relationships/<int:pk>/", views.relationshipmap_detail, name="relationshipmap_detail"),
    path("relationships/<int:pk>/edit/", views.relationshipmap_edit, name="relationshipmap_edit"),
    path("relationships/<int:pk>/delete/", views.relationshipmap_delete, name="relationshipmap_delete"),

    # Account tiers (Account Segmentation & Tiering)
    path("tiers/", views.accounttier_list, name="accounttier_list"),
    path("tiers/add/", views.accounttier_create, name="accounttier_create"),
    path("tiers/<int:pk>/", views.accounttier_detail, name="accounttier_detail"),
    path("tiers/<int:pk>/edit/", views.accounttier_edit, name="accounttier_edit"),
    path("tiers/<int:pk>/delete/", views.accounttier_delete, name="accounttier_delete"),

    # Account plans (Account Plans & Growth Strategies)
    path("plans/", views.accountplan_list, name="accountplan_list"),
    path("plans/add/", views.accountplan_create, name="accountplan_create"),
    path("plans/<int:pk>/", views.accountplan_detail, name="accountplan_detail"),
    path("plans/<int:pk>/edit/", views.accountplan_edit, name="accountplan_edit"),
    path("plans/<int:pk>/delete/", views.accountplan_delete, name="accountplan_delete"),
]
