from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('auth/login/',TokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/',TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/',views.Register.as_view(),name='register'),
    path('auth/forget-password/',views.ForgetPassword.as_view(),name='forget_password'),
    path('auth/reset-password/',views.ResetPassword.as_view(),name='reset_password'),
    path('user/profile/get/',views.GetProfile.as_view(),name='get_profile'),
    path('user/profile/update/',views.UpdateProfile.as_view(),name='update_profile'),
    path('user/change-password/',views.ChangePassword.as_view(),name='change_password'),

]