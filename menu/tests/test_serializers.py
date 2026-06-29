from django.test import TestCase

from menu.models import Category, MenuItem, Unit
from menu.serializers import MenuItemSerializer


class MenuItemSerializerTest(TestCase):
    def test_menu_item_output_includes_label_ar(self):
        category = Category.objects.create(name_ar="طعام")
        unit = Unit.objects.create(name_ar="عادي")
        item = MenuItem.objects.create(
            name_ar="برجر",
            label_ar="برجر كلاسيك",
            price=10,
            category=category,
            unit=unit,
        )

        data = MenuItemSerializer(item).data

        self.assertEqual(data["label_ar"], "برجر كلاسيك")
