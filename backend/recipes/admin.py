from django.contrib import admin

from .models import Recipe, Tag, Ingridient, RecipeIngridient


class RecipeIngridientsInLine(admin.TabularInline):
    model = RecipeIngridient
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'slug']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'author']
    list_filter = ['author', 'name', 'tags']
    search_fields = ['author', 'name']
    inlines = [RecipeIngridientsInLine]
    readonly_fields = ['favorits_count']
    # filter_horizontal = ['tags']
    fields = ['author', 'name', 'image', 'text', 'coocking_time', 'tags',
              'favorits_count']


@admin.register(Ingridient)
class IngridientAdmin(admin.ModelAdmin):
    list_display = ['name', 'measurement_unit']
    search_fields = ['name']
    list_filter = ['name']
