from django_filters import FilterSet, ModelMultipleChoiceFilter
from recipes.models import Tag
from rest_framework import filters


class IngredientSearchFilterBackend(filters.SearchFilter):
    search_param = 'name'


class RecipeFilterSet(FilterSet):
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        label='tags',
        queryset=Tag.objects.all()
    )
