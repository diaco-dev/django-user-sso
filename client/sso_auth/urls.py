from django.urls import path
from .views import LoginView, CallbackView, M2MTokenView

urlpatterns = [
    path('login/', LoginView.as_view(), name='sso-login'),
    path('callback/', CallbackView.as_view(), name='sso-callback'),
    path('m2m-token/', M2MTokenView.as_view(), name='m2m-token'),
]