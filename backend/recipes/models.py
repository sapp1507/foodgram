from django.core.validators import validate_slug
from django.db import models

from users.models import User


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

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

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

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


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
        upload_to='recipes/images/'
    )
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveIntegerField(verbose_name='Время готовки')
    tags = models.ManyToManyField(Tag, verbose_name='Тэг')
    favorite = models.ManyToManyField(
        User, related_name='favorite', blank=True)
    shopping_carts = models.ManyToManyField(
        User, related_name='shopping_cart', blank=True)
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name

    def favorite_count(self):
        return self.favorite.count()
    favorite_count.short_description = 'Добавили в избранное'

    def get_tags(self):
        return self.tags.all()

    def get_ingredients(self):
        return self.ingredients.all()


class AmountIngredient(models.Model):
    """Рецепты и ингредиенты, многие ко многим"""
    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredients',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='ingredient_count',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_amount_ingredients',
                fields=['recipe', 'ingredient']
            )
        ]
