from django.urls import path
from .views import (
    CustomerCreateView, 
    CustomerListView, 
    CustomerSearchView,
    CustomerUpdateView,
    DeliveryCompanyListView,
    OrderCreateView,
    OrderListView,
    OrderDetailView,
    OrderStatusUpdateView,
    OrderLogListView,
)
urlpatterns = [
    path("", OrderCreateView.as_view(), name="create-order"),
    path("customers/", CustomerCreateView.as_view(), name="create-customer"),
    path("customers/list/", CustomerListView.as_view(), name="list-customers"),
    path("customers/search/", CustomerSearchView.as_view(), name="search-customer"),
    path("customers/<int:pk>/", CustomerUpdateView.as_view(), name="update-customer"),
    path("delivery-companies/", DeliveryCompanyListView.as_view(), name="list-delivery-companies"),
    path("logs/", OrderLogListView.as_view(), name="list-order-logs"),
    path("list/", OrderListView.as_view(), name="list-orders"),
    path("<uuid:pk>/", OrderDetailView.as_view()),
    path("<uuid:pk>/status/", OrderStatusUpdateView.as_view()),
]
