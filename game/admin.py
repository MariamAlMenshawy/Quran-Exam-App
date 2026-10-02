from django.contrib import admin
from .models import Session, SessionQuestion

# Register your models here.


class QuestionInline(admin.TabularInline):
    model = SessionQuestion
    extra = 0

class AddSession(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ['user','challenge_type','user_answer','correct_answer','is_correct','created_at']
    list_filter = ['challenge_type','created_at']
    search_fields = ['user__email']
    ordering = ['-created_at']

admin.site.register(Session,AddSession)



class AddSessionQuestion(admin.ModelAdmin):
    list_display = ['session','ayah']
    list_filter = ['session']
    search_fields = ['session']

admin.site.register(SessionQuestion,AddSessionQuestion)



