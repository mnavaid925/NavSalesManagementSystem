from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    # Orders
    path("orders/", views.order_list, name="order_list"),
    path("orders/add/", views.order_create, name="order_create"),
    path("orders/<int:pk>/", views.order_detail, name="order_detail"),
    path("orders/<int:pk>/edit/", views.order_edit, name="order_edit"),
    path("orders/<int:pk>/delete/", views.order_delete, name="order_delete"),

    # Order lines
    path("lines/", views.orderline_list, name="orderline_list"),
    path("lines/add/", views.orderline_create, name="orderline_create"),
    path("lines/<int:pk>/", views.orderline_detail, name="orderline_detail"),
    path("lines/<int:pk>/edit/", views.orderline_edit, name="orderline_edit"),
    path("lines/<int:pk>/delete/", views.orderline_delete, name="orderline_delete"),

    # Fulfillments
    path("fulfillments/", views.fulfillment_list, name="fulfillment_list"),
    path("fulfillments/add/", views.fulfillment_create, name="fulfillment_create"),
    path("fulfillments/<int:pk>/", views.fulfillment_detail, name="fulfillment_detail"),
    path("fulfillments/<int:pk>/edit/", views.fulfillment_edit, name="fulfillment_edit"),
    path("fulfillments/<int:pk>/delete/", views.fulfillment_delete, name="fulfillment_delete"),

    # Amendments
    path("amendments/", views.orderamendment_list, name="orderamendment_list"),
    path("amendments/add/", views.orderamendment_create, name="orderamendment_create"),
    path("amendments/<int:pk>/", views.orderamendment_detail, name="orderamendment_detail"),
    path("amendments/<int:pk>/edit/", views.orderamendment_edit, name="orderamendment_edit"),
    path("amendments/<int:pk>/delete/", views.orderamendment_delete, name="orderamendment_delete"),

    # Revenue schedules
    path("revenue/", views.revenueschedule_list, name="revenueschedule_list"),
    path("revenue/add/", views.revenueschedule_create, name="revenueschedule_create"),
    path("revenue/<int:pk>/", views.revenueschedule_detail, name="revenueschedule_detail"),
    path("revenue/<int:pk>/edit/", views.revenueschedule_edit, name="revenueschedule_edit"),
    path("revenue/<int:pk>/delete/", views.revenueschedule_delete, name="revenueschedule_delete"),
]
