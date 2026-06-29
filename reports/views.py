from datetime import date, timedelta
from decimal import Decimal
from typing import NotRequired, TypedDict, cast

from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from menu.models import Branch
from orders.models import Order

from .serializers import DailyReportQuerySerializer, DailyReportResponseSerializer


class DailyReportValidatedData(TypedDict):
    date_from: date
    date_to: date
    branch_id: NotRequired[Branch]
    status: NotRequired[str]


@extend_schema(
    parameters=[DailyReportQuerySerializer],
    responses={200: DailyReportResponseSerializer(many=True)},
)
class DailyReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = DailyReportQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(DailyReportValidatedData, serializer.validated_data)

        date_from = validated_data["date_from"]
        date_to = validated_data["date_to"]

        rows_by_day = self._empty_rows_by_day(date_from=date_from, date_to=date_to)

        orders = Order.objects.filter(
            created_at__date__gte=date_from, created_at__date__lte=date_to
        )

        branch = validated_data.get("branch_id")
        report_status = validated_data.get("status")

        if isinstance(branch, Branch):
            orders = orders.filter(branch=branch)

        if report_status:
            orders = orders.filter(status=report_status)

        self._add_order_totals(rows_by_day=rows_by_day, orders=orders)
        self._add_status_totals(rows_by_day=rows_by_day, orders=orders)
        self._add_customer_totals(rows_by_day=rows_by_day, orders=orders)

        return Response(list(rows_by_day.values()), status=status.HTTP_200_OK)

    def _empty_rows_by_day(self, *, date_from, date_to):
        rows_by_day = {}
        current_date = date_from

        while current_date <= date_to:
            rows_by_day[current_date] = {
                "date": current_date.isoformat(),
                "total_orders": 0,
                "orders_by_status": {
                    status_value: 0 for status_value, _ in Order.OrderStatus.choices
                },
                "total_existing_customers_ordered": 0,
                "total_new_customers_ordered": 0,
                "total_revenue": "0.00",
            }
            current_date += timedelta(days=1)

        return rows_by_day

    def _add_order_totals(self, *, rows_by_day, orders):
        daily_totals = (
            orders.annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(total_orders=Count("id"), total_revenue=Sum("total_price"))
        )

        for daily_total in daily_totals:
            row = rows_by_day[daily_total["day"]]
            row["total_orders"] = daily_total["total_orders"]
            row["total_revenue"] = self._format_revenue(daily_total["total_revenue"])

    def _add_status_totals(self, *, rows_by_day, orders):
        daily_status_totals = (
            orders.annotate(day=TruncDate("created_at"))
            .values("day", "status")
            .annotate(total=Count("id"))
        )

        for status_total in daily_status_totals:
            rows_by_day[status_total["day"]]["orders_by_status"][
                status_total["status"]
            ] = status_total["total"]

    def _add_customer_totals(self, *, rows_by_day, orders):
        for day, row in rows_by_day.items():
            customer_ids = set(
                orders.filter(created_at__date=day)
                .values_list("customer_id", flat=True)
                .distinct()
            )

            existing_customer_ids = set(
                Order.objects.filter(
                    customer_id__in=customer_ids, created_at__date__lt=day
                )
                .values_list("customer_id", flat=True)
                .distinct()
            )

            row["total_existing_customers_ordered"] = len(existing_customer_ids)
            row["total_new_customers_ordered"] = len(
                customer_ids - existing_customer_ids
            )

    def _format_revenue(self, value):
        return str((value or Decimal("0.00")).quantize(Decimal("0.01")))
