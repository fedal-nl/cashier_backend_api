from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple

from menu.models import MenuItem

from .models import Campaign, Customer, DeliveryCompany, Order, OrderItem, OrderLog

# Register your models here.
admin.site.register(Customer)
admin.site.register(DeliveryCompany)
admin.site.register(OrderItem)


class CampaignMenuItemChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, menu_item):
        branches = ", ".join(branch.name for branch in menu_item.branches.all())
        branches = branches or "All branches"
        return f"{menu_item.name_ar} — {menu_item.category.name_ar} — {branches}"


class CampaignAdminForm(forms.ModelForm):
    menu_items = CampaignMenuItemChoiceField(
        queryset=MenuItem.objects.select_related("category").prefetch_related("branches"),
        widget=FilteredSelectMultiple("menu items", is_stacked=False),
    )

    class Meta:
        model = Campaign
        fields = "__all__"


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    form = CampaignAdminForm
    list_display = (
        "id",
        "campaign_name",
        "channel",
        "start_date",
        "end_date",
        "amount_spent",
        "current_revenue",
        "total_orders",
        "profit",
    )
    list_filter = ("channel", "start_date", "end_date")
    search_fields = ("id", "campaign_name", "menu_items__name_ar")
    readonly_fields = ("current_revenue", "total_orders", "profit")


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
