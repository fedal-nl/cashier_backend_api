"""
This module contains the business logic for creating orders and handling order-related operations. 
It provides a service function to create an order along with its items and modifications, calculating the 
total price accordingly.
Instead of logic in the serializers, we keep it here to maintain separation of concerns and keep the serializers
simple and focused on data validation and transformation.
"""
from decimal import Decimal

from .models import Order, OrderItem, OrderItemModification


def create_order(*, customer, status, items_data, note=None) -> Order:
    """Creates an order with the given customer, status, items data, and an optional note.
       The items_data should be a list of dictionaries, each containing:
        - menu_item: the MenuItem instance being ordered
        - name_ar: the Arabic name of the menu item (snapshot)
        - base_price: the base price of the menu item at the time of order
        - quantity: the quantity of this menu item being ordered
        - modifications: a list of modifications (optional), where each modification is a dictionary containing:
        - ingredient: the Ingredient instance being added or removed
        - name_ar: the Arabic name of the ingredient (snapshot)
        - type: the type of modification ('added' or 'removed')
    """
    order = Order.objects.create(
        customer=customer,
        status=status,
        note=note or "",
        total_price=0
    )

    total_order_price = Decimal("0.00")

    for item in items_data:
        base_price = Decimal(item["base_price"])
        quantity = item["quantity"]

        total_price = base_price * quantity

        order_item = OrderItem.objects.create(
            order=order,
            menu_item=item["menu_item"],
            menu_item_name_ar=item["name_ar"],
            menu_item_base_price=base_price,
            quantity=quantity,
            total_price=total_price,
            order_item_note=item.get("order_item_note", "")
        )

        # handle modifications and add their price to the total price of the order item based on the quantity
        for mod in item.get("modifications", []):
            if not mod.get("ingredient"):
                continue  # skip modifications that don't have an ingredient
            ingredient = mod.get("ingredient")
            mod_quantity = mod.get("quantity", 1)

            OrderItemModification.objects.create(
                order_item=order_item,
                ingredient=ingredient,
                ingredient_name_ar=mod["name_ar"],
                ingredient_price=ingredient.price,
                modification_type=mod["type"],
                quantity=mod_quantity
            )
            if mod["type"] == "added":
                total_price += ingredient.price * mod_quantity
            elif mod["type"] == "removed":
                total_price -= ingredient.price * mod_quantity

        total_order_price += total_price

    order.total_price = total_order_price
    order.save()

    return order
