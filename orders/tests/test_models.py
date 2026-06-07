from django.test import TestCase
from django.utils import timezone

from orders.models import (
    Customer,
    DeliveryCompany,
    Order,
    OrderLog,
    OrderItem,
    OrderItemModification,
)

from menu.models import (
    Category,
    Unit,
    MenuItem,
    Ingredient,
)


class CustomerModelTest(TestCase):

    def test_create_customer(self):
        customer = Customer.objects.create(
            name="Omar",
            email="omar@test.com",
            phone_number="123456",
            address="Amsterdam"
        )

        self.assertEqual(customer.name, "Omar")
        self.assertEqual(str(customer), "Omar - omar@test.com")

    def test_unique_email(self):
        Customer.objects.create(
            name="User1",
            email="test@test.com"
        )

        with self.assertRaises(Exception):
            Customer.objects.create(
                name="User2",
                email="test@test.com"
            )


class DeliveryCompanyModelTest(TestCase):

    def test_create_delivery_company(self):
        delivery_company = DeliveryCompany.objects.create(
            name="Fast Delivery",
            phone_number="0771234567",
            website="https://delivery.example.com",
            contact_person="Sara"
        )

        self.assertEqual(
            delivery_company.name,
            "Fast Delivery"
        )

        self.assertEqual(
            str(delivery_company),
            "Fast Delivery"
        )

    def test_delivery_company_name_is_optional(self):
        delivery_company = DeliveryCompany.objects.create()

        self.assertEqual(
            str(delivery_company),
            f"Delivery company #{delivery_company.id}"
        )


class OrderModelTest(TestCase):

    def setUp(self):
        self.customer = Customer.objects.create(
            name="Omar",
            email="omar@test.com"
        )

        self.status = Order.OrderStatus.CREATED

    def test_create_order(self):
        order = Order.objects.create(
            customer=self.customer,
            total_price=50,
            status=self.status
        )

        self.assertIsNotNone(order.id)  # UUID generated
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.status, self.status)

    def test_order_str(self):
        order = Order.objects.create(
            customer=self.customer,
            total_price=20,
            status=self.status
        )

        expected = f"Order #{order.id} - {self.customer.name} - {self.status}"
        self.assertEqual(str(order), expected)


class OrderLogModelTest(TestCase):

    def setUp(self):
        self.customer = Customer.objects.create(
            name="Omar",
            email="omar-log@test.com"
        )
        self.order = Order.objects.create(
            customer=self.customer,
            total_price=20,
            status=Order.OrderStatus.CREATED
        )

    def test_create_order_log(self):
        log = OrderLog.objects.create(
            order=self.order,
            customer=self.customer,
            event_type=OrderLog.EventType.CREATED,
            new_status=Order.OrderStatus.CREATED
        )

        self.assertEqual(log.order, self.order)
        self.assertEqual(log.customer, self.customer)
        self.assertEqual(log.event_type, OrderLog.EventType.CREATED)
        self.assertEqual(log.new_status, Order.OrderStatus.CREATED)

    def test_order_log_str(self):
        log = OrderLog.objects.create(
            order=self.order,
            customer=self.customer,
            event_type=OrderLog.EventType.STATUS_UPDATED,
            previous_status=Order.OrderStatus.CREATED,
            new_status=Order.OrderStatus.PREPARING
        )

        expected = f"status_updated - Order #{self.order.id} - preparing"
        self.assertEqual(str(log), expected)


class OrderItemModelTest(TestCase):

    def setUp(self):
        self.customer = Customer.objects.create(
            name="Omar",
            email="omar@test.com"
        )

        self.status = Order.OrderStatus.CREATED

        self.order = Order.objects.create(
            customer=self.customer,
            total_price=0,
            status=self.status
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

    def test_create_order_item(self):
        item = OrderItem.objects.create(
            order=self.order,
            menu_item=self.menu_item,
            menu_item_name_ar="برجر",
            menu_item_base_price=10,
            quantity=2,
            total_price=20
        )

        self.assertEqual(item.order, self.order)
        self.assertEqual(item.quantity, 2)

    def test_order_item_str(self):
        item = OrderItem.objects.create(
            order=self.order,
            menu_item=self.menu_item,
            menu_item_name_ar="برجر",
            menu_item_base_price=10,
            quantity=2,
            total_price=20
        )

        expected = "2 x برجر - $20"
        self.assertEqual(str(item), expected)

    def test_cascade_delete_order(self):
        item = OrderItem.objects.create(
            order=self.order,
            menu_item=self.menu_item,
            menu_item_name_ar="برجر",
            menu_item_base_price=10,
            quantity=1,
            total_price=10
        )

        self.order.delete()

        self.assertEqual(OrderItem.objects.count(), 0)


class OrderItemModificationTest(TestCase):

    def setUp(self):
        self.customer = Customer.objects.create(
            name="Omar",
            email="omar@test.com"
        )

        self.status = Order.OrderStatus.CREATED

        self.order = Order.objects.create(
            customer=self.customer,
            total_price=0,
            status=self.status
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

        self.order_item = OrderItem.objects.create(
            order=self.order,
            menu_item=self.menu_item,
            menu_item_name_ar="برجر",
            menu_item_base_price=10,
            quantity=1,
            total_price=10
        )

        self.ingredient = Ingredient.objects.create(
            name_ar="جبنة",
            unit=self.unit
        )

    def test_create_modification(self):
        mod = OrderItemModification.objects.create(
            order_item=self.order_item,
            ingredient=self.ingredient,
            ingredient_name_ar="جبنة",
            modification_type="added"
        )

        self.assertEqual(mod.order_item, self.order_item)

    def test_modification_str(self):
        mod = OrderItemModification.objects.create(
            order_item=self.order_item,
            ingredient=self.ingredient,
            ingredient_name_ar="جبنة",
            modification_type="added"
        )

        expected = "Added جبنة"
        self.assertEqual(str(mod), expected)

    def test_cascade_delete_order_item(self):
        OrderItemModification.objects.create(
            order_item=self.order_item,
            ingredient=self.ingredient,
            ingredient_name_ar="جبنة",
            modification_type="added"
        )

        self.order_item.delete()

        self.assertEqual(OrderItemModification.objects.count(), 0)
