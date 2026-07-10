from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from menu.models import Branch, Category, Ingredient, MenuItem, Unit
from orders.models import Customer, DeliveryCompany, Order, OrderLog


class OrderManagementViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(username="cashier", password="test1234")

        self.client.login(username="cashier", password="test1234")

        self.customer = Customer.objects.create(name="Omar", email="omar@test.com")
        self.branch = Branch.objects.create(name="Main Branch")

        self.order = Order.objects.create(
            customer=self.customer,
            branch=self.branch,
            total_price=10000,
            status=Order.OrderStatus.CREATED,
        )

    def test_list_customers_search_filters_before_pagination(self):
        for index in range(12):
            Customer.objects.create(
                name=f"Customer {index}",
                email=f"customer-{index}@test.com",
                phone_number=f"07700000{index:02d}",
            )

        target = Customer.objects.create(
            name="Zainab Search",
            email="zainab-search@test.com",
            phone_number="07999999123",
        )

        response = self.client.get(
            "/api/orders/customers/list/?page_size=5&search=07999999123"
        )

        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["id"], target.id)

    def test_list_customers_search_ignores_email_and_address(self):
        Customer.objects.create(
            name="Email Only",
            email="email-only@test.com",
            phone_number="07711111111",
            address="Hidden Street",
        )

        email_response = self.client.get(
            "/api/orders/customers/list/?search=email-only"
        )
        address_response = self.client.get("/api/orders/customers/list/?search=Hidden")

        self.assertEqual(email_response.status_code, 200)
        self.assertEqual(address_response.status_code, 200)
        self.assertEqual(email_response.json()["count"], 0)
        self.assertEqual(address_response.json()["count"], 0)

    def test_list_orders(self):
        response = self.client.get("/api/orders/list/")

        data = response.json()

        self.assertEqual(response.status_code, 200)

        self.assertEqual(data["count"], 1)

        self.assertEqual(len(data["results"]), 1)

    def test_filter_orders_by_status(self):
        response = self.client.get("/api/orders/list/?status=created")

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json()["count"], 1)

    def test_list_orders_can_be_paginated(self):
        for index in range(3):
            customer = Customer.objects.create(
                name=f"Customer {index}", email=f"customer-{index}@test.com"
            )
            Order.objects.create(
                customer=customer,
                branch=self.branch,
                total_price=100,
                status=Order.OrderStatus.CREATED,
            )

        response = self.client.get("/api/orders/list/?page_size=2")

        data = response.json()

        self.assertEqual(response.status_code, 200)

        self.assertEqual(data["count"], 4)

        self.assertIsNotNone(data["next"])

        self.assertIsNone(data["previous"])

        self.assertEqual(len(data["results"]), 2)

    def test_today_order_summary_returns_count_revenue_and_status_totals(self):
        second_branch = Branch.objects.create(name="Second Branch")

        Order.objects.create(
            customer=self.customer,
            branch=self.branch,
            total_price=25.50,
            status=Order.OrderStatus.COMPLETED,
        )

        new_customer = Customer.objects.create(
            name="Sara", email="sara-summary@test.com"
        )
        Order.objects.create(
            customer=new_customer,
            branch=self.branch,
            total_price=10,
            status=Order.OrderStatus.PAID,
        )

        Order.objects.create(
            customer=new_customer,
            branch=self.branch,
            total_price=900,
            status=Order.OrderStatus.CANCELLED,
        )

        Order.objects.create(
            customer=new_customer,
            branch=second_branch,
            total_price=35,
            status=Order.OrderStatus.DELIVERED,
        )

        old_order = Order.objects.create(
            customer=self.customer,
            branch=self.branch,
            total_price=500,
            status=Order.OrderStatus.DELIVERED,
        )
        Order.objects.filter(id=old_order.id).update(
            created_at=timezone.now() - timedelta(days=1)
        )

        response = self.client.get("/api/orders/summary/today/")

        data = response.json()

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(data), 2)

        main_branch_summary = data[0]
        second_branch_summary = data[1]

        self.assertEqual(main_branch_summary["branch_id"], self.branch.id)

        self.assertEqual(main_branch_summary["branch_name"], "Main Branch")

        self.assertEqual(main_branch_summary["total_orders"], 4)

        self.assertEqual(main_branch_summary["total_revenue"], "10035.50")

        self.assertEqual(main_branch_summary["total_existing_customers_ordered"], 1)

        self.assertEqual(main_branch_summary["total_new_customers_ordered"], 1)

        self.assertEqual(main_branch_summary["orders_by_status"]["created"], 1)

        self.assertEqual(main_branch_summary["orders_by_status"]["completed"], 1)

        self.assertEqual(main_branch_summary["orders_by_status"]["cancelled"], 1)

        self.assertEqual(main_branch_summary["orders_by_status"]["delivered"], 0)

        self.assertEqual(second_branch_summary["branch_id"], second_branch.id)

        self.assertEqual(second_branch_summary["branch_name"], "Second Branch")

        self.assertEqual(second_branch_summary["total_orders"], 1)

        self.assertEqual(second_branch_summary["total_revenue"], "35.00")

        self.assertEqual(second_branch_summary["orders_by_status"]["delivered"], 1)

    def test_get_single_order(self):
        response = self.client.get(f"/api/orders/{self.order.id}/")

        self.assertEqual(response.status_code, 200)

    def test_put_order_updates_order_details(self):
        new_customer = Customer.objects.create(
            name="Sara",
            email="sara-update@test.com",
        )
        new_branch = Branch.objects.create(
            name="Second Branch",
        )
        delivery_company = DeliveryCompany.objects.create(
            name="Fast Delivery",
        )

        response = self.client.put(
            f"/api/orders/{self.order.id}/",
            {
                "customer_id": new_customer.id,
                "branch_id": new_branch.id,
                "delivery_company_id": delivery_company.id,
                "order_type": Order.OrderType.DELIVERY,
                "note": "Updated by frontend",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.order.refresh_from_db()

        self.assertEqual(self.order.customer, new_customer)
        self.assertEqual(self.order.branch, new_branch)
        self.assertEqual(self.order.delivery_company, delivery_company)
        self.assertEqual(self.order.order_type, Order.OrderType.DELIVERY)
        self.assertEqual(self.order.note, "Updated by frontend")
        self.assertEqual(response.json()["branch"]["id"], new_branch.id)

    def test_put_order_rejects_missing_required_branch(self):
        response = self.client.put(
            f"/api/orders/{self.order.id}/",
            {
                "order_type": Order.OrderType.TAKEAWAY,
                "note": "Missing branch",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("branch_id", response.json())

    def test_patch_order_updates_order_details(self):
        response = self.client.patch(
            f"/api/orders/{self.order.id}/",
            {
                "order_type": Order.OrderType.DINE_IN,
                "customer_id": None,
                "delivery_company_id": None,
                "note": "Moved to dine in",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.order.refresh_from_db()

        self.assertEqual(self.order.order_type, Order.OrderType.DINE_IN)
        self.assertIsNone(self.order.customer)
        self.assertIsNone(self.order.delivery_company)
        self.assertEqual(self.order.note, "Moved to dine in")
        self.assertEqual(response.json()["order_type"], Order.OrderType.DINE_IN)

    def test_put_order_accepts_frontend_edit_payload_and_replaces_items(self):
        category = Category.objects.create(name_ar="Food")
        unit = Unit.objects.create(name_ar="Piece")
        menu_item = MenuItem.objects.create(
            name_ar="Burger",
            price=10,
            category=category,
            unit=unit,
        )
        menu_item.branches.add(self.branch)
        ingredient = Ingredient.objects.create(
            name_ar="Cheese",
            price=2,
            unit=unit,
        )

        response = self.client.put(
            f"/api/orders/{self.order.id}/",
            {
                "customer_id": None,
                "branch_id": self.branch.id,
                "delivery_company_id": None,
                "order_type": Order.OrderType.DINE_IN,
                "status": Order.OrderStatus.PREPARING,
                "note": "Updated items",
                "items": [
                    {
                        "menu_item_id": menu_item.id,
                        "quantity": 2,
                        "note": "No onion",
                        "modifications": [
                            {
                                "ingredient_id": ingredient.id,
                                "type": "added",
                                "quantity": 1,
                                "name_ar": ingredient.name_ar,
                            }
                        ],
                    }
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.order.refresh_from_db()

        self.assertEqual(self.order.order_type, Order.OrderType.DINE_IN)
        self.assertEqual(self.order.status, Order.OrderStatus.PREPARING)
        self.assertEqual(self.order.note, "Updated items")
        self.assertEqual(self.order.total_price, 22)
        self.assertEqual(self.order.items.count(), 1)

        order_item = self.order.items.get()
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.total_price, 22)
        self.assertEqual(order_item.modifications.count(), 1)

    def test_patch_order_rejects_invalid_branch(self):
        response = self.client.patch(
            f"/api/orders/{self.order.id}/",
            {
                "order_type": Order.OrderType.DINE_IN,
                "branch_id": 999,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid branch_id", str(response.content))

    def test_update_order_status(self):
        response = self.client.patch(
            f"/api/orders/{self.order.id}/status/",
            {"status": Order.OrderStatus.PREPARING},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.order.refresh_from_db()

        self.assertEqual(self.order.status, Order.OrderStatus.PREPARING)

        log = self.order.logs.filter(event_type=OrderLog.EventType.STATUS_UPDATED).get()

        self.assertEqual(log.previous_status, Order.OrderStatus.CREATED)

        self.assertEqual(log.new_status, Order.OrderStatus.PREPARING)

        self.assertEqual(log.created_by, self.user)

    def test_update_order_status_to_picked_up_sets_delivery_company(self):
        delivery_company = DeliveryCompany.objects.create(
            name="Fast Delivery",
            phone_number="0771234567",
            website="https://delivery.example.com",
            contact_person="Sara",
        )

        response = self.client.patch(
            f"/api/orders/{self.order.id}/status/",
            {
                "status": Order.OrderStatus.PICKED_UP,
                "delivery_company_id": delivery_company.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.order.refresh_from_db()

        self.assertEqual(self.order.status, Order.OrderStatus.PICKED_UP)

        self.assertEqual(self.order.delivery_company, delivery_company)

        self.assertEqual(response.json()["delivery_company"]["id"], delivery_company.id)

    def test_update_order_status_to_preparing_sets_delivery_company(self):
        delivery_company = DeliveryCompany.objects.create(name="Fast Delivery")

        response = self.client.patch(
            f"/api/orders/{self.order.id}/status/",
            {
                "status": Order.OrderStatus.PREPARING,
                "delivery_company_id": delivery_company.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.order.refresh_from_db()

        self.assertEqual(self.order.status, Order.OrderStatus.PREPARING)

        self.assertEqual(self.order.delivery_company, delivery_company)

    def test_update_order_status_to_picked_up_without_delivery_company(self):
        response = self.client.patch(
            f"/api/orders/{self.order.id}/status/",
            {"status": Order.OrderStatus.PICKED_UP},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.order.refresh_from_db()

        self.assertEqual(self.order.status, Order.OrderStatus.PICKED_UP)

        self.assertIsNone(self.order.delivery_company)

    def test_update_order_status_rejects_invalid_delivery_company(self):
        response = self.client.patch(
            f"/api/orders/{self.order.id}/status/",
            {"status": Order.OrderStatus.PICKED_UP, "delivery_company_id": 999},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.assertIn("delivery_company_id", response.json())

    def test_list_delivery_companies(self):
        delivery_company = DeliveryCompany.objects.create(
            name="Fast Delivery",
            phone_number="0771234567",
            website="https://delivery.example.com",
            contact_person="Sara",
        )

        response = self.client.get("/api/orders/delivery-companies/")

        data = response.json()

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(data), 1)

        self.assertEqual(data[0]["id"], delivery_company.id)

        self.assertEqual(data[0]["name"], "Fast Delivery")

    def test_filter_orders_by_customer_name(self):
        Customer.objects.create(name="Ali", email="ali@test.com")

        response = self.client.get("/api/orders/list/?customer=Omar")

        data = response.json()

        self.assertEqual(response.status_code, 200)

        self.assertEqual(data["count"], 1)

        self.assertEqual(data["results"][0]["customer"]["name"], "Omar")

    def test_search_order_by_id(self):
        response = self.client.get(f"/api/orders/list/?search={self.order.id}")

        data = response.json()

        self.assertEqual(response.status_code, 200)

        self.assertEqual(data["count"], 1)

        self.assertEqual(data["results"][0]["id"], str(self.order.id))

    def test_search_order_by_customer_name(self):
        other_customer = Customer.objects.create(
            name="Ali", email="ali-search@test.com"
        )
        Order.objects.create(
            customer=other_customer,
            branch=self.branch,
            total_price=50,
            status=Order.OrderStatus.CREATED,
        )

        response = self.client.get("/api/orders/list/?search=Omar")

        data = response.json()

        self.assertEqual(response.status_code, 200)

        self.assertEqual(data["count"], 1)

        self.assertEqual(data["results"][0]["customer"]["name"], "Omar")

    def test_list_order_logs(self):
        OrderLog.objects.create(
            order=self.order,
            customer=self.customer,
            event_type=OrderLog.EventType.CREATED,
            new_status=Order.OrderStatus.CREATED,
            created_by=self.user,
        )

        response = self.client.get("/api/orders/logs/")

        data = response.json()

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(data), 1)

        self.assertEqual(data[0]["order_id"], str(self.order.id))

        self.assertEqual(data[0]["customer"]["name"], "Omar")

        self.assertEqual(data[0]["created_by_username"], "cashier")

    def test_filter_order_logs_by_date_customer_and_status(self):
        matching_log = OrderLog.objects.create(
            order=self.order,
            customer=self.customer,
            event_type=OrderLog.EventType.CREATED,
            new_status=Order.OrderStatus.CREATED,
            created_by=self.user,
        )

        other_customer = Customer.objects.create(name="Ali", email="ali-logs@test.com")
        other_order = Order.objects.create(
            customer=other_customer,
            branch=self.branch,
            total_price=50,
            status=Order.OrderStatus.PREPARING,
        )
        other_log = OrderLog.objects.create(
            order=other_order,
            customer=other_customer,
            event_type=OrderLog.EventType.STATUS_UPDATED,
            previous_status=Order.OrderStatus.CREATED,
            new_status=Order.OrderStatus.PREPARING,
            created_by=self.user,
        )

        yesterday = timezone.now() - timedelta(days=1)
        OrderLog.objects.filter(id=other_log.id).update(created_at=yesterday)

        today = timezone.localdate()

        response = self.client.get(
            f"/api/orders/logs/?date={today}&customer=Omar&status=created"
        )

        data = response.json()

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(data), 1)

        self.assertEqual(data[0]["id"], matching_log.id)

    def test_filter_order_logs_rejects_invalid_date(self):
        response = self.client.get("/api/orders/logs/?date=not-a-date")

        self.assertEqual(response.status_code, 400)
