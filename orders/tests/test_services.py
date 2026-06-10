from django.contrib.auth.models import User
from django.test import TestCase

from orders.services import create_order, update_order_status
from orders.models import Customer, DeliveryCompany, Order, OrderLog
from menu.models import Category, Unit, MenuItem, Ingredient


class OrderServiceTest(TestCase):

    def setUp(self):
        self.customer = Customer.objects.create(
            name="Omar",
            email="omar@test.com"
        )
        self.user = User.objects.create_user(
            username="cashier",
            password="test1234"
        )

        self.status = Order.OrderStatus.CREATED

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

        self.delivery_company = DeliveryCompany.objects.create(
            name="Fast Delivery"
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

    def test_create_order_writes_created_log(self):
        order = create_order(
            customer=self.customer,
            status=self.status,
            user=self.user,
            items_data=[
                {
                    "menu_item": self.menu_item,
                    "name_ar": "برجر",
                    "base_price": 10,
                    "quantity": 1,
                    "modifications": []
                }
            ]
        )

        log = order.logs.get()
        self.assertEqual(log.event_type, OrderLog.EventType.CREATED)
        self.assertIsNone(log.previous_status)
        self.assertEqual(log.new_status, Order.OrderStatus.CREATED)
        self.assertEqual(log.created_by, self.user)

    def test_create_order_sets_delivery_company(self):
        order = create_order(
            customer=self.customer,
            status=self.status,
            delivery_company=self.delivery_company,
            items_data=[
                {
                    "menu_item": self.menu_item,
                    "name_ar": "برجر",
                    "base_price": 10,
                    "quantity": 1,
                    "modifications": []
                }
            ]
        )

        self.assertEqual(
            order.delivery_company,
            self.delivery_company
        )

    def test_update_order_status_writes_status_log(self):
        order = create_order(
            customer=self.customer,
            status=self.status,
            items_data=[
                {
                    "menu_item": self.menu_item,
                    "name_ar": "برجر",
                    "base_price": 10,
                    "quantity": 1,
                    "modifications": []
                }
            ]
        )

        update_order_status(
            order=order,
            status=Order.OrderStatus.PREPARING,
            user=self.user
        )

        order.refresh_from_db()
        log = order.logs.filter(
            event_type=OrderLog.EventType.STATUS_UPDATED
        ).get()

        self.assertEqual(order.status, Order.OrderStatus.PREPARING)
        self.assertEqual(log.previous_status, Order.OrderStatus.CREATED)
        self.assertEqual(log.new_status, Order.OrderStatus.PREPARING)
        self.assertEqual(log.created_by, self.user)

    def test_update_order_status_sets_delivery_company(self):
        delivery_company = DeliveryCompany.objects.create(
            name="Fast Delivery"
        )

        order = create_order(
            customer=self.customer,
            status=self.status,
            items_data=[
                {
                    "menu_item": self.menu_item,
                    "name_ar": "برجر",
                    "base_price": 10,
                    "quantity": 1,
                    "modifications": []
                }
            ]
        )

        update_order_status(
            order=order,
            status=Order.OrderStatus.PICKED_UP,
            delivery_company=delivery_company,
            user=self.user
        )

        order.refresh_from_db()

        self.assertEqual(
            order.delivery_company,
            delivery_company
        )

        self.assertEqual(
            order.status,
            Order.OrderStatus.PICKED_UP
        )


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
                            "quantity": 2,
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

    def test_create_order_with_no_ingredient_modifications(self):
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
                            "quantity": 1,
                        }
                    ]
                }
            ]
        )

        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.total_price, 12)
        item = order.items.first()
        assert item is not None
        self.assertEqual(item.modifications.count(), 1)

    def test_create_order_with_multiple_items_and_modifications(self):
        another_menu_item = MenuItem.objects.create(
            name_ar="بطاطس",
            price=5,
            category=self.category,
            quantity=1,
            unit=self.unit
        )

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
                            "quantity": 1,
                        }
                    ]
                },
                {
                    "menu_item": another_menu_item,
                    "name_ar": "بطاطس",
                    "base_price": 5,
                    "quantity": 2,
                    "modifications": []
                }
            ]
        )

        self.assertEqual(order.items.count(), 2)
        self.assertEqual(order.total_price, 22)  # (10 + 2) for the burger with cheese + (5*2) for the fries

    def test_create_order_with_removed_ingredient_modification(self):
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
                            "type": "removed",
                            "quantity": 1,
                        }
                    ]
                }
            ]
        )

        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.total_price, 8)  # 10 for the burger - 2 for the removed cheese
        item = order.items.first()
        assert item is not None
        self.assertEqual(item.modifications.count(), 1)

    def test_create_order_without_ingredient_in_modification(self):
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
                            "name_ar": "جبنة",
                            "type": "added",
                            "quantity": 1,
                        }
                    ]
                }
            ]
        )

        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.total_price, 10)  # the modification should be ignored since it doesn't have an ingredient
        item = order.items.first()
        assert item is not None
        self.assertEqual(item.modifications.count(), 0)
