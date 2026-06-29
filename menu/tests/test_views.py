from django.test import TestCase
from rest_framework.test import APIClient

from menu.models import Branch, Category, MenuItem, Unit


class MenuBranchViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.category = Category.objects.create(name_ar="طعام")
        self.unit = Unit.objects.create(name_ar="عادي")
        self.main_branch = Branch.objects.create(
            name="Main Branch", location="Amsterdam"
        )
        self.second_branch = Branch.objects.create(
            name="Second Branch", location="Rotterdam"
        )

        self.main_item = MenuItem.objects.create(
            name_ar="برجر", price=10, category=self.category, unit=self.unit
        )
        self.second_item = MenuItem.objects.create(
            name_ar="بيتزا", price=12, category=self.category, unit=self.unit
        )
        self.second_item.branches.set([self.second_branch])

    def test_list_branches(self):
        response = self.client.get("/api/menu/branches/")

        data = response.json()

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(data), 2)

        self.assertEqual(data[0]["name"], "Main Branch")

    def test_menu_can_be_filtered_by_branch(self):
        response = self.client.get(f"/api/menu/menus/?branch_id={self.main_branch.id}")

        data = response.json()

        self.assertEqual(response.status_code, 200)

        item_names = [item["name_ar"] for item in data[0]["items"]]

        self.assertEqual(item_names, ["برجر"])

    def test_menu_rejects_invalid_branch(self):
        response = self.client.get("/api/menu/menus/?branch_id=999")

        self.assertEqual(response.status_code, 400)

        self.assertIn("branch_id", response.json())
