from django.test import TestCase

from orders.services import create_order
from orders.models import OrderStatus, Customer
from menu.models import Category, Quantity, MenuItem, Ingredient


class OrderServiceTest(TestCase):

    def setUp(self):
        self.customer = Customer.objects.create(
            name="Omar",
            email="omar@test.com"
        )

        self.status = OrderStatus.objects.create(
            name_en="Created",
            name_ar="تم الإنشاء"
        )

        self.category = Category.objects.create(
            name_en="Food",
            name_ar="طعام"
        )

        self.quantity = Quantity.objects.create(
            name_en="Regular",
            name_ar="عادي"
        )

        self.menu_item = MenuItem.objects.create(
            name_en="Burger",
            name_ar="برجر",
            price=10,
            category=self.category,
            quantity=self.quantity
        )

        self.ingredient = Ingredient.objects.create(
            name_en="Cheese",
            name_ar="جبنة"
        )

    def test_create_order_with_items(self):
        order = create_order(
            customer=self.customer,
            status=self.status,
            items_data=[
                {
                    "menu_item": self.menu_item,
                    "name_en": "Burger",
                    "name_ar": "برجر",
                    "base_price": 10,
                    "quantity": 2,
                    "modifications": [
                        {
                            "ingredient": self.ingredient,
                            "name_en": "Cheese",
                            "name_ar": "جبنة",
                            "type": "added"
                        }
                    ]
                }
            ]
        )

        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.total_price, 20)
        item = order.items.first()
        assert item is not None
        self.assertEqual(item.modifications.count(), 1)
