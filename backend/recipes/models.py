from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import validate_slug

User = get_user_model()


class Tag(models.Model):
    """Тэги"""
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        unique=True,
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет',
        unique=True,
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        validators=[validate_slug],
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Рецепты"""
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
    )
    image = models.ImageField(
        'Фото',
        upload_to='recipes/',
        blank=True,
    )
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.IntegerField(verbose_name='Время готовки')
    tags = models.ManyToManyField(Tag, verbose_name='Тэг')
    favorite = models.ManyToManyField(
        User, related_name='favorite', blank=True)
    shopping_carts = models.ManyToManyField(
        User, related_name='shopping_cart', blank=True)

    def favorite_count(self):
        return self.favorite.count()
    favorite_count.short_description = 'Добавили в избранное'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингридиенты и их единица измерения"""
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Ед. изм.'
    )

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class RecipeIngredient(models.Model):
    """Рецепты и ингредиенты, многие ко многим"""
    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredients',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='recipes',
        on_delete=models.CASCADE,
    )
    amount = models.IntegerField()
