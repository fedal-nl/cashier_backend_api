from django.urls import path
from .views import (
    CustomerCreateView, 
    CustomerListView, 
    OrderCreateView,
    OrderListView,
    OrderDetailView,
    OrderStatusUpdateView,
)
urlpatterns = [
    path("", OrderCreateView.as_view(), name="create-order"),
    path("customers/", CustomerCreateView.as_view(), name="create-customer"),
    path("customers/list/", CustomerListView.as_view(), name="list-customers"),
    path("list/", OrderListView.as_view(), name="list-orders"),
    path("<uuid:pk>/", OrderDetailView.as_view()),
    path("<uuid:pk>/status/", OrderStatusUpdateView.as_view()),
]
