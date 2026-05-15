from django.test import TestCase
from django.db import IntegrityError

from menu.models import (
    Category,
    Unit,
    MenuItem,
    Ingredient,
    MenuItemIngredient,
)


class CategoryModelTest(TestCase):

    def test_create_category(self):
        category = Category.objects.create(
            name_ar="طعام"
        )
        self.assertEqual(category.name_ar, "طعام")
        self.assertTrue(category.is_active)

    def test_category_str(self):
        category = Category.objects.create(
            name_ar="مشروبات"
        )
        self.assertEqual(str(category), "مشروبات")



class UnitModelTest(TestCase):

    def test_create_unit(self):
        unit = Unit.objects.create(
            name_ar="صغير"
        )
        self.assertEqual(unit.name_ar, "صغير")

    def test_unit_str(self):
        unit = Unit.objects.create(
            name_ar="كبير"
        )
        self.assertEqual(str(unit), "كبير")


class IngredientModelTest(TestCase):

    def test_create_ingredient(self):
        ingredient = Ingredient.objects.create(
            name_ar="جبنة"
        )
        self.assertTrue(ingredient.is_active)

    def test_ingredient_str(self):
        ingredient = Ingredient.objects.create(
            name_ar="طماطم"
        )
        self.assertEqual(str(ingredient), "طماطم")


class MenuItemModelTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(
            name_ar="طعام"
        )
        self.unit = Unit.objects.create(
            name_ar="عادي"
        )

    def test_create_menu_item(self):
        item = MenuItem.objects.create(
            name_ar="برجر",
            price=12.50,
            category=self.category,
            unit=self.unit
        )

        self.assertEqual(item.name_ar, "برجر")
        self.assertEqual(item.price, 12.50)
        self.assertTrue(item.is_active)

    def test_menu_item_str(self):
        item = MenuItem.objects.create(
            name_ar="بيتزا",
            price=15,
            category=self.category,
            unit=self.unit
        )

        self.assertEqual(str(item), "بيتزا")


class MenuItemIngredientTest(TestCase):

    def setUp(self):
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
            unit=self.unit
        )

        self.ingredient = Ingredient.objects.create(
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

        expected = "برجر | جبنة"
        self.assertEqual(str(relation), expected)
