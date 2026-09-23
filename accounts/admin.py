from django.contrib import admin
from .models import User

# Register your models here.

class AddUser(admin.ModelAdmin):
    list_display = ['email','full_name','total_points','is_active','is_staff']
    list_filter = ['is_active','is_staff']
    search_fields = ['email','full_name']
    ordering = ['-total_points']

admin.site.register(User,AddUser)
