from django.contrib import admin
from .models import Surah, Ayah


class AyahInline(admin.TabularInline):
    model = Ayah
    extra = 0


class AddSurah(admin.ModelAdmin):
    inlines = [AyahInline]


class AddAyah(admin.ModelAdmin):
    pass

admin.site.register(Surah,AddSurah)
admin.site.register(Ayah,AddAyah)

