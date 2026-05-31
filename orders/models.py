from decimal import Decimal

from django.db import models
import uuid
from typing import TYPE_CHECKING
if TYPE_CHECKING:  # pragma: no cover
    from django.db.models import Manager


# TODO: Move the customer model to a separate app called "customers" and link it to orders via a ForeignKey. 
# This will allow us to manage customers independently and reuse the customer model in other parts of the system if needed.
class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, blank=True, null=True, verbose_name="البريد الإلكتروني")
    phone_number = models.CharField(max_length=20, blank=True, null=True, unique=True, verbose_name="رقم الهاتف")
    address = models.TextField(blank=True, null=True, verbose_name="العنوان")

    # make the default ordering by id
    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.name} - {self.email}"

class Order(models.Model):
    """The Order model represents a customer's order in the system."""
    # Make the order status enum class instead of a separate model, since it has a fixed set of values and doesn't require additional fields.
    class OrderStatus(models.TextChoices):
        CREATED = 'created', 'تم الإنشاء'
        PREPARING = 'preparing', 'قيد التحضير'
        READY = 'ready', 'جاهز للاستلام'
        COMPLETED = 'completed', 'مكتمل'
        CANCELLED = 'cancelled', 'ملغي'
        PAID = 'paid', 'مدفوع'
        PICKED_UP = 'picked_up', 'تم الاستلام'
        DELIVERED = 'delivered', 'تم التوصيل'

    if TYPE_CHECKING:  # pragma: no cover
        items: Manager['OrderItem']

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    note = models.TextField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.CREATED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # make the default ordering by id
    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"Order #{self.id} - {self.customer.name} - {self.status}"
    
class OrderItem(models.Model):
    """The OrderItem model represents an item in a customer's order."""

    if TYPE_CHECKING:  # pragma: no cover
        modifications: Manager['OrderItemModification']

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey('menu.MenuItem', on_delete=models.CASCADE)
    # these are snapshot fields to store the menu item details at the time of order,
    # in case they change later.
    menu_item_name_ar = models.CharField(max_length=100)
    menu_item_base_price = models.DecimalField(max_digits=10, decimal_places=2)

    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_item_note = models.TextField(blank=True, null=True)

    # make the default ordering by id
    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.quantity} x {self.menu_item_name_ar} - ${self.total_price}"
    
class OrderItemModification(models.Model):
    """The OrderItemModification model represents a modification to an order item, such as added or removed ingredients."""
    class Actions(models.TextChoices):
        ADDED = 'added', '+'
        REMOVED = 'removed', '-'

    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.CASCADE,
        related_name='modifications'
    )
    ingredient = models.ForeignKey('menu.Ingredient', on_delete=models.CASCADE)
    # snapshot fields to store the ingredient details at the time of modification
    ingredient_name_ar = models.CharField(max_length=100) 
    ingredient_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    quantity = models.PositiveIntegerField(default=1)

    modification_type = models.CharField(max_length=20)  # e.g., 'added', 'removed'

    # make the default ordering by id
    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.modification_type.capitalize()} {self.ingredient_name_ar}"
