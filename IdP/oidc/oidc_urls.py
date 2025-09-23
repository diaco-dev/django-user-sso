## account/oidc_urls.py
from django.urls import path, include
from oauth2_provider import urls as oauth2_urls
from . import oidc_views

urlpatterns = [
    # OIDC endpoints for client applications
    path('authorize/', oidc_views.AuthorizationView.as_view(), name='authorize'),
    path('token/', oidc_views.TokenView.as_view(), name='token'),
    path('userinfo/', oidc_views.UserInfoView.as_view(), name='userinfo'),
    path('.well-known/openid-configuration/', oidc_views.OpenIDConfigurationView.as_view(),
         name='openid-configuration'),

    # OAuth2 provider URLs
    path('', include(oauth2_urls)),
]