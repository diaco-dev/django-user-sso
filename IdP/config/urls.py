
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import path,include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('oidc/', include('oidc_provider.urls', namespace='oidc_provider')),
    path('api/v1/account/', include('account.urls')),
    path('accounts/', include('django.contrib.auth.urls')),  # مسیرهای ورود پیش‌فرض
]
