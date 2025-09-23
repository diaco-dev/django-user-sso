from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from .views import login_view, UserRegistrationView, user_profile_view, update_profile_view, logout_view

urlpatterns = [
    # Authentication endpoints
    path('login/', login_view, name='account_login'),
    path('register/', UserRegistrationView.as_view(), name='account_register'),
    path('profile/', user_profile_view, name='account_profile'),
    path('update/', update_profile_view, name='account_update'),
    path('logout/', logout_view, name='account_logout'),
]