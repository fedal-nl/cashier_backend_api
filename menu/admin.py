from django.contrib import admin
from django import forms

from .models import Branch, Category, Unit, MenuItem, Ingredient, MenuItemIngredient


class MenuItemAdminForm(forms.ModelForm):
    branches = forms.ModelMultipleChoiceField(
        queryset=Branch.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = MenuItem
        fields = "__all__"


class MenuItemAdmin(admin.ModelAdmin):
    form = MenuItemAdminForm

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        if not form.cleaned_data.get("branches"):
            form.instance.branches.set(Branch.objects.all())


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name_ar", "admin_ranking", "frontend_ranking", "is_active")
    list_editable = ("admin_ranking", "frontend_ranking", "is_active")
    ordering = ("admin_ranking", "name_ar", "id")


# Register your models here.
admin.site.register(Branch)
admin.site.register(Unit)
admin.site.register(MenuItem, MenuItemAdmin)
admin.site.register(Ingredient)
admin.site.register(MenuItemIngredient)
