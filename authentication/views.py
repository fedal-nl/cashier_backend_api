from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    LoginInputSerializer,
    AuthResponseSerializer,
    MeResponseSerializer,
)
from drf_spectacular.utils import extend_schema


@extend_schema(exclude=True)
def csrf(request):
    return JsonResponse({"csrfToken": get_token(request)})


@extend_schema(request=LoginInputSerializer, responses={200: AuthResponseSerializer})
class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return Response({"message": "Logged in"})

        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )


@extend_schema(request=None, responses={200: AuthResponseSerializer})
class LogoutView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        logout(request)
        return Response({"message": "Logged out"})


@extend_schema(responses={200: MeResponseSerializer})
class MeView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            return Response({"authenticated": True, "username": request.user.username})

        return Response({"authenticated": False})
