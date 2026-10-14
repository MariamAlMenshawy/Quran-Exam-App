from django.urls import path
from . import views

urlpatterns = [
    path('quran/surahs/',views.GetSurahs.as_view(),name='get_surahs'),
]