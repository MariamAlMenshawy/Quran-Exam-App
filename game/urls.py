from django.urls import path
from . import views

urlpatterns = [
    path('game/generate/',views.GenerateSession.as_view(),name='generate_session'),
    path('game/submit/',views.SumbitSession.as_view(), name='submit_session'),
    path('user/history/',views.UserSessionHistory.as_view(),name='user_history'),
]