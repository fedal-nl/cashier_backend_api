from django.contrib import admin
from .models import Category, Quantity, MenuItem, Ingredient, MenuItemIngredient

# Register your models here.
admin.site.register(Category)
admin.site.register(Quantity)
admin.site.register(MenuItem)
admin.site.register(Ingredient)
admin.site.register(MenuItemIngredient)
