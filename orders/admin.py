from django.contrib import admin
from .models import Customer, DeliveryCompany, Order, OrderItem, OrderLog

# Register your models here.
admin.site.register(Customer)
admin.site.register(DeliveryCompany)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrderLog)
