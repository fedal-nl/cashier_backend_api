# menu/urls.py
from django.urls import path
from .views import (
    BranchListView,
    MenuListView,
    CategoryListView,
    UnitListView,
    IngredientListView,
    MenuItemIngredientListView,
)

urlpatterns = [
    path("branches/", BranchListView.as_view(), name="branch-list"),
    path("menus/", MenuListView.as_view(), name="menu-list"),
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("units/", UnitListView.as_view(), name="unit-list"),
    path("ingredients/", IngredientListView.as_view(), name="ingredient-list"),
    path("menu-item-ingredients/", MenuItemIngredientListView.as_view(), name="menu-item-ingredient-list"),
]
