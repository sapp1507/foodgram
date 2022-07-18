def clear_ingredients_in_recipe(recipe):
    ingredients = recipe.ingredients.all()
    for ingredient in ingredients:
        ingredient.delete()
