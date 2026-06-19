from django.urls import path

from . import views

app_name = "masterdata"

urlpatterns = [
    # Product Catalog & Pricing
    path("products/", views.productcatalog_list, name="productcatalog_list"),
    path("products/add/", views.productcatalog_create, name="productcatalog_create"),
    path("products/<int:pk>/", views.productcatalog_detail, name="productcatalog_detail"),
    path("products/<int:pk>/edit/", views.productcatalog_edit, name="productcatalog_edit"),
    path("products/<int:pk>/delete/", views.productcatalog_delete, name="productcatalog_delete"),

    # Custom Fields & Objects
    path("custom-fields/", views.customfield_list, name="customfield_list"),
    path("custom-fields/add/", views.customfield_create, name="customfield_create"),
    path("custom-fields/<int:pk>/", views.customfield_detail, name="customfield_detail"),
    path("custom-fields/<int:pk>/edit/", views.customfield_edit, name="customfield_edit"),
    path("custom-fields/<int:pk>/delete/", views.customfield_delete, name="customfield_delete"),

    # Sales Methodology Configuration
    path("methodologies/", views.methodologyconfig_list, name="methodologyconfig_list"),
    path("methodologies/add/", views.methodologyconfig_create, name="methodologyconfig_create"),
    path("methodologies/<int:pk>/", views.methodologyconfig_detail, name="methodologyconfig_detail"),
    path("methodologies/<int:pk>/edit/", views.methodologyconfig_edit, name="methodologyconfig_edit"),
    path("methodologies/<int:pk>/delete/", views.methodologyconfig_delete, name="methodologyconfig_delete"),

    # Price Books
    path("price-books/", views.pricebook_list, name="pricebook_list"),
    path("price-books/add/", views.pricebook_create, name="pricebook_create"),
    path("price-books/<int:pk>/", views.pricebook_detail, name="pricebook_detail"),
    path("price-books/<int:pk>/edit/", views.pricebook_edit, name="pricebook_edit"),
    path("price-books/<int:pk>/delete/", views.pricebook_delete, name="pricebook_delete"),

    # Localization & Multi-Language
    path("localization/", views.localizationsetting_list, name="localizationsetting_list"),
    path("localization/add/", views.localizationsetting_create, name="localizationsetting_create"),
    path("localization/<int:pk>/", views.localizationsetting_detail, name="localizationsetting_detail"),
    path("localization/<int:pk>/edit/", views.localizationsetting_edit, name="localizationsetting_edit"),
    path("localization/<int:pk>/delete/", views.localizationsetting_delete, name="localizationsetting_delete"),
]
