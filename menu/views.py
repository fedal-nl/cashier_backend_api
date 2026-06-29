from typing import cast

from rest_framework.generics import ListAPIView
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Branch, Category, Unit, Ingredient, MenuItemIngredient
from .serializers import (
    BranchSerializer,
    CategorySerializer,
    UnitSerializer,
    IngredientSerializer,
    MenuItemIngredientSerializer,
)


class BranchListView(ListAPIView):
    queryset = Branch.objects.filter(is_active=True)
    serializer_class = BranchSerializer


class MenuListView(ListAPIView):
    queryset = Category.objects.prefetch_related(
        "items__branches",
        "items__ingredients__ingredient",
        "items__ingredients__ingredient__unit",
    ).filter(is_active=True)
    serializer_class = CategorySerializer

    def list(self, request, *args, **kwargs):
        branch_id = request.query_params.get("branch_id")

        if (
            branch_id
            and not Branch.objects.filter(id=branch_id, is_active=True).exists()
        ):
            return Response(
                {"branch_id": "Invalid branch_id"}, status=status.HTTP_400_BAD_REQUEST
            )

        return super().list(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        request = cast(Request, self.request)
        context["branch_id"] = request.query_params.get("branch_id")

        return context


class CategoryListView(ListAPIView):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer


class UnitListView(ListAPIView):
    queryset = Unit.objects.filter(is_active=True)
    serializer_class = UnitSerializer


class IngredientListView(ListAPIView):
    queryset = Ingredient.objects.filter(is_active=True)
    serializer_class = IngredientSerializer


class MenuItemIngredientListView(ListAPIView):
    queryset = MenuItemIngredient.objects.filter(menu_item__is_active=True)
    serializer_class = MenuItemIngredientSerializer
