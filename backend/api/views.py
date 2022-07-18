from rest_framework import viewsets, permissions

from recipes.models import Recipe, Tag, Ingredient
from .serializers import (TagSerializer, RecipeSerializer,
                          IngredientSerializer, AddRecipeSerializer)
from .filters import IngredientSearchFilterBackend
from .paginators import PageLimitPaginator


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    # permission_classes = [permissions.AllowAny]
    filter_backends = [IngredientSearchFilterBackend]
    search_fields = ['^name']
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    # serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = PageLimitPaginator

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return AddRecipeSerializer
