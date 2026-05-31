from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from orders.models import Customer, Order


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