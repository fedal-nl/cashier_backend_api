from rest_framework import serializers
from .models import Order, OrderItemModification, Customer, OrderItem
from menu.models import Ingredient, MenuItem
from .services import create_order


class OrderItemModificationInputSerializer(serializers.Serializer):
    ingredient_id = serializers.IntegerField()
    name_ar = serializers.CharField(max_length=255)
    type = serializers.ChoiceField(choices=OrderItemModification.Actions.choices)
    quantity = serializers.IntegerField(default=1)


class OrderItemModificationOutputSerializer(serializers.ModelSerializer):
    ingredient_id = serializers.IntegerField(source='ingredient.id')
    ingredient_name_ar = serializers.CharField(source='ingredient.name_ar')
    ingredient_price = serializers.DecimalField(source='ingredient.price', max_digits=10, decimal_places=2)
    unit_id = serializers.IntegerField(source='ingredient.unit.id', allow_null=True)
    unit_name_ar = serializers.CharField(source='ingredient.unit.name_ar', allow_null=True)

    class Meta:
        model = OrderItemModification
        fields = [
            'id',
            'ingredient_id',
            'ingredient_name_ar',
            'ingredient_price',
            'unit_id',
            'unit_name_ar',
            'quantity',
            'modification_type'
        ]


class OrderItemInputSerializer(serializers.Serializer):
    menu_item_id = serializers.IntegerField()
    quantity = serializers.IntegerField()
    modifications = OrderItemModificationInputSerializer(many=True, required=False)


class OrderItemOutputSerializer(serializers.ModelSerializer):
    menu_item_id = serializers.IntegerField(source='menu_item.id')
    menu_item_name_ar = serializers.CharField(source='menu_item.name_ar')
    menu_item_base_price = serializers.DecimalField(source='menu_item.base_price', max_digits=10, decimal_places=2)
    modifications = OrderItemModificationOutputSerializer(many=True)

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'menu_item_id',
            'menu_item_name_ar',
            'menu_item_base_price',
            'quantity',
            'total_price',
            'modifications'
        ]


class CustomerInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    address = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def create(self, validated_data):
        return Customer.objects.create(**validated_data)


class CustomerOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'phone_number', 'address']


class OrderInputSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    items = OrderItemInputSerializer(many=True)
    note = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate(self, attrs):
        
        # check that the customer exists
        try:
            customer = Customer.objects.get(id=attrs['customer_id'])
            attrs['customer'] = customer
        except Customer.DoesNotExist:
            raise serializers.ValidationError("Invalid customer_id")
        
        # check that there is at least one item in the order
        if not attrs['items']:
            raise serializers.ValidationError("Order must have at least one item")
        
        return attrs
        
    def create(self, validated_data: dict) -> Order:
        # Convert the input data into the format expected by the create_order service function
        items_data = []
        for item in validated_data['items']:
            try:
                menu_item = MenuItem.objects.get(id=item['menu_item_id'])
            except MenuItem.DoesNotExist:
                raise serializers.ValidationError(f"Invalid menu_item_id: {item['menu_item_id']}")
            
            modifications_data = []
            for mod in item.get('modifications', []):
                try:
                    ingredient = Ingredient.objects.get(id=mod['ingredient_id'])
                except Ingredient.DoesNotExist:
                    raise serializers.ValidationError(f"Invalid ingredient_id: {mod['ingredient_id']}")
                
                modifications_data.append({
                    "ingredient": ingredient,
                    "name_ar": mod['name_ar'],
                    "type": mod['type'],
                    "quantity": mod.get('quantity', 1)
                })
            
            items_data.append({
                "menu_item": menu_item,
                "name_ar": menu_item.name_ar,
                "base_price": menu_item.price,
                "quantity": item['quantity'],
                "modifications": modifications_data
            })
        
        order = create_order(
            customer=validated_data['customer'],
            status=validated_data.get('status', Order.OrderStatus.CREATED),
            items_data=items_data,
            note=validated_data.get('note', "")
        )
        return order


class OrderOutputSerializer(serializers.ModelSerializer):
    customer = CustomerOutputSerializer()
    items = OrderItemOutputSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'status', 'note', 'created_at', 'items']


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=Order.OrderStatus.choices
    )