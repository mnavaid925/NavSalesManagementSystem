from django.urls import path

from . import views

app_name = "tenants"

urlpatterns = [
    path("", views.overview, name="overview"),

    # Tenant Onboarding
    path("onboarding/", views.onboardingstep_list, name="onboardingstep_list"),
    path("onboarding/add/", views.onboardingstep_create, name="onboardingstep_create"),
    path("onboarding/<int:pk>/", views.onboardingstep_detail, name="onboardingstep_detail"),
    path("onboarding/<int:pk>/edit/", views.onboardingstep_edit, name="onboardingstep_edit"),
    path("onboarding/<int:pk>/delete/", views.onboardingstep_delete, name="onboardingstep_delete"),

    # Subscriptions
    path("subscriptions/", views.subscription_list, name="subscription_list"),
    path("subscriptions/add/", views.subscription_create, name="subscription_create"),
    path("subscriptions/<int:pk>/", views.subscription_detail, name="subscription_detail"),
    path("subscriptions/<int:pk>/edit/", views.subscription_edit, name="subscription_edit"),
    path("subscriptions/<int:pk>/delete/", views.subscription_delete, name="subscription_delete"),

    # Invoices
    path("invoices/", views.invoice_list, name="invoice_list"),
    path("invoices/add/", views.invoice_create, name="invoice_create"),
    path("invoices/<int:pk>/", views.invoice_detail, name="invoice_detail"),
    path("invoices/<int:pk>/edit/", views.invoice_edit, name="invoice_edit"),
    path("invoices/<int:pk>/delete/", views.invoice_delete, name="invoice_delete"),

    # Encryption keys
    path("security/keys/", views.encryptionkey_list, name="encryptionkey_list"),
    path("security/keys/add/", views.encryptionkey_create, name="encryptionkey_create"),
    path("security/keys/<int:pk>/", views.encryptionkey_detail, name="encryptionkey_detail"),
    path("security/keys/<int:pk>/edit/", views.encryptionkey_edit, name="encryptionkey_edit"),
    path("security/keys/<int:pk>/rotate/", views.encryptionkey_rotate, name="encryptionkey_rotate"),
    path("security/keys/<int:pk>/delete/", views.encryptionkey_delete, name="encryptionkey_delete"),

    # Branding
    path("branding/", views.brandingsetting_list, name="brandingsetting_list"),
    path("branding/add/", views.brandingsetting_create, name="brandingsetting_create"),
    path("branding/<int:pk>/", views.brandingsetting_detail, name="brandingsetting_detail"),
    path("branding/<int:pk>/edit/", views.brandingsetting_edit, name="brandingsetting_edit"),
    path("branding/<int:pk>/delete/", views.brandingsetting_delete, name="brandingsetting_delete"),

    # Health metrics
    path("health/", views.healthmetric_list, name="healthmetric_list"),
    path("health/add/", views.healthmetric_create, name="healthmetric_create"),
    path("health/<int:pk>/", views.healthmetric_detail, name="healthmetric_detail"),
    path("health/<int:pk>/edit/", views.healthmetric_edit, name="healthmetric_edit"),
    path("health/<int:pk>/delete/", views.healthmetric_delete, name="healthmetric_delete"),
]
