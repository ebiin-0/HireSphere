from django.contrib import admin
from .models import Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'industry', 'location']
    list_filter = ['industry']
    search_fields = ['name', 'user__username']
