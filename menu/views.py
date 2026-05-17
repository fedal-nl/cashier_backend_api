from rest_framework.generics import ListAPIView
from .models import Category, Unit, MenuItem, Ingredient, MenuItemIngredient
from .serializers import CategorySerializer, MenuItemSerializer, UnitSerializer, IngredientSerializer, MenuItemIngredientSerializer


class MenuListView(ListAPIView):
    queryset = Category.objects.prefetch_related('items').filter(is_active=True)
    serializer_class = CategorySerializer


class CategoryListView(ListAPIView):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer


class UnitListView(ListAPIView):
    queryset = Unit.objects.filter(is_active=True)
    serializer_class = UnitSerializer


class IngredientListView(ListAPIView):
    queryset = Ingredient.objects.filter(is_active=True)
    serializer_class = IngredientSerializer


class MenuItemIngredientListView(ListAPIView):
    queryset = MenuItemIngredient.objects.filter(menu_item__is_active=True)
    serializer_class = MenuItemIngredientSerializer
