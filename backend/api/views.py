from rest_framework import viewsets, permissions

from recipes.models import Recipe, Tag, Ingredient
from .serializers import TagSerializer, RecipeSerializer, IngredientSerializer
from .filters import IngredientSearchFilterBackend


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
