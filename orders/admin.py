from django.contrib import admin
from .models import OrderStatus, Customer, Order, OrderItem

# Register your models here.
admin.site.register(OrderStatus)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderItem)
