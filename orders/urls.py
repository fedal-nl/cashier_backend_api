from django.urls import path
from .views import CustomerCreateView, CustomerListView, OrderCreateView

urlpatterns = [
    path("", OrderCreateView.as_view(), name="create-order"),
    path("customers/", CustomerCreateView.as_view(), name="create-customer"),
    path("customers/list/", CustomerListView.as_view(), name="list-customers"),
]
