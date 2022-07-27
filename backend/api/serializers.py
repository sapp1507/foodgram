from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import AmountIngredient, Ingredient, Recipe, Tag
from users.models import User

from .utils import clear_ingredients_in_recipe, is_authenticated


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class AmountIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')

    class Meta:
        model = AmountIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']


class AddAmountIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')

    class Meta:
        model = AmountIngredient
        fields = ['id', 'amount']


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed']

    def get_is_subscribed(self, obj):
        if is_authenticated(self.context):
            return obj.following.filter(
                user=self.context['request'].user).exists()
        return False


class UserCustomCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password']

    def validate(self, attrs):
        user = User(**attrs)
        password = attrs.get('password')

        if user.username.lower() == 'me':
            raise serializers.ValidationError('username \"me\" не доступен')

        try:
            validate_password(password, user)
        except django_exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {'password': serializer_error['non_field_errors']}
            )
        return attrs


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(source='get_tags', read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = AmountIngredientsSerializer(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name', 'image',
                  'text', 'cooking_time']

    def get_is_favorited(self, obj):
        if is_authenticated(self.context):
            return obj.favorite.filter(
                id=self.context['request'].user.id
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        if is_authenticated(self.context):
            return obj.shopping_carts.filter(
                id=self.context['request'].user.id
            ).exists()
        return False


class AddRecipeSerializer(RecipeSerializer):
    ingredients = AddAmountIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'ingredients', 'name', 'image', 'text',
                  'cooking_time']

    def validate(self, attrs):
        request = self.context['request']
        if request.method != 'POST':
            return attrs

        for ingredient in request.data['ingredients']:
            count = 0
            for find_ingredient in request.data['ingredients']:
                if ingredient['id'] == find_ingredient['id']:
                    count += 1
                if count > 1:
                    raise serializers.ValidationError(
                        {'ingredients': 'Есть повторяющиеся ингредиенты'})

            if not Ingredient.objects.filter(id=ingredient['id']).exists():
                raise serializers.ValidationError(
                    {'ingredients': f'Недопустимый первичный ключ '
                                    f'{ingredient["id"]} - объект не '
                                    f'существует'})
        return attrs

    def _take_validate_data(self, data):
        tags = data.pop('tags')
        ingredients = data.pop('ingredients')
        return tags, ingredients

    def _create_amount_for_recipe(self, ingredients, recipe):
        for ingredient in ingredients:
            add_ingredient = get_object_or_404(
                Ingredient, pk=ingredient['ingredient']['id'])
            amount, created = AmountIngredient.objects.get_or_create(
                recipe=recipe,
                ingredient=add_ingredient,
                amount=ingredient['amount']
            )
            if created:
                amount.save()

    def create(self, validated_data):
        author = self.context['request'].user
        tags, ingredients = self._take_validate_data(validated_data)
        recipe = Recipe.objects.create(
            author=author,
            **validated_data
        )
        recipe.tags.set(tags)

        self._create_amount_for_recipe(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        clear_ingredients_in_recipe(instance)
        tags, ingredients = self._take_validate_data(validated_data)
        super().update(instance, validated_data)
        self._create_amount_for_recipe(ingredients, instance)
        instance.tags.set(tags)
        return instance

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance, context=self.context)
        return serializer.data


class SmallRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class UserRecipeSerializer(UserSerializer):
    recipes = SmallRecipeSerializer(read_only=True, many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count']

    def get_recipes_count(self, author):
        return author.recipes.count()
