from django.test import TestCase
from rest_framework.test import APIClient


from orders.models import Customer, DeliveryCompany, Order
from menu.models import Branch, Category, Unit, MenuItem, Ingredient


class OrderAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.customer = Customer.objects.create(
            id=1, name="Omar", email="omar@test.com"
        )

        self.status = Order.OrderStatus.CREATED

        self.category = Category.objects.create(id=1, name_ar="طعام")

        self.unit = Unit.objects.create(id=1, name_ar="عادي")

        self.menu_item = MenuItem.objects.create(
            id=1, name_ar="برجر", price=10, category=self.category, unit=self.unit
        )

        self.ingredient = Ingredient.objects.create(
            id=1, name_ar="جبنة", price=2, unit=self.unit
        )

        self.branch = Branch.objects.create(name="Main Branch")
        self.menu_item.branches.add(self.branch)

        self.delivery_company = DeliveryCompany.objects.create(name="Fast Delivery")

    def test_create_order_success(self):
        payload = {
            "customer_id": self.customer.pk,
            "branch_id": self.branch.id,
            "delivery_company_id": self.delivery_company.pk,
            "order_type": Order.OrderType.DELIVERY,
            "status": self.status,
            "items": [
                {
                    "menu_item_id": self.menu_item.pk,
                    "quantity": 2,
                    "modifications": [
                        {
                            "ingredient_id": self.ingredient.pk,
                            "type": "added",
                            "quantity": 1,
                            "name_ar": "جبنة",
                        }
                    ],
                }
            ],
        }

        response = self.client.post("/api/orders/", payload, format="json")

        self.assertEqual(response.status_code, 201)

    def test_create_order_requires_branch(self):
        payload = {
            "customer_id": self.customer.pk,
            "delivery_company_id": self.delivery_company.pk,
            "order_type": Order.OrderType.DELIVERY,
            "items": [
                {"menu_item_id": self.menu_item.pk, "quantity": 1, "modifications": []}
            ],
        }

        response = self.client.post("/api/orders/", payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("branch_id", response.json())

    def test_create_delivery_order_requires_customer_and_delivery_company(self):
        payload = {
            "order_type": Order.OrderType.DELIVERY,
            "branch_id": self.branch.id,
            "items": [
                {"menu_item_id": self.menu_item.pk, "quantity": 1, "modifications": []}
            ],
        }

        response = self.client.post("/api/orders/", payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("customer_id", response.json())

        payload["customer_id"] = self.customer.pk
        response = self.client.post("/api/orders/", payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("delivery_company_id", response.json())

    def test_create_takeaway_order_allows_optional_customer_and_no_delivery_company(
        self,
    ):
        payload = {
            "order_type": Order.OrderType.TAKEAWAY,
            "branch_id": self.branch.id,
            "items": [
                {"menu_item_id": self.menu_item.pk, "quantity": 1, "modifications": []}
            ],
        }

        response = self.client.post("/api/orders/", payload, format="json")

        self.assertEqual(response.status_code, 201)
        order = Order.objects.get(id=response.json()["order_id"])
        self.assertEqual(order.order_type, Order.OrderType.TAKEAWAY)
        self.assertIsNone(order.customer)
        self.assertIsNone(order.delivery_company)

    def test_create_dine_in_order_allows_no_customer_info(self):
        payload = {
            "order_type": Order.OrderType.DINE_IN,
            "branch_id": self.branch.id,
            "items": [
                {"menu_item_id": self.menu_item.pk, "quantity": 1, "modifications": []}
            ],
        }

        response = self.client.post("/api/orders/", payload, format="json")

        self.assertEqual(response.status_code, 201)
        order = Order.objects.get(id=response.json()["order_id"])
        self.assertEqual(order.order_type, Order.OrderType.DINE_IN)
        self.assertIsNone(order.customer)

    def test_list_order_types_returns_arabic_labels(self):
        response = self.client.get("/api/orders/types/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {"value": "delivery", "label_ar": "توصيل"},
                {"value": "takeaway", "label_ar": "استلام خارجي"},
                {"value": "dine_in", "label_ar": "داخل المطعم"},
            ],
        )

    def test_create_order_with_branch_success(self):
        payload = {
            "customer_id": self.customer.pk,
            "branch_id": self.branch.id,
            "delivery_company_id": self.delivery_company.pk,
            "status": self.status,
            "items": [
                {"menu_item_id": self.menu_item.pk, "quantity": 2, "modifications": []}
            ],
        }

        response = self.client.post("/api/orders/", payload, format="json")

        self.assertEqual(response.status_code, 201)

        order = Order.objects.get(id=response.json()["order_id"])

        self.assertEqual(order.branch, self.branch)

    def test_create_order_with_delivery_company_success(self):
        payload = {
            "customer_id": self.customer.pk,
            "branch_id": self.branch.id,
            "delivery_company_id": self.delivery_company.pk,
            "status": self.status,
            "items": [
                {"menu_item_id": self.menu_item.pk, "quantity": 2, "modifications": []}
            ],
        }

        response = self.client.post("/api/orders/", payload, format="json")

        self.assertEqual(response.status_code, 201)

        order = Order.objects.get(id=response.json()["order_id"])

        self.assertEqual(order.delivery_company, self.delivery_company)

    def test_create_order_rejects_menu_item_not_available_for_branch(self):
        other_branch = Branch.objects.create(name="Second Branch")
        self.menu_item.branches.set([self.branch])

        payload = {
            "customer_id": self.customer.pk,
            "branch_id": other_branch.id,
            "delivery_company_id": self.delivery_company.pk,
            "status": self.status,
            "items": [
                {"menu_item_id": self.menu_item.pk, "quantity": 2, "modifications": []}
            ],
        }

        response = self.client.post("/api/orders/", payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("not available", str(response.text))

    def test_order_creation_invalid_order_not_exist(self):
        payload = {
            "customer_id": self.customer.pk,
            "branch_id": self.branch.id,
            "delivery_company_id": self.delivery_company.pk,
            "status": self.status,
            "items": [
                {
                    "menu_item_id": 999,  # non-existent menu item
                    "quantity": 2,
                    "modifications": [],
                }
            ],
        }

        response = self.client.post("/api/orders/", payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid menu_item_id", str(response.text))

    def test_order_creation_customer_not_exist(self):
        payload = {
            "customer_id": 999,  # non-existent customer
            "branch_id": self.branch.id,
            "delivery_company_id": self.delivery_company.pk,
            "status": self.status,
            "items": [
                {"menu_item_id": self.menu_item.pk, "quantity": 2, "modifications": []}
            ],
        }

        response = self.client.post("/api/orders/", payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid customer_id", str(response.text))

    def test_order_creation_no_items(self):
        payload = {
            "customer_id": self.customer.pk,
            "branch_id": self.branch.id,
            "delivery_company_id": self.delivery_company.pk,
            "status": self.status,
            "items": [],  # no items
        }

        response = self.client.post("/api/orders/", payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Order must have at least one item", str(response.text))

    def test_order_create_error_menu_item_not_exist(self):
        payload = {
            "customer_id": self.customer.pk,
            "branch_id": self.branch.id,
            "delivery_company_id": self.delivery_company.pk,
            "status": self.status,
            "items": [
                {
                    "menu_item_id": 999,  # non-existent menu item
                    "quantity": 2,
                    "modifications": [],
                }
            ],
        }

        response = self.client.post("/api/orders/", payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid menu_item_id", str(response.text))

    def test_order_create_error_ingredient_not_exist(self):
        payload = {
            "customer_id": self.customer.pk,
            "branch_id": self.branch.id,
            "delivery_company_id": self.delivery_company.pk,
            "status": self.status,
            "items": [
                {
                    "menu_item_id": self.menu_item.pk,
                    "quantity": 2,
                    "modifications": [
                        {
                            "ingredient_id": 999,  # non-existent ingredient
                            "type": "added",
                            "quantity": 1,
                            "name_ar": "جبنة",
                        }
                    ],
                }
            ],
        }

        response = self.client.post("/api/orders/", payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid ingredient_id", str(response.text))


class CustomerAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_customer_success(self):
        payload = {"name": "Omar", "email": "omar@example.com"}
        response = self.client.post("/api/orders/customers/", payload, format="json")
        data = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            data, {"message": "Customer created successfully", "customer_id": 1}
        )

    def test_create_customer_missing_name(self):
        payload = {"email": "omar@example.com"}
        response = self.client.post("/api/orders/customers/", payload, format="json")
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertIn("name", data)

    def test_fetch_all_customers(self):
        # Create some customers
        # Create some customers
        Customer.objects.create(name="Omar", email="omar@example.com")
        Customer.objects.create(name="Ali", email="ali@example.com")

        # Fetch the customers
        response = self.client.get("/api/orders/customers/list/")
        data = response.json()

        # Assert the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["count"], 2)
        self.assertIsNone(data["next"])
        self.assertIsNone(data["previous"])
        self.assertEqual(len(data["results"]), 2)
        self.assertEqual(data["results"][0]["name"], "Omar")
        self.assertEqual(data["results"][0]["email"], "omar@example.com")
        self.assertEqual(data["results"][1]["name"], "Ali")
        self.assertEqual(data["results"][1]["email"], "ali@example.com")

    def test_fetch_customers_can_be_paginated(self):
        for index in range(3):
            Customer.objects.create(
                name=f"Customer {index}", email=f"customer-{index}@example.com"
            )

        response = self.client.get("/api/orders/customers/list/?page_size=2")
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["count"], 3)
        self.assertIsNotNone(data["next"])
        self.assertIsNone(data["previous"])
        self.assertEqual(len(data["results"]), 2)

    def test_search_customer_found(self):
        customer = Customer.objects.create(
            name="Omar", email="omar@test.com", phone_number="0771234567"
        )

        response = self.client.get("/api/orders/customers/search/?phone=0771234567")

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertTrue(data["exists"])

        self.assertEqual(data["customer"]["id"], customer.id)

    def test_search_customer_not_found(self):
        response = self.client.get("/api/orders/customers/search/?phone=0000000000")

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertFalse(data["exists"])

    def test_search_customer_without_phone(self):
        response = self.client.get("/api/orders/customers/search/")

        self.assertEqual(response.status_code, 400)

        self.assertEqual(response.json()["error"], "Phone required")

    def test_update_customer_success(self):
        customer = Customer.objects.create(
            name="Omar",
            email="omar@test.com",
            phone_number="0771234567",
            address="Amsterdam",
        )

        response = self.client.patch(
            f"/api/orders/customers/{customer.id}/",
            {"name": "Omar Updated", "address": "Rotterdam"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        customer.refresh_from_db()

        self.assertEqual(customer.name, "Omar Updated")

        self.assertEqual(customer.address, "Rotterdam")

        self.assertEqual(customer.email, "omar@test.com")

        data = response.json()

        self.assertEqual(data["id"], customer.id)

        self.assertEqual(data["name"], "Omar Updated")

    def test_update_customer_allows_blank_optional_fields(self):
        customer = Customer.objects.create(
            name="Omar",
            email="omar@test.com",
            phone_number="0771234567",
            address="Amsterdam",
        )

        response = self.client.patch(
            f"/api/orders/customers/{customer.id}/",
            {"email": "", "phone_number": "", "address": ""},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        customer.refresh_from_db()

        self.assertEqual(customer.email, "")

        self.assertEqual(customer.phone_number, "")

        self.assertEqual(customer.address, "")

    def test_update_customer_rejects_duplicate_email(self):
        Customer.objects.create(name="Ali", email="ali@test.com")

        customer = Customer.objects.create(name="Omar", email="omar@test.com")

        response = self.client.patch(
            f"/api/orders/customers/{customer.id}/",
            {"email": "ali@test.com"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.assertIn("email", response.json())

    def test_update_customer_not_found(self):
        response = self.client.patch(
            "/api/orders/customers/999/", {"name": "Missing"}, format="json"
        )

        self.assertEqual(response.status_code, 404)
