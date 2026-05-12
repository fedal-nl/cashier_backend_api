from django.test import TestCase
from django.db import IntegrityError

from menu.models import (
    Category,
    Quantity,
    MenuItem,
    Ingredient,
    MenuItemIngredient,
)


class CategoryModelTest(TestCase):

    def test_create_category(self):
        category = Category.objects.create(
            name_en="Food",
            name_ar="طعام"
        )
        self.assertEqual(category.name_en, "Food")
        self.assertTrue(category.is_active)

    def test_category_str(self):
        category = Category.objects.create(
            name_en="Drinks",
            name_ar="مشروبات"
        )
        self.assertEqual(str(category), "Drinks - مشروبات")


class QuantityModelTest(TestCase):

    def test_create_quantity(self):
        quantity = Quantity.objects.create(
            name_en="Small",
            name_ar="صغير"
        )
        self.assertEqual(quantity.name_en, "Small")

    def test_quantity_str(self):
        quantity = Quantity.objects.create(
            name_en="Large",
            name_ar="كبير"
        )
        self.assertEqual(str(quantity), "Large - كبير")


class IngredientModelTest(TestCase):

    def test_create_ingredient(self):
        ingredient = Ingredient.objects.create(
            name_en="Cheese",
            name_ar="جبنة"
        )
        self.assertTrue(ingredient.is_active)

    def test_ingredient_str(self):
        ingredient = Ingredient.objects.create(
            name_en="Tomato",
            name_ar="طماطم"
        )
        self.assertEqual(str(ingredient), "Tomato - طماطم")


class MenuItemModelTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(
            name_en="Food",
            name_ar="طعام"
        )
        self.quantity = Quantity.objects.create(
            name_en="Regular",
            name_ar="عادي"
        )

    def test_create_menu_item(self):
        item = MenuItem.objects.create(
            name_en="Burger",
            name_ar="برجر",
            price=12.50,
            category=self.category,
            quantity=self.quantity
        )

        self.assertEqual(item.name_en, "Burger")
        self.assertEqual(item.price, 12.50)
        self.assertTrue(item.is_active)

    def test_menu_item_str(self):
        item = MenuItem.objects.create(
            name_en="Pizza",
            name_ar="بيتزا",
            price=15,
            category=self.category,
            quantity=self.quantity
        )

        self.assertEqual(str(item), "Pizza - بيتزا")


class MenuItemIngredientTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(
            name_en="Food",
            name_ar="طعام"
        )

        self.quantity = Quantity.objects.create(
            name_en="Regular",
            name_ar="عادي"
        )

        self.menu_item = MenuItem.objects.create(
            name_en="Burger",
            name_ar="برجر",
            price=10,
            category=self.category,
            quantity=self.quantity
        )

        self.ingredient = Ingredient.objects.create(
            name_en="Cheese",
            name_ar="جبنة"
        )

    def test_create_menu_item_ingredient(self):
        relation = MenuItemIngredient.objects.create(
            menu_item=self.menu_item,
            ingredient=self.ingredient
        )

        self.assertTrue(relation.is_default)
        self.assertTrue(relation.is_removable)
        self.assertTrue(relation.is_addable)

    def test_unique_constraint(self):
        MenuItemIngredient.objects.create(
            menu_item=self.menu_item,
            ingredient=self.ingredient
        )

        with self.assertRaises(IntegrityError):
            MenuItemIngredient.objects.create(
                menu_item=self.menu_item,
                ingredient=self.ingredient
            )

    def test_string_representation(self):
        relation = MenuItemIngredient.objects.create(
            menu_item=self.menu_item,
            ingredient=self.ingredient
        )

        expected = "Burger - برجر | Cheese - جبنة"
        self.assertEqual(str(relation), expected)
