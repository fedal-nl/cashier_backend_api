from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .serializers import (
    OrderInputSerializer, 
    CustomerInputSerializer, 
    CustomerOutputSerializer, 
    OrderOutputSerializer,
    OrderStatusUpdateSerializer
)
from .models import Customer, Order
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
            order = serializer.save()
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


@extend_schema(responses={200: CustomerOutputSerializer(many=True)})
class CustomerListView(APIView):
    def get(self, request):
        customers = Customer.objects.all()
        serializer = CustomerOutputSerializer(customers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(responses={200: OrderOutputSerializer(many=True)})
class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Order.objects.select_related(
            "customer"
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
                Q(id__icontains=search)
            )

        serializer = OrderOutputSerializer(
            queryset,
            many=True
        )

        return Response(serializer.data)  
  
  
@extend_schema(responses={200: OrderOutputSerializer})    
class OrderDetailView(RetrieveAPIView):
    queryset = Order.objects.all()
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
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        order.status = serializer.validated_data[
            "status"
        ]

        order.save()

        return Response({
            "message": "Status updated",
            "status": order.status
        })