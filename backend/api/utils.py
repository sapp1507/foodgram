from rest_framework.response import Response


def clear_ingredients_in_recipe(recipe):
    """Удаляет у рецепта все ингредиенты с их количество при удалении
    рецепта или редактировании"""
    recipe.ingredients.all().delete()


def is_authenticated(context):
    """Проверка авторизован ли пользователь из контекста"""
    return context['request'].user.is_authenticated


def get_response_as_error(message, status_response):
    return Response(
        {'errors': message},
        status_response
    )
