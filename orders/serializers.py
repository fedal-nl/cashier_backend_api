from rest_framework import serializers
from .models import (
    Customer,
    DeliveryCompany,
    Order,
    OrderItem,
    OrderItemModification,
    OrderLog,
)
from menu.models import Ingredient, MenuItem
from menu.models import Branch
from menu.serializers import BranchSerializer
from .services import create_order, replace_order_items


class OrderItemModificationInputSerializer(serializers.Serializer):
    ingredient_id = serializers.IntegerField()
    name_ar = serializers.CharField(max_length=255)
    type = serializers.ChoiceField(choices=OrderItemModification.Actions.choices)
    quantity = serializers.IntegerField(default=1)


class OrderItemModificationOutputSerializer(serializers.ModelSerializer):
    ingredient_id = serializers.IntegerField(source="ingredient.id")
    ingredient_name_ar = serializers.CharField(source="ingredient.name_ar")
    ingredient_price = serializers.DecimalField(
        source="ingredient.price", max_digits=10, decimal_places=2
    )
    unit_id = serializers.IntegerField(source="ingredient.unit.id", allow_null=True)
    unit_name_ar = serializers.CharField(
        source="ingredient.unit.name_ar", allow_null=True
    )

    class Meta:
        model = OrderItemModification
        fields = [
            "id",
            "ingredient_id",
            "ingredient_name_ar",
            "ingredient_price",
            "unit_id",
            "unit_name_ar",
            "quantity",
            "modification_type",
        ]


class OrderItemInputSerializer(serializers.Serializer):
    menu_item_id = serializers.IntegerField()
    quantity = serializers.IntegerField()
    note = serializers.CharField(max_length=255, required=False, allow_blank=True)
    modifications = OrderItemModificationInputSerializer(many=True, required=False)


class OrderItemOutputSerializer(serializers.ModelSerializer):
    menu_item_id = serializers.IntegerField(source="menu_item.id")

    modifications = OrderItemModificationOutputSerializer(many=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "menu_item_id",
            "menu_item_name_ar",
            "menu_item_base_price",
            "quantity",
            "total_price",
            "order_item_note",
            "modifications",
        ]


class CustomerInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone_number = serializers.CharField(
        max_length=20, required=False, allow_blank=True
    )
    address = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def create(self, validated_data):
        return Customer.objects.create(**validated_data)


class CustomerOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "name", "email", "phone_number", "address"]


class PaginatedCustomerOutputSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)
    results = CustomerOutputSerializer(many=True)


class DeliveryCompanyOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryCompany
        fields = [
            "id",
            "name",
            "phone_number",
            "website",
            "contact_person",
        ]


class OrderTypeSerializer(serializers.Serializer):
    value = serializers.CharField()
    label_ar = serializers.CharField()


class CustomerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["name", "email", "phone_number", "address"]
        extra_kwargs = {
            "name": {"required": False},
            "email": {"required": False, "allow_blank": True, "allow_null": True},
            "phone_number": {
                "required": False,
                "allow_blank": True,
                "allow_null": True,
            },
            "address": {"required": False, "allow_blank": True, "allow_null": True},
        }


def build_order_items_data(items: list[dict]) -> list[dict]:
    items_data = []
    for item in items:
        try:
            menu_item = MenuItem.objects.get(id=item["menu_item_id"])
        except MenuItem.DoesNotExist:
            raise serializers.ValidationError(
                f"Invalid menu_item_id: {item['menu_item_id']}"
            )

        modifications_data = []
        for mod in item.get("modifications", []):
            try:
                ingredient = Ingredient.objects.get(id=mod["ingredient_id"])
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    f"Invalid ingredient_id: {mod['ingredient_id']}"
                )

            modifications_data.append(
                {
                    "ingredient": ingredient,
                    "name_ar": mod["name_ar"],
                    "type": mod["type"],
                    "quantity": mod.get("quantity", 1),
                }
            )

        items_data.append(
            {
                "menu_item": menu_item,
                "name_ar": menu_item.name_ar,
                "base_price": menu_item.price,
                "quantity": item["quantity"],
                "order_item_note": item.get("note", ""),
                "modifications": modifications_data,
            }
        )

    return items_data


class OrderInputSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField(required=False, allow_null=True)
    branch_id = serializers.IntegerField()
    delivery_company_id = serializers.IntegerField(required=False, allow_null=True)
    order_type = serializers.ChoiceField(
        choices=Order.OrderType.choices, default=Order.OrderType.DELIVERY
    )
    items = OrderItemInputSerializer(many=True)
    note = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate(self, attrs):
        order_type = attrs.get("order_type", Order.OrderType.DELIVERY)
        customer_id = attrs.get("customer_id")
        delivery_company_id = attrs.get("delivery_company_id")

        if order_type == Order.OrderType.DELIVERY:
            if not customer_id:
                raise serializers.ValidationError(
                    {"customer_id": "This field is required for delivery orders."}
                )
            if not delivery_company_id:
                raise serializers.ValidationError(
                    {
                        "delivery_company_id": "This field is required for delivery orders."
                    }
                )

        if customer_id:
            try:
                customer = Customer.objects.get(id=customer_id)
                attrs["customer"] = customer
            except Customer.DoesNotExist:
                raise serializers.ValidationError("Invalid customer_id")
        else:
            attrs["customer"] = None

        if delivery_company_id:
            try:
                delivery_company = DeliveryCompany.objects.get(id=delivery_company_id)
                attrs["delivery_company"] = delivery_company
            except DeliveryCompany.DoesNotExist:
                raise serializers.ValidationError("Invalid delivery_company_id")
        else:
            attrs["delivery_company"] = None

        try:
            branch = Branch.objects.get(id=attrs["branch_id"], is_active=True)
            attrs["branch"] = branch
        except Branch.DoesNotExist:
            raise serializers.ValidationError("Invalid branch_id")

        # check that there is at least one item in the order
        if not attrs["items"]:
            raise serializers.ValidationError("Order must have at least one item")

        for item in attrs["items"]:
            if not MenuItem.objects.filter(id=item["menu_item_id"]).exists():
                raise serializers.ValidationError(
                    f"Invalid menu_item_id: {item['menu_item_id']}"
                )

            if not MenuItem.objects.filter(
                id=item["menu_item_id"], branches=branch
            ).exists():
                raise serializers.ValidationError(
                    f"menu_item_id {item['menu_item_id']} is not available for this branch"
                )

        return attrs

    def create(self, validated_data: dict) -> Order:
        user = validated_data.pop("user", None)
        items_data = build_order_items_data(validated_data["items"])

        order = create_order(
            customer=validated_data["customer"],
            branch=validated_data.get("branch"),
            delivery_company=validated_data["delivery_company"],
            order_type=validated_data.get("order_type", Order.OrderType.DELIVERY),
            status=validated_data.get("status", Order.OrderStatus.CREATED),
            items_data=items_data,
            note=validated_data.get("note", ""),
            user=user,
        )
        return order


class OrderUpdateSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField(required=False, allow_null=True)
    branch_id = serializers.IntegerField(required=False)
    delivery_company_id = serializers.IntegerField(required=False, allow_null=True)
    status = serializers.ChoiceField(
        choices=Order.OrderStatus.choices,
        required=False,
    )
    order_type = serializers.ChoiceField(
        choices=Order.OrderType.choices,
        required=False,
    )
    items = OrderItemInputSerializer(many=True, required=False)
    note = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    def validate(self, attrs):
        order = self.instance

        if order is None:
            raise serializers.ValidationError("Order instance is required")

        if not self.partial:
            missing_fields = [
                field
                for field in ["branch_id", "order_type"]
                if field not in attrs
            ]
            if missing_fields:
                raise serializers.ValidationError(
                    {
                        field: "This field is required."
                        for field in missing_fields
                    }
                )

        effective_order_type = attrs.get("order_type", order.order_type)
        effective_customer_id = attrs.get("customer_id", order.customer_id)
        effective_delivery_company_id = attrs.get(
            "delivery_company_id",
            order.delivery_company_id,
        )

        if effective_order_type == Order.OrderType.DELIVERY:
            if not effective_customer_id:
                raise serializers.ValidationError(
                    {"customer_id": "This field is required for delivery orders."}
                )
            if not effective_delivery_company_id:
                raise serializers.ValidationError(
                    {
                        "delivery_company_id": "This field is required for delivery orders."
                    }
                )

        if "customer_id" in attrs:
            customer_id = attrs.get("customer_id")
            if customer_id is None:
                attrs["customer"] = None
            else:
                try:
                    attrs["customer"] = Customer.objects.get(id=customer_id)
                except Customer.DoesNotExist:
                    raise serializers.ValidationError("Invalid customer_id")

        if "delivery_company_id" in attrs:
            delivery_company_id = attrs.get("delivery_company_id")
            if delivery_company_id is None:
                attrs["delivery_company"] = None
            else:
                try:
                    attrs["delivery_company"] = DeliveryCompany.objects.get(
                        id=delivery_company_id
                    )
                except DeliveryCompany.DoesNotExist:
                    raise serializers.ValidationError("Invalid delivery_company_id")

        if "branch_id" in attrs:
            try:
                attrs["branch"] = Branch.objects.get(
                    id=attrs["branch_id"],
                    is_active=True,
                )
            except Branch.DoesNotExist:
                raise serializers.ValidationError("Invalid branch_id")

        branch = attrs.get("branch", order.branch)

        if "items" in attrs:
            if not attrs["items"]:
                raise serializers.ValidationError("Order must have at least one item")

            for item in attrs["items"]:
                if not MenuItem.objects.filter(id=item["menu_item_id"]).exists():
                    raise serializers.ValidationError(
                        f"Invalid menu_item_id: {item['menu_item_id']}"
                    )

                if not MenuItem.objects.filter(
                    id=item["menu_item_id"], branches=branch
                ).exists():
                    raise serializers.ValidationError(
                        f"menu_item_id {item['menu_item_id']} is not available for this branch"
                    )

        return attrs

    def update(self, instance, validated_data):
        for input_field in [
            "customer_id",
            "delivery_company_id",
            "branch_id",
        ]:
            validated_data.pop(input_field, None)

        for field in [
            "customer",
            "branch",
            "delivery_company",
            "order_type",
            "status",
            "note",
        ]:
            if field in validated_data:
                setattr(instance, field, validated_data[field])

        items = validated_data.pop("items", None)

        instance.save()

        if items is not None:
            replace_order_items(
                order=instance,
                items_data=build_order_items_data(items),
            )

        return instance


class OrderOutputSerializer(serializers.ModelSerializer):
    customer = CustomerOutputSerializer(allow_null=True)
    branch = BranchSerializer()
    delivery_company = DeliveryCompanyOutputSerializer(allow_null=True)
    order_type_label_ar = serializers.CharField(source="get_order_type_display")
    items = OrderItemOutputSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "branch",
            "delivery_company",
            "status",
            "order_type",
            "order_type_label_ar",
            "note",
            "created_at",
            "items",
            "total_price",
            "updated_at",
        ]


class PaginatedOrderOutputSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)
    results = OrderOutputSerializer(many=True)


class TodayOrderSummarySerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_existing_customers_ordered = serializers.IntegerField()
    total_new_customers_ordered = serializers.IntegerField()
    orders_by_status = serializers.DictField(child=serializers.IntegerField())


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.OrderStatus.choices)
    delivery_company_id = serializers.IntegerField(required=False)

    def validate_delivery_company_id(self, value):
        try:
            return DeliveryCompany.objects.get(id=value)
        except DeliveryCompany.DoesNotExist:
            raise serializers.ValidationError("Invalid delivery_company_id")

    def validate(self, attrs):
        return attrs


class OrderLogOutputSerializer(serializers.ModelSerializer):
    order_id = serializers.UUIDField(source="order.id")
    customer = CustomerOutputSerializer(allow_null=True)
    created_by_username = serializers.CharField(
        source="created_by.username", allow_null=True
    )

    class Meta:
        model = OrderLog
        fields = [
            "id",
            "order_id",
            "customer",
            "event_type",
            "previous_status",
            "new_status",
            "created_by_username",
            "created_at",
        ]
