from django.db import models

# Create your models here.

class Category(models.Model):
    name_en = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    # make the default ordering by id
    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.name_en} - {self.name_ar}"

class Quantity(models.Model):
    name_en = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    # make the default ordering by id
    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.name_en} - {self.name_ar}"

class MenuItem(models.Model):
    name_en = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100)
    description_en = models.TextField(default='', blank=True, null=True)
    description_ar = models.TextField(default='', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    quantity = models.ForeignKey(Quantity, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='menu_items/', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    # make the default ordering by id
    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.name_en} - {self.name_ar}"
    

class Ingredient(models.Model):
    name_en = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    # make the default ordering by id
    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.name_en} - {self.name_ar}"
    

class MenuItemIngredient(models.Model):
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name='ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)

    is_default = models.BooleanField(default=True)

    is_removable = models.BooleanField(default=True)

    is_addable = models.BooleanField(default=True)

    # make the default ordering by id
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['menu_item', 'ingredient'],
                name='unique_menu_item_ingredient'
            )
        ]
        ordering = ['id']

    def __str__(self):
        return f"{self.menu_item.name_en} - {self.menu_item.name_ar} | {self.ingredient.name_en} - {self.ingredient.name_ar}"
