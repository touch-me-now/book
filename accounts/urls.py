from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.views import RegistrationView


urlpatterns = [
    path("register/", RegistrationView.as_view(), name="auth-register"),
    path('token/', TokenObtainPairView.as_view(), name='auth-token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='auth-token-refresh'),
]
