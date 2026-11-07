from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', 'user_type', 'is_verified', 'date_joined']
    list_filter = ['user_type', 'is_verified', 'is_active']
    search_fields = ['username', 'email']
