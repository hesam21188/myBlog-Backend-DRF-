from django.urls import path

from .views import *

urlpatterns = [
    path('', GetUsername.as_view(), name='get_username'),
    path('register/', RegistrationView.as_view(), name='register'),
    path('active/', ActivationView.as_view(), name='activate'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('resend_email/', ResndEmailView.as_view(), name='resend_email'),
    path('change_password/', ChangePassword.as_view(), name='change_password'),
]
