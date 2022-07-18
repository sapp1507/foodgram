from django.contrib import admin

from .models import Recipe, Tag, Ingredient, AmountIngredient


class RecipeIngredientsInLine(admin.TabularInline):
    model = AmountIngredient
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'slug']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'author']
    list_filter = ['author', 'name', 'tags']
    search_fields = ['author', 'name']
    inlines = [RecipeIngredientsInLine]
    readonly_fields = ['favorite_count']
    # filter_horizontal = ['tags']
    fields = ['author', 'name', 'image', 'text', 'cooking_time', 'tags',
              'favorite_count', 'favorite', 'shopping_carts']


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'measurement_unit']
    search_fields = ['name']
    list_filter = ['name']
