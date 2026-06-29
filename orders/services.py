"""
This module contains the business logic for creating orders and handling order-related operations.
It provides a service function to create an order along with its items and modifications, calculating the
total price accordingly.
Instead of logic in the serializers, we keep it here to maintain separation of concerns and keep the serializers
simple and focused on data validation and transformation.
"""

from decimal import Decimal

from .models import Order, OrderItem, OrderItemModification, OrderLog


def replace_order_items(*, order, items_data) -> None:
    order.items.all().delete()
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
            order_item_note=item.get("order_item_note", ""),
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
                quantity=mod_quantity,
            )
            if mod["type"] == "added":
                total_price += ingredient.price * mod_quantity
            elif mod["type"] == "removed":
                total_price -= ingredient.price * mod_quantity

        order_item.total_price = total_price
        order_item.save(update_fields=["total_price", "updated_at"])
        total_order_price += total_price

    order.total_price = total_order_price
    order.save(update_fields=["total_price", "updated_at"])


def create_order(
    *,
    customer,
    branch,
    status,
    items_data,
    note=None,
    delivery_company=None,
    order_type=Order.OrderType.DELIVERY,
    user=None,
) -> Order:
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
        branch=branch,
        delivery_company=delivery_company,
        order_type=order_type,
        status=status,
        note=note or "",
        total_price=0,
    )

    replace_order_items(
        order=order,
        items_data=items_data,
    )
    order.save()
    create_order_log(
        order=order,
        event_type=OrderLog.EventType.CREATED,
        new_status=order.status,
        user=user,
    )

    return order


def update_order_status(*, order, status, delivery_company=None, user=None) -> Order:
    previous_status = order.status
    order.status = status

    if delivery_company is not None:
        order.delivery_company = delivery_company

    order.save()

    create_order_log(
        order=order,
        event_type=OrderLog.EventType.STATUS_UPDATED,
        previous_status=previous_status,
        new_status=order.status,
        user=user,
    )

    return order


def create_order_log(
    *, order, event_type, new_status, previous_status=None, user=None
) -> OrderLog:
    if user is not None and not getattr(user, "is_authenticated", False):
        user = None

    return OrderLog.objects.create(
        order=order,
        customer=order.customer,
        event_type=event_type,
        previous_status=previous_status,
        new_status=new_status,
        created_by=user,
    )
