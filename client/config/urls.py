
from django.contrib import admin
from django.urls import path,include

from core.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('oidc/', include('mozilla_django_oidc.urls')),
    path('api/v1/core/', include('core.urls')),
    path('', home, name='root'),  # مسیر root را به ویوی home هدایت کنید

]
