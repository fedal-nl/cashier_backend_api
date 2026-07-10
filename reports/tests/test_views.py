from datetime import datetime, timezone as datetime_timezone

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from menu.models import Branch
from orders.models import Customer, Order


class DailyReportViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(username="cashier", password="test1234")

        self.client.login(username="cashier", password="test1234")

        self.main_branch = Branch.objects.create(name="Main Branch")
        self.second_branch = Branch.objects.create(name="Second Branch")
        self.default_branch = Branch.objects.create(name="Default Branch")

        self.new_customer = Customer.objects.create(
            name="New Customer", email="new@test.com"
        )
        self.existing_customer = Customer.objects.create(
            name="Existing Customer", email="existing@test.com"
        )
        self.second_new_customer = Customer.objects.create(
            name="Second New Customer", email="second-new@test.com"
        )

        previous_order = self._create_order(
            customer=self.existing_customer,
            status=Order.OrderStatus.CREATED,
            total_price=7,
            created_at=datetime(2026, 5, 31, 12, tzinfo=datetime_timezone.utc),
        )

        self._create_order(
            customer=self.new_customer,
            status=Order.OrderStatus.CREATED,
            total_price=10,
            created_at=datetime(2026, 6, 1, 10, tzinfo=datetime_timezone.utc),
        )
        self._create_order(
            customer=self.new_customer,
            status=Order.OrderStatus.COMPLETED,
            total_price=20,
            created_at=datetime(2026, 6, 1, 11, tzinfo=datetime_timezone.utc),
        )
        self._create_order(
            customer=self.existing_customer,
            status=Order.OrderStatus.CREATED,
            total_price=5,
            created_at=datetime(2026, 6, 1, 12, tzinfo=datetime_timezone.utc),
        )
        self._create_order(
            customer=self.new_customer,
            status=Order.OrderStatus.PICKED_UP,
            total_price=12,
            created_at=datetime(2026, 6, 2, 10, tzinfo=datetime_timezone.utc),
        )
        self._create_order(
            customer=self.second_new_customer,
            status=Order.OrderStatus.DELIVERED,
            total_price=10,
            created_at=datetime(2026, 6, 2, 11, tzinfo=datetime_timezone.utc),
        )

        self.assertEqual(previous_order.created_at.date().isoformat(), "2026-05-31")

    def test_daily_report_returns_rows_for_date_range(self):
        response = self.client.get(
            "/api/reports/daily/?date_from=2026-06-01&date_to=2026-06-03"
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(len(data), 9)

        first_day = self._find_report_row(
            data, date="2026-06-01", branch=self.default_branch
        )

        self.assertEqual(first_day["date"], "2026-06-01")
        self.assertEqual(first_day["branch_id"], self.default_branch.id)
        self.assertEqual(first_day["branch_name"], "Default Branch")
        self.assertEqual(first_day["total_orders"], 3)
        self.assertEqual(first_day["orders_by_status"]["created"], 2)
        self.assertEqual(first_day["orders_by_status"]["completed"], 1)
        self.assertEqual(first_day["orders_by_status"]["picked_up"], 0)
        self.assertEqual(first_day["total_new_customers_ordered"], 1)
        self.assertEqual(first_day["total_existing_customers_ordered"], 1)
        self.assertEqual(first_day["total_revenue"], "35.00")

        second_day = self._find_report_row(
            data, date="2026-06-02", branch=self.default_branch
        )

        self.assertEqual(second_day["date"], "2026-06-02")
        self.assertEqual(second_day["total_orders"], 2)
        self.assertEqual(second_day["orders_by_status"]["picked_up"], 1)
        self.assertEqual(second_day["orders_by_status"]["delivered"], 1)
        self.assertEqual(second_day["total_new_customers_ordered"], 1)
        self.assertEqual(second_day["total_existing_customers_ordered"], 1)
        self.assertEqual(second_day["total_revenue"], "22.00")

        empty_day = self._find_report_row(
            data, date="2026-06-03", branch=self.default_branch
        )

        self.assertEqual(
            empty_day,
            {
                "date": "2026-06-03",
                "branch_id": self.default_branch.id,
                "branch_name": "Default Branch",
                "total_orders": 0,
                "orders_by_status": {
                    "created": 0,
                    "preparing": 0,
                    "ready": 0,
                    "completed": 0,
                    "cancelled": 0,
                    "paid": 0,
                    "picked_up": 0,
                    "delivered": 0,
                },
                "total_existing_customers_ordered": 0,
                "total_new_customers_ordered": 0,
                "total_revenue": "0.00",
            },
        )

    def test_daily_report_requires_authentication(self):
        client = APIClient()

        response = client.get(
            "/api/reports/daily/?date_from=2026-06-01&date_to=2026-06-03"
        )

        self.assertEqual(response.status_code, 403)

    def test_daily_report_requires_valid_dates(self):
        response = self.client.get(
            "/api/reports/daily/?date_from=bad&date_to=2026-06-03"
        )

        self.assertEqual(response.status_code, 400)

        self.assertIn("date_from", response.json())

    def test_daily_report_rejects_date_to_before_date_from(self):
        response = self.client.get(
            "/api/reports/daily/?date_from=2026-06-03&date_to=2026-06-01"
        )

        self.assertEqual(response.status_code, 400)

        self.assertIn("date_to", response.json())

    def test_daily_report_can_be_filtered_by_branch(self):
        branch_customer = Customer.objects.create(
            name="Branch Customer", email="branch@test.com"
        )
        self._create_order(
            customer=branch_customer,
            branch=self.main_branch,
            status=Order.OrderStatus.CREATED,
            total_price=15,
            created_at=datetime(2026, 6, 1, 13, tzinfo=datetime_timezone.utc),
        )
        self._create_order(
            customer=branch_customer,
            branch=self.second_branch,
            status=Order.OrderStatus.CREATED,
            total_price=50,
            created_at=datetime(2026, 6, 1, 14, tzinfo=datetime_timezone.utc),
        )

        response = self.client.get(
            f"/api/reports/daily/?date_from=2026-06-01&date_to=2026-06-01&branch_id={self.main_branch.id}"
        )

        data = response.json()

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["branch_id"], self.main_branch.id)
        self.assertEqual(data[0]["branch_name"], "Main Branch")
        self.assertEqual(data[0]["total_orders"], 1)

        self.assertEqual(data[0]["total_revenue"], "15.00")

    def test_daily_report_can_be_filtered_by_status(self):
        response = self.client.get(
            "/api/reports/daily/?date_from=2026-06-01&date_to=2026-06-01&status=completed"
        )

        data = response.json()

        self.assertEqual(response.status_code, 200)

        default_branch_report = self._find_report_row(
            data, date="2026-06-01", branch=self.default_branch
        )

        self.assertEqual(default_branch_report["total_orders"], 1)

        self.assertEqual(default_branch_report["orders_by_status"]["completed"], 1)

        self.assertEqual(default_branch_report["orders_by_status"]["created"], 0)

    def test_daily_report_rejects_invalid_branch(self):
        response = self.client.get(
            "/api/reports/daily/?date_from=2026-06-01&date_to=2026-06-01&branch_id=999"
        )

        self.assertEqual(response.status_code, 400)

        self.assertIn("branch_id", response.json())

    def _create_order(self, *, customer, status, total_price, created_at, branch=None):
        branch = branch or self.default_branch
        order = Order.objects.create(
            customer=customer, branch=branch, total_price=total_price, status=status
        )
        Order.objects.filter(id=order.id).update(
            created_at=created_at, updated_at=created_at
        )
        order.refresh_from_db()

        return order

    def _find_report_row(self, rows, *, date, branch):
        return next(
            row
            for row in rows
            if row["date"] == date and row["branch_id"] == branch.id
        )
