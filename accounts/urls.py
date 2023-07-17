from django.urls import path

from . import views
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
     path('register/', views.RegisterView.as_view(), name='register'),
     path('verify-register-otp/', views.VerifyRegisterOTP.as_view(), name='verify-otp'),
     path('send-register-otp/', views.SendRegisterOTP.as_view(), name='send-verification-otp'),

     path('send-reset-password-otp/', views.SendResetPasswordOTP.as_view(), name='send-reset-password-otp'),
     path('verify-reset-password-otp/', views.VerifyResetPasswordOTP.as_view(), name='verify-reset-password-otp'),
     path('reset-password/', views.ResetPasswordView.as_view(), name='reset-password'),

     path('login/', 
          views.CustomTokenObtainPairView.as_view(), 
          name='token_create'),  # override sjwt stock token
     path('token/refresh/', 
          jwt_views.TokenRefreshView.as_view(), 
          name='token_refresh'),

     path('<str:username>/', views.AccountDetailView.as_view(), name='account'),
]