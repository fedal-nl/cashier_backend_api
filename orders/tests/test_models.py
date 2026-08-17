from datetime import timedelta

from django.db.models import ProtectedError
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone

from orders.models import (
    Campaign,
    Customer,
    DeliveryCompany,
    Order,
    OrderLog,
    OrderItem,
    OrderItemModification,
)

from menu.models import (
    Branch,
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
            address="Amsterdam",
        )

        self.assertEqual(customer.name, "Omar")
        self.assertEqual(str(customer), "Omar - omar@test.com")

    def test_email_and_phone_number_can_be_reused(self):
        Customer.objects.create(
            name="User1",
            email="test@test.com",
            phone_number="123456",
        )
        customer = Customer.objects.create(
            name="User2",
            email="test@test.com",
            phone_number="123456",
        )

        self.assertEqual(customer.email, "test@test.com")
        self.assertEqual(customer.phone_number, "123456")


class DeliveryCompanyModelTest(TestCase):
    def test_create_delivery_company(self):
        delivery_company = DeliveryCompany.objects.create(
            name="Fast Delivery",
            phone_number="0771234567",
            website="https://delivery.example.com",
            contact_person="Sara",
        )

        self.assertEqual(delivery_company.name, "Fast Delivery")

        self.assertEqual(str(delivery_company), "Fast Delivery")

    def test_delivery_company_name_is_optional(self):
        delivery_company = DeliveryCompany.objects.create()

        self.assertEqual(
            str(delivery_company), f"Delivery company #{delivery_company.id}"
        )


class OrderModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Omar", email="omar@test.com")

        self.status = Order.OrderStatus.CREATED
        self.branch = Branch.objects.create(name="Main Branch")

    def test_create_order(self):
        order = Order.objects.create(
            customer=self.customer,
            branch=self.branch,
            total_price=50,
            status=self.status,
        )

        self.assertIsNotNone(order.id)  # UUID generated
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.branch, self.branch)
        self.assertEqual(order.status, self.status)

    def test_order_str(self):
        order = Order.objects.create(
            customer=self.customer,
            branch=self.branch,
            total_price=20,
            status=self.status,
        )

        expected = f"Order #{order.id} - {self.customer.name} - {self.status}"
        self.assertEqual(str(order), expected)


class OrderLogModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Omar", email="omar-log@test.com")
        self.branch = Branch.objects.create(name="Main Branch")
        self.order = Order.objects.create(
            customer=self.customer,
            branch=self.branch,
            total_price=20,
            status=Order.OrderStatus.CREATED,
        )

    def test_create_order_log(self):
        log = OrderLog.objects.create(
            order=self.order,
            customer=self.customer,
            event_type=OrderLog.EventType.CREATED,
            new_status=Order.OrderStatus.CREATED,
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
            new_status=Order.OrderStatus.PREPARING,
        )

        expected = f"status_updated - Order #{self.order.id} - preparing"
        self.assertEqual(str(log), expected)


class OrderItemModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Omar", email="omar@test.com")

        self.status = Order.OrderStatus.CREATED
        self.branch = Branch.objects.create(name="Main Branch")

        self.order = Order.objects.create(
            customer=self.customer,
            branch=self.branch,
            total_price=0,
            status=self.status,
        )

        self.category = Category.objects.create(name_ar="طعام")

        self.unit = Unit.objects.create(name_ar="عادي")

        self.menu_item = MenuItem.objects.create(
            name_ar="برجر", price=10, category=self.category, quantity=1, unit=self.unit
        )

    def test_create_order_item(self):
        item = OrderItem.objects.create(
            order=self.order,
            menu_item=self.menu_item,
            menu_item_name_ar="برجر",
            menu_item_base_price=10,
            quantity=2,
            total_price=20,
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
            total_price=20,
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
            total_price=10,
        )

        self.order.delete()

        self.assertEqual(OrderItem.objects.count(), 0)

    def test_branch_delete_is_protected(self):
        with self.assertRaises(ProtectedError):
            self.branch.delete()


class CampaignModelTest(TestCase):
    def setUp(self):
        self.branch = Branch.objects.create(name="Main")
        self.category = Category.objects.create(name_ar="Food")
        self.menu_item = MenuItem.objects.create(
            name_ar="Burger", price=10, category=self.category
        )
        self.other_item = MenuItem.objects.create(
            name_ar="Drink", price=5, category=self.category
        )
        self.campaign = Campaign.objects.create(
            campaign_name="TikTok Burger",
            start_date=timezone.localdate(),
            end_date=timezone.localdate(),
            channel=Campaign.Channel.TIKTOK,
            amount_spent=12,
        )
        self.campaign.menu_items.add(self.menu_item)

    def test_metrics_only_include_promoted_items_from_non_cancelled_orders(self):
        order = Order.objects.create(
            branch=self.branch,
            status=Order.OrderStatus.COMPLETED,
            total_price=25,
        )
        OrderItem.objects.create(
            order=order,
            menu_item=self.menu_item,
            menu_item_name_ar="Burger",
            menu_item_base_price=10,
            quantity=2,
            total_price=20,
        )
        OrderItem.objects.create(
            order=order,
            menu_item=self.other_item,
            menu_item_name_ar="Drink",
            menu_item_base_price=5,
            quantity=1,
            total_price=5,
        )
        cancelled_order = Order.objects.create(
            branch=self.branch,
            status=Order.OrderStatus.CANCELLED,
            total_price=10,
        )
        OrderItem.objects.create(
            order=cancelled_order,
            menu_item=self.menu_item,
            menu_item_name_ar="Burger",
            menu_item_base_price=10,
            quantity=1,
            total_price=10,
        )

        self.assertEqual(self.campaign.current_revenue, 20)
        self.assertEqual(self.campaign.total_orders, 1)
        self.assertEqual(self.campaign.profit, 8)

    def test_end_date_cannot_precede_start_date(self):
        campaign = Campaign(
            campaign_name="Invalid",
            start_date=timezone.localdate(),
            end_date=timezone.localdate() - timedelta(days=1),
            channel=Campaign.Channel.ONLINE,
            amount_spent=10,
        )

        with self.assertRaises(ValidationError):
            campaign.full_clean()


class OrderItemModificationTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Omar", email="omar@test.com")

        self.status = Order.OrderStatus.CREATED
        self.branch = Branch.objects.create(name="Main Branch")

        self.order = Order.objects.create(
            customer=self.customer,
            branch=self.branch,
            total_price=0,
            status=self.status,
        )

        self.category = Category.objects.create(name_ar="طعام")

        self.unit = Unit.objects.create(name_ar="عادي")

        self.menu_item = MenuItem.objects.create(
            name_ar="برجر", price=10, category=self.category, quantity=1, unit=self.unit
        )

        self.order_item = OrderItem.objects.create(
            order=self.order,
            menu_item=self.menu_item,
            menu_item_name_ar="برجر",
            menu_item_base_price=10,
            quantity=1,
            total_price=10,
        )

        self.ingredient = Ingredient.objects.create(name_ar="جبنة", unit=self.unit)

    def test_create_modification(self):
        mod = OrderItemModification.objects.create(
            order_item=self.order_item,
            ingredient=self.ingredient,
            ingredient_name_ar="جبنة",
            modification_type="added",
        )

        self.assertEqual(mod.order_item, self.order_item)

    def test_modification_str(self):
        mod = OrderItemModification.objects.create(
            order_item=self.order_item,
            ingredient=self.ingredient,
            ingredient_name_ar="جبنة",
            modification_type="added",
        )

        expected = "Added جبنة"
        self.assertEqual(str(mod), expected)

    def test_cascade_delete_order_item(self):
        OrderItemModification.objects.create(
            order_item=self.order_item,
            ingredient=self.ingredient,
            ingredient_name_ar="جبنة",
            modification_type="added",
        )

        self.order_item.delete()

        self.assertEqual(OrderItemModification.objects.count(), 0)
