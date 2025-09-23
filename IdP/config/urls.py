from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/account/', include('account.urls')),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('auth/', include('oidc.oidc_urls')),
]
