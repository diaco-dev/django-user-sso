from django.contrib.auth.views import LoginView
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from account.views import RegisterView, CustomTokenObtainPairView, CustomTokenRefreshView, login

router = DefaultRouter()
app_name = 'accounts'

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('login/', login, name='home'),
]