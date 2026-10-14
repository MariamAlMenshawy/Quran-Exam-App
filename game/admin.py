from django.contrib import admin
from .models import Session, SessionQuestion

# Register your models here.


class QuestionInline(admin.TabularInline):
    model = SessionQuestion
    extra = 0

class AddSession(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ['id','user','challenge_type','display_user_answer','display_correct_answer','is_correct','created_at']
    list_filter = ['id','user','challenge_type','created_at']
    search_fields = ['user__email']
    ordering = ['-created_at']
    @admin.display(description='Correct Answer')
    def display_correct_answer(self, obj):
        return obj.correct_answer.text

    @admin.display(description='User Answer')
    def display_user_answer(self, obj):
        return obj.user_answer.text if obj.user_answer else '-'

admin.site.register(Session,AddSession)



class AddSessionQuestion(admin.ModelAdmin):
    list_display = ['session','ayah']
    list_filter = ['session']
    search_fields = ['session']

admin.site.register(SessionQuestion,AddSessionQuestion)



