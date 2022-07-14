from django.contrib.auth import get_user_model
from django.contrib import admin

from .models import Subscription

User = get_user_model()


class SubscriptionInLine(admin.TabularInline):
    model = Subscription
    extra = 1
    fk_name = 'user'
    fields = ['author']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display_links = ['username']
    list_display = ['id', 'username', 'email']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_filter = ['username', 'email']
    inlines = [SubscriptionInLine]
