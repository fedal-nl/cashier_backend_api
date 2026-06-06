from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from orders.models import Customer, Order, OrderLog


class OrderManagementViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="cashier",
            password="test1234"
        )

        self.client.login(
            username="cashier",
            password="test1234"
        )

        self.customer = Customer.objects.create(
            name="Omar",
            email="omar@test.com"
        )

        self.order = Order.objects.create(
            customer=self.customer,
            total_price=10000,
            status=Order.OrderStatus.CREATED
        )

    def test_list_orders(self):
        response = self.client.get(
            "/api/orders/list/"
        )

        data = response.json()

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(data),
            1
        )


    def test_filter_orders_by_status(self):
        response = self.client.get(
            "/api/orders/list/?status=created"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(response.json()),
            1
        )

    def test_get_single_order(self):
        response = self.client.get(
            f"/api/orders/{self.order.id}/"
        )

        self.assertEqual(
            response.status_code,
            200
        )        


    def test_update_order_status(self):
        response = self.client.patch(
            f"/api/orders/{self.order.id}/status/",
            {
                "status":
                    Order.OrderStatus.PREPARING
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.order.refresh_from_db()

        self.assertEqual(
            self.order.status,
            Order.OrderStatus.PREPARING
        )

        log = self.order.logs.filter(
            event_type=OrderLog.EventType.STATUS_UPDATED
        ).get()

        self.assertEqual(
            log.previous_status,
            Order.OrderStatus.CREATED
        )

        self.assertEqual(
            log.new_status,
            Order.OrderStatus.PREPARING
        )

        self.assertEqual(
            log.created_by,
            self.user
        )

    def test_filter_orders_by_customer_name(self):
        Customer.objects.create(
            name="Ali",
            email="ali@test.com"
        )

        response = self.client.get(
            "/api/orders/list/?customer=Omar"
        )

        data = response.json()

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(data),
            1
        )

        self.assertEqual(
            data[0]["customer"]["name"],
            "Omar"
        )        
    def test_search_order_by_id(self):
        response = self.client.get(
            f"/api/orders/list/?search={self.order.id}"
        )

        data = response.json()

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(data),
            1
        )

        self.assertEqual(
            data[0]["id"],
            str(self.order.id)
        )

    def test_list_order_logs(self):
        OrderLog.objects.create(
            order=self.order,
            customer=self.customer,
            event_type=OrderLog.EventType.CREATED,
            new_status=Order.OrderStatus.CREATED,
            created_by=self.user
        )

        response = self.client.get(
            "/api/orders/logs/"
        )

        data = response.json()

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(data),
            1
        )

        self.assertEqual(
            data[0]["order_id"],
            str(self.order.id)
        )

        self.assertEqual(
            data[0]["customer"]["name"],
            "Omar"
        )

        self.assertEqual(
            data[0]["created_by_username"],
            "cashier"
        )

    def test_filter_order_logs_by_date_customer_and_status(self):
        matching_log = OrderLog.objects.create(
            order=self.order,
            customer=self.customer,
            event_type=OrderLog.EventType.CREATED,
            new_status=Order.OrderStatus.CREATED,
            created_by=self.user
        )

        other_customer = Customer.objects.create(
            name="Ali",
            email="ali-logs@test.com"
        )
        other_order = Order.objects.create(
            customer=other_customer,
            total_price=50,
            status=Order.OrderStatus.PREPARING
        )
        other_log = OrderLog.objects.create(
            order=other_order,
            customer=other_customer,
            event_type=OrderLog.EventType.STATUS_UPDATED,
            previous_status=Order.OrderStatus.CREATED,
            new_status=Order.OrderStatus.PREPARING,
            created_by=self.user
        )

        yesterday = timezone.now() - timedelta(days=1)
        OrderLog.objects.filter(
            id=other_log.id
        ).update(
            created_at=yesterday
        )

        today = timezone.localdate()

        response = self.client.get(
            f"/api/orders/logs/?date={today}&customer=Omar&status=created"
        )

        data = response.json()

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(data),
            1
        )

        self.assertEqual(
            data[0]["id"],
            matching_log.id
        )

    def test_filter_order_logs_rejects_invalid_date(self):
        response = self.client.get(
            "/api/orders/logs/?date=not-a-date"
        )

        self.assertEqual(
            response.status_code,
            400
        )
