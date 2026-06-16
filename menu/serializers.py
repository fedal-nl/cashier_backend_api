from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from .models import Branch, Category, Unit, MenuItem, Ingredient, MenuItemIngredient


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'name', 'location', 'is_active']


class MenuItemIngredientSerializer(serializers.ModelSerializer):
    ingredient_id = serializers.IntegerField(source='ingredient.id')
    ingredient_name_ar = serializers.CharField(source='ingredient.name_ar')
    price = serializers.DecimalField(source='ingredient.price', max_digits=10, decimal_places=2)
    unit_id = serializers.IntegerField(source='ingredient.unit.id', allow_null=True)
    unit_name_ar = serializers.CharField(source='ingredient.unit.name_ar', allow_null=True)

    class Meta:
        model = MenuItemIngredient
        fields = [
            'ingredient_id',
            'ingredient_name_ar',
            'price',
            'unit_id',
            'unit_name_ar',
            'is_default',
            'is_removable',
            'is_addable'
        ]


class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(source='category.id')
    category_name_ar = serializers.CharField(source='category.name_ar')
    unit_id = serializers.IntegerField(source='unit.id', allow_null=True)
    unit_name_ar = serializers.CharField(source='unit.name_ar', allow_null=True)
    ingredients = MenuItemIngredientSerializer(many=True)
    branches = BranchSerializer(many=True)

    class Meta:
        model = MenuItem
        fields = [
            'id',
            'name_ar',
            'label_ar',
            'description_ar',
            'price',
            'category_id',
            'category_name_ar',
            'quantity',
            'unit_id',
            'unit_name_ar',
            'image',
            'is_active',
            'branches',
            'ingredients'
        ]


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'name_ar']


class IngredientSerializer(serializers.ModelSerializer):
    unit_id = serializers.IntegerField(source='unit.id', allow_null=True)
    unit_name_ar = serializers.CharField(source='unit.name_ar', allow_null=True)

    class Meta:
        model = Ingredient
        fields = ['id', 'name_ar', 'price', 'unit_id', 'unit_name_ar', 'is_active']


class CategorySerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name_ar', 'items']

    @extend_schema_field(MenuItemSerializer(many=True))
    def get_items(self, obj):
        items = obj.items.filter(
            is_active=True
        ).prefetch_related(
            'branches',
            'ingredients__ingredient',
            'ingredients__ingredient__unit'
        )

        branch_id = self.context.get('branch_id')

        if branch_id:
            items = items.filter(
                branches__id=branch_id
            )

        return MenuItemSerializer(
            items.distinct(),
            many=True
        ).data
