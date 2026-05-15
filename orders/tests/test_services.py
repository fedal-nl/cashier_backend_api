from django.test import TestCase

from orders.services import create_order
from orders.models import OrderStatus, Customer
from menu.models import Category, Unit, MenuItem, Ingredient


class OrderServiceTest(TestCase):

    def setUp(self):
        self.customer = Customer.objects.create(
            name="Omar",
            email="omar@test.com"
        )

        self.status = OrderStatus.objects.create(
            name_ar="تم الإنشاء"
        )

        self.category = Category.objects.create(
            name_ar="طعام"
        )

        self.unit = Unit.objects.create(
            name_ar="عادي"
        )

        self.menu_item = MenuItem.objects.create(
            name_ar="برجر",
            price=10,
            category=self.category,
            quantity=1,
            unit=self.unit
        )

        self.ingredient = Ingredient.objects.create(
            name_ar="جبنة",
            price=2,
            unit=self.unit
        )

    def test_create_order_with_items_without_modifications(self):
        order = create_order(
            customer=self.customer,
            status=self.status,
            items_data=[
                {
                    "menu_item": self.menu_item,
                    "name_ar": "برجر",
                    "base_price": 10,
                    "quantity": 2,
                    "modifications": []
                }
            ]
        )

        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.total_price, 20)
        item = order.items.first()
        assert item is not None
        self.assertEqual(item.modifications.count(), 0)


    def test_create_order_with_items_with_modifications(self):
        order = create_order(
            customer=self.customer,
            status=self.status,
            items_data=[
                {
                    "menu_item": self.menu_item,
                    "name_ar": "برجر",
                    "base_price": 10,
                    "quantity": 1,
                    "modifications": [
                        {
                            "ingredient": self.ingredient,
                            "name_ar": "جبنة",
                            "type": "added",
                            "quantity": 2
                        }
                    ]
                }
            ]
        )

        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.total_price, 14)  # 10 for the burger + 2*2 for the added cheese
        item = order.items.first()
        assert item is not None
        self.assertEqual(item.modifications.count(), 1)
