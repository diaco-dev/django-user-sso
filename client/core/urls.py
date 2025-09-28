from django.urls import path, include
from rest_framework.routers import DefaultRouter
from task import views
from core.test_views import test_api_dashboard, test_api_endpoint, test_session
from core.views import user_info_api,logout_view
router = DefaultRouter()
router.register('core', views.TaskViewSet, basename='core')


app_name = 'core'

urlpatterns = [
    path('', include(router.urls)),

    path('test-session/', test_session, name='test_session'),
    path('test-api/', test_api_dashboard, name='test_api_dashboard'),
    path('test-api-server/', test_api_endpoint, name='test_api_server'),
    path('logout/', logout_view, name='logout'),
    path('api/user-info/', user_info_api, name='user_info_api'),  # Add this
    ]