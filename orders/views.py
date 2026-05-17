from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import OrderInputSerializer, CustomerInputSerializer, CustomerOutputSerializer, OrderOutputSerializer
from .models import Customer

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
