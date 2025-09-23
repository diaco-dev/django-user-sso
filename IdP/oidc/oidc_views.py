from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from oauth2_provider.views import AuthorizationView as BaseAuthorizationView
from oauth2_provider.views import TokenView as BaseTokenView
from oauth2_provider.contrib.rest_framework import TokenHasScope

from account.serializers import UserSerializer


class AuthorizationView(BaseAuthorizationView):
    """
    OIDC Authorization endpoint
    نقطه پایانی مجوزدهی OIDC
    """
    pass


class TokenView(BaseTokenView):
    """
    OIDC Token endpoint
    نقطه پایانی توکن OIDC
    """
    pass


class UserInfoView(APIView):
    """
    OIDC UserInfo endpoint
    نقطه پایانی اطلاعات کاربر OIDC
    """
    permission_classes = [IsAuthenticated, TokenHasScope]
    required_scopes = ['openid']

    def get(self, request):
        user = request.user
        user_data = UserSerializer(user).data

        # OIDC standard claims
        oidc_claims = {
            'sub': str(user.id),
            'email': user.email,
            'email_verified': user.is_verified,
            'name': user.get_full_name(),
            'given_name': user.first_name,
            'family_name': user.last_name,
            'preferred_username': user.username,
            'picture': user.avatar,
            'updated_at': int(user.updated_at.timestamp()) if user.updated_at else None,
        }

        # Add additional claims based on scopes
        if 'profile' in request.auth.scope.split():
            if hasattr(user, 'profile'):
                oidc_claims.update({
                    'website': user.profile.website,
                    'locale': 'fa-IR',
                    'zoneinfo': 'Asia/Tehran',
                })

        return Response(oidc_claims)


class OpenIDConfigurationView(APIView):
    """
    OIDC Discovery document endpoint
    نقطه پایانی سند کشف OIDC
    """
    permission_classes = []

    def get(self, request):
        base_url = request.build_absolute_uri('/')[:-1]

        config = {
            "issuer": base_url,
            "authorization_endpoint": f"{base_url}{reverse('authorize')}",
            "token_endpoint": f"{base_url}{reverse('token')}",
            "userinfo_endpoint": f"{base_url}{reverse('userinfo')}",
            "jwks_uri": f"{base_url}/auth/jwks/",

            "response_types_supported": [
                "code",
                "id_token",
                "id_token token",
                "code id_token",
                "code token",
                "code id_token token"
            ],
            "subject_types_supported": ["public"],
            "id_token_signing_alg_values_supported": ["RS256"],
            "scopes_supported": ["openid", "profile", "email"],
            "token_endpoint_auth_methods_supported": [
                "client_secret_post",
                "client_secret_basic"
            ],
            "claims_supported": [
                "aud", "email", "email_verified", "exp", "family_name",
                "given_name", "iat", "iss", "locale", "name", "picture",
                "sub"
            ],
            "code_challenge_methods_supported": ["S256"],
        }

        return JsonResponse(config)