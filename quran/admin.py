from django.contrib import admin
from .models import Surah, Ayah


class AyahInline(admin.TabularInline):
    model = Ayah
    extra = 0


class AddSurah(admin.ModelAdmin):
    inlines = [AyahInline]
    list_display = ['surah_number','name']
    search_fields = ['name']
    ordering = ['surah_number']

admin.site.register(Surah,AddSurah)


class AddAyah(admin.ModelAdmin):
    list_display = ['surah__name','numberInSurah','juz','text']
    list_filter = ['surah__name','juz']
    search_fields = ['text']
    ordering = ['surah','numberInSurah']
    
admin.site.register(Ayah,AddAyah)

