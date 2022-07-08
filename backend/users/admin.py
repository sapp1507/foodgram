
from django.contrib import admin  # type: ignore

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email']
    search_fields = ['username', 'email', 'first_name', 'last_name']
