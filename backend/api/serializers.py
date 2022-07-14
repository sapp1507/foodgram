from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from djoser.serializers import UserCreateSerializer

from recipes.models import Tag, Ingredient

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['name', 'measurement_unit']


class RecipeSerializer(serializers.ModelSerializer):
    pass


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed']

    def get_is_subscribed(self, obj):
        if self.context['request'].user.is_authenticated:
            return obj.following.filter(user=self.context[
                'request'].user).exists()
        return False


class UserCustomCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password']

    def validate(self, attrs):
        user = User(**attrs)
        password = attrs.get('password')

        if user.username == 'me':
            raise serializers.ValidationError('username <me> не доступен')

        try:
            validate_password(password, user)
        except django_exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {'password': serializer_error['non_field_errors']}
            )
        return attrs
