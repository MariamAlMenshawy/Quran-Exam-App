from django.contrib import admin
from .models import Session

# Register your models here.

class AddSession(admin.ModelAdmin):
    list_display = ['user','challenge_type','user_answer','correct_answer','is_correct','created_at']
    list_filter = ['challenge_type','created_at']
    search_fields = ['user__email']
    ordering = ['-created_at']

admin.site.register(Session,AddSession)
