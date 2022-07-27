from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from api.serializers import SmallRecipeSerializer
from api.utils import get_response_as_error
from recipes.models import Recipe


class ListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    pass


class CreateDeleteMixin:
    def custom_create(self, request, id_recipe, attribute):
        recipe = get_object_or_404(Recipe, pk=id_recipe)
        queryset = getattr(request.user, attribute)
        if not queryset.filter(id=recipe.id).exists():
            queryset.add(recipe)
            serializer = SmallRecipeSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status.HTTP_201_CREATED)
        return get_response_as_error(
            f'Рецепт "{recipe.name}" уже добавлен',
            status.HTTP_400_BAD_REQUEST
        )

    def custom_destroy(self, request, id_recipe, attribute):
        recipe = get_object_or_404(Recipe, pk=id_recipe)
        queryset = getattr(request.user, attribute)
        if queryset.filter(id=recipe.id).exists():
            queryset.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return get_response_as_error(
            f'Рецепта "{recipe.name}" нету в списке',
            status.HTTP_400_BAD_REQUEST
        )
