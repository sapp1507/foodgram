# Generated by Django 4.0.6 on 2022-07-14 12:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='RecipeIngredient',
            new_name='AmountIngredient',
        ),
    ]
