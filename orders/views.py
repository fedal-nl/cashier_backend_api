from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from django.utils.dateparse import parse_date
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .serializers import (
    OrderInputSerializer, 
    CustomerInputSerializer, 
    CustomerOutputSerializer, 
    CustomerUpdateSerializer,
    DeliveryCompanyOutputSerializer,
    OrderOutputSerializer,
    OrderStatusUpdateSerializer,
    OrderLogOutputSerializer,
    PaginatedCustomerOutputSerializer,
    PaginatedOrderOutputSerializer
)
from .models import Customer, DeliveryCompany, Order, OrderLog
from .pagination import StandardResultsSetPagination
from .services import update_order_status
from rest_framework.generics import (
    RetrieveAPIView,
    UpdateAPIView
)
from rest_framework.permissions import IsAuthenticated

@extend_schema(request=OrderInputSerializer, responses={201: OrderOutputSerializer})
class OrderCreateView(APIView):

    def post(self, request):
        serializer = OrderInputSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save(user=request.user)
            return Response({"message": "Order created successfully", "order_id": order.pk}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=CustomerInputSerializer, responses={201: CustomerOutputSerializer})
class CustomerCreateView(APIView):

    def post(self, request):
        serializer = CustomerInputSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            return Response({"message": "Customer created successfully", "customer_id": customer.pk}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


PAGINATION_PARAMETERS = [
    OpenApiParameter(
        name="page",
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        description="Page number to return. Use this instead of fetching every row.",
    ),
    OpenApiParameter(
        name="page_size",
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        default=2,
        description="Number of rows per page. Defaults to 2 and is capped at 100.",
    ),
]


@extend_schema(
    parameters=PAGINATION_PARAMETERS,
    responses={200: PaginatedCustomerOutputSerializer},
)
class CustomerListView(APIView):
    def get(self, request):
        customers = Customer.objects.all()
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(customers, request, view=self)

        # Return DRF's paginated shape so the UI gets count/next/previous
        # metadata without loading the full customer table at once.
        serializer = CustomerOutputSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


@extend_schema(request=CustomerUpdateSerializer, responses={200: CustomerOutputSerializer})
class CustomerUpdateView(UpdateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerUpdateSerializer

    def patch(self, request, *args, **kwargs):
        customer = self.get_object()

        serializer = self.get_serializer(
            customer,
            data=request.data,
            partial=True
        )

        serializer.is_valid(
            raise_exception=True
        )

        customer = serializer.save()

        return Response(
            CustomerOutputSerializer(customer).data,
            status=status.HTTP_200_OK
        )


@extend_schema(responses={200: DeliveryCompanyOutputSerializer(many=True)})
class DeliveryCompanyListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        delivery_companies = DeliveryCompany.objects.all()
        serializer = DeliveryCompanyOutputSerializer(
            delivery_companies,
            many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(responses={200: OrderOutputSerializer(many=False)})
class CustomerSearchView(APIView):
    def get(self, request):
        phone = request.query_params.get("phone")

        if not phone:
            return Response(
                {"error": "Phone required"},
                status=400
            )

        customer = Customer.objects.filter(
            phone_number=phone
        ).first()

        if not customer:
            return Response(
                {"exists": False}
            )

        serializer = CustomerOutputSerializer(
            customer
        )

        return Response({
            "exists": True,
            "customer": serializer.data
        })

@extend_schema(
    parameters=[
        *PAGINATION_PARAMETERS,
        OpenApiParameter(
            name="status",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter orders by status, for example created or completed.",
        ),
        OpenApiParameter(
            name="customer",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter orders by customer name.",
        ),
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Search orders by id or customer name.",
        ),
    ],
    responses={200: PaginatedOrderOutputSerializer},
)
class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Order.objects.select_related(
            "customer",
            "branch",
            "delivery_company"
        ).prefetch_related(
            "items__modifications"
        )

        status_filter = request.query_params.get(
            "status"
        )

        customer_filter = request.query_params.get(
            "customer"
        )

        search = request.query_params.get(
            "search"
        )

        if status_filter:
            queryset = queryset.filter(
                status=status_filter
            )

        if customer_filter:
            queryset = queryset.filter(
                customer__name__icontains=customer_filter
            )

        if search:
            queryset = queryset.filter(
                Q(id__icontains=search) |
                Q(customer__name__icontains=search)
            )

        queryset = queryset.order_by(
            "-created_at"
        )

        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)

        # Serialize only the requested page to keep large order histories from
        # loading all nested order items and modifications in one response.
        serializer = OrderOutputSerializer(
            page,
            many=True
        )

        return paginator.get_paginated_response(serializer.data)  
  
  
@extend_schema(responses={200: OrderOutputSerializer})    
class OrderDetailView(RetrieveAPIView):
    queryset = Order.objects.select_related(
        "customer",
        "branch",
        "delivery_company"
    ).prefetch_related(
        "items__modifications"
    )
    serializer_class = OrderOutputSerializer
    permission_classes = [IsAuthenticated]


@extend_schema(request=OrderStatusUpdateSerializer, responses={200: OrderOutputSerializer})
class OrderStatusUpdateView(UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        order = self.get_object()

        serializer = self.get_serializer(
            data=request.data,
            context={
                "order": order
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        order = update_order_status(
            order=order,
            status=serializer.validated_data["status"],
            delivery_company=serializer.validated_data.get("delivery_company_id"),
            user=request.user
        )

        return Response({
            "message": "Status updated",
            "status": order.status,
            "delivery_company": DeliveryCompanyOutputSerializer(
                order.delivery_company
            ).data if order.delivery_company else None
        })


@extend_schema(responses={200: OrderLogOutputSerializer(many=True)})
class OrderLogListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = OrderLog.objects.select_related(
            "order",
            "customer",
            "created_by"
        )

        date_filter = request.query_params.get("date")
        customer_filter = request.query_params.get("customer")
        status_filter = request.query_params.get("status")

        if date_filter:
            parsed_date = parse_date(date_filter)
            if parsed_date is None:
                return Response(
                    {"date": "Use YYYY-MM-DD format."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            queryset = queryset.filter(
                created_at__date=parsed_date
            )

        if customer_filter:
            if customer_filter.isdigit():
                queryset = queryset.filter(
                    customer_id=customer_filter
                )
            else:
                queryset = queryset.filter(
                    customer__name__icontains=customer_filter
                )

        if status_filter:
            queryset = queryset.filter(
                new_status=status_filter
            )

        serializer = OrderLogOutputSerializer(
            queryset,
            many=True
        )

        return Response(serializer.data)
