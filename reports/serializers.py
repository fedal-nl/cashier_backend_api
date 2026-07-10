from rest_framework import serializers

from menu.models import Branch
from orders.models import Order


class DailyReportQuerySerializer(serializers.Serializer):
    date_from = serializers.DateField()
    date_to = serializers.DateField()
    branch_id = serializers.IntegerField(required=False)
    status = serializers.ChoiceField(choices=Order.OrderStatus.choices, required=False)

    def validate(self, attrs):
        if attrs["date_from"] > attrs["date_to"]:
            raise serializers.ValidationError(
                {"date_to": "date_to must be greater than or equal to date_from."}
            )

        return attrs

    def validate_branch_id(self, value):
        try:
            return Branch.objects.get(id=value, is_active=True)
        except Branch.DoesNotExist:
            raise serializers.ValidationError("Invalid branch_id")


class DailyReportResponseSerializer(serializers.Serializer):
    date = serializers.DateField()
    branch_id = serializers.IntegerField()
    branch_name = serializers.CharField()
    total_orders = serializers.IntegerField()
    orders_by_status = serializers.DictField(child=serializers.IntegerField())
    total_existing_customers_ordered = serializers.IntegerField()
    total_new_customers_ordered = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
