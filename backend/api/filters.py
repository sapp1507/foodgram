from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import filters

from recipes.models import User


class IngredientSearchFilterBackend(filters.SearchFilter):
    search_param = 'name'


class RecipeFilterBackend(DjangoFilterBackend):
    def filter_queryset(self, request, queryset, view):
        params = request.query_params

        is_favorited = params.get('is_favorited')
        is_in_shopping_cart = params.get('is_in_shopping_cart')
        author_id = params.get('author')
        tags = params.getlist('tags')

        if is_favorited is not None and is_favorited == '1':
            queryset = queryset.filter(favorite=request.user)

        if is_in_shopping_cart is not None and is_in_shopping_cart == '1':
            queryset = queryset.filter(shopping_carts__id=request.user.id)

        if author_id is not None and User.objects.filter(
                pk=author_id).exists():
            queryset = queryset.filter(author_id=author_id)

        if tags:
            regular_tags = '|'.join(tags)
            queryset = queryset.filter(tags__slug__regex=regular_tags)

        return queryset.distinct()
