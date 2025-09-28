from django.urls import path,include
from core.views import oauth_callback, login_redirect
from django.contrib import admin
urlpatterns = [
     path('admin/', admin.site.urls),
    path("login/", login_redirect, name="login"),
    path("oauth/callback/", oauth_callback, name="oauth_callback"),
    path('api/v1/task/', include('task.urls')),
    path('api/v1/core/', include('core.urls')),
]

