from django.contrib import admin
from .models import Customer, DeliveryCompany, Order, OrderItem, OrderLog

# Register your models here.
admin.site.register(Customer)
admin.site.register(DeliveryCompany)
admin.site.register(OrderItem)
admin.site.register(OrderLog)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order_type",
        "customer",
        "delivery_company",
        "status",
        "total_price",
        "created_at",
    )
    list_filter = (
        "order_type",
        "status",
        "delivery_company",
    )
    search_fields = (
        "id",
        "customer__name",
        "customer__phone_number",
    )
