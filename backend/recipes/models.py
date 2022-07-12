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
        related_name='recipies',
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
    )
    image = models.ImageField(
        'Фото',
        upload_to='recipies/',
        blank=True,
    )
    text = models.TextField(verbose_name='Описание')
    coocking_time = models.IntegerField(verbose_name='Время готовки')
    tags = models.ManyToManyField(Tag, verbose_name='Тэг')
    favorits = models.ManyToManyField(
        User, related_name='favorits', blank=True)
    shopping_carts = models.ManyToManyField(
        User, related_name='shopping_cart', blank=True)

    def favorits_count(self):
        return self.favorits.count()
    favorits_count.short_description = 'Добавили в избранное'

    def __str__(self):
        return self.name


class Ingridient(models.Model):
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


class RecipeIngridient(models.Model):
    """Рецепты и ингридиенты, многие ко многим"""
    recipe = models.ForeignKey(
        Recipe,
        related_name='ingridients',
        on_delete=models.CASCADE,
    )
    ingridient = models.ForeignKey(
        Ingridient,
        related_name='recipies',
        on_delete=models.CASCADE,
    )
    amount = models.IntegerField()
