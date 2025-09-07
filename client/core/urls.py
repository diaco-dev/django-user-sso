from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib import admin
from django.urls import path, include
from .views import ProtectedAPIView, home
router = DefaultRouter()
app_name = 'core'

urlpatterns = [
    path('', include(router.urls)),
    path('protected/', ProtectedAPIView.as_view(), name='protected_api'),
    path('home/', home, name='home'),

]