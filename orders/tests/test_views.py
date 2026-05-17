from django.test import TestCase
from rest_framework.test import APIClient

from orders.models import Customer, OrderStatus
from menu.models import Category, Unit, MenuItem, Ingredient


class OrderAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.customer = Customer.objects.create(
            id=1,
            name="Omar",
            email="omar@test.com"
        )

        self.status = OrderStatus.objects.create(
            id=1,
            name_ar="تم الإنشاء"
        )

        self.category = Category.objects.create(
            id=1,
            name_ar="طعام"
        )

        self.unit = Unit.objects.create(
            id=1,
            name_ar="عادي"
        )

        self.menu_item = MenuItem.objects.create(
            id=1,
            name_ar="برجر",
            price=10,
            category=self.category,
            unit=self.unit
        )

        self.ingredient = Ingredient.objects.create(
            id=1,
            name_ar="جبنة",
            price=2,
            unit=self.unit
        )

    def test_create_order_success(self):
        payload = {
            "customer_id": self.customer.pk,
            "status_id": self.status.pk,
            "items": [
                {
                    "menu_item_id": self.menu_item.pk,
                    "quantity": 2,
                    "modifications": [
                        {
                            "ingredient_id": self.ingredient.pk,
                            "type": "added",
                            "quantity": 1,
                            "name_ar": "جبنة"
                        }
                    ]
                }
            ]
        }

        response = self.client.post("/api/orders/", payload, format="json")

        self.assertEqual(response.status_code, 201)

    def test_order_creation_invalid_status_not_exist(self):
        payload = {
            "customer_id": self.customer.pk,
            "status_id": 999,  # non-existent status
            "items": [
                {
                    "menu_item_id": self.menu_item.pk,
                    "quantity": 2,
                    "modifications": []
                }
            ]
        }

        response = self.client.post("/api/orders/", payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid status_id", str(response.text))

    def test_order_creation_invalid_order_not_exist(self):
        payload = {
            "customer_id": self.customer.pk,
            "status_id": self.status.pk,
            "items": [
                {
                    "menu_item_id": 999,  # non-existent menu item
                    "quantity": 2,
                    "modifications": []
                }
            ]
        }

        response = self.client.post("/api/orders/", payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid menu_item_id", str(response.text))

    def test_order_creation_customer_not_exist(self):
        payload = {
            "customer_id": 999,  # non-existent customer
            "status_id": self.status.pk,
            "items": [
                {
                    "menu_item_id": self.menu_item.pk,
                    "quantity": 2,
                    "modifications": []
                }
            ]
        }

        response = self.client.post("/api/orders/", payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid customer_id", str(response.text))

    def test_order_creation_no_items(self):
        payload = {
            "customer_id": self.customer.pk,
            "status_id": self.status.pk,
            "items": []  # no items
        }

        response = self.client.post("/api/orders/", payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Order must have at least one item", str(response.text))

    def test_order_create_error_menu_item_not_exist(self):
        payload = {
            "customer_id": self.customer.pk,
            "status_id": self.status.pk,
            "items": [
                {
                    "menu_item_id": 999,  # non-existent menu item
                    "quantity": 2,
                    "modifications": []
                }
            ]
        }

        response = self.client.post("/api/orders/", payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid menu_item_id", str(response.text))
    
    def test_order_create_error_ingredient_not_exist(self):
        payload = {
            "customer_id": self.customer.pk,
            "status_id": self.status.pk,
            "items": [
                {
                    "menu_item_id": self.menu_item.pk,
                    "quantity": 2,
                    "modifications": [
                        {
                            "ingredient_id": 999,  # non-existent ingredient
                            "type": "added",
                            "quantity": 1,
                            "name_ar": "جبنة"
                        }
                    ]
                }
            ]
        }

        response = self.client.post("/api/orders/", payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid ingredient_id", str(response.text))


class CustomerAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_create_customer_success(self):
        payload = {
            "name": "Omar",
            "email": "omar@example.com"
        }
        response = self.client.post("/api/orders/customers/", payload, format="json")
        data = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data, {'message': 'Customer created successfully', 'customer_id': 1})

    def test_create_customer_missing_name(self):
        payload = {
            "email": "omar@example.com"
        }
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
        # self.assertEqual(data, "")
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['name'], "Omar")
        self.assertEqual(data[0]['email'], "omar@example.com")
        self.assertEqual(data[1]['name'], "Ali")
        self.assertEqual(data[1]['email'], "ali@example.com")
