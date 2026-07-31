from django.contrib import admin
from .models import Customer, DeliveryCompany, Order, OrderItem, OrderLog

# Register your models here.
admin.site.register(Customer)
admin.site.register(DeliveryCompany)
admin.site.register(OrderItem)


@admin.register(OrderLog)
class OrderLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "event_type",
        "previous_status",
        "new_status",
        "created_by",
        "updated_at",
    )
    list_filter = ("event_type", "new_status", "updated_at")
    search_fields = (
        "order__id",
        "customer__name",
        "created_by__username",
    )
    readonly_fields = (
        "order",
        "customer",
        "event_type",
        "previous_status",
        "new_status",
        "created_by",
        "changes",
        "created_at",
        "updated_at",
    )

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


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
