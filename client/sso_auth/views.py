"""
SSO Authentication Views
ویوهای احراز هویت SSO
"""
import requests
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


@api_view(['GET'])
@permission_classes([AllowAny])
def sso_login(request):
    """
    Redirect to IdP for authentication
    هدایت به IdP برای احراز هویت
    """
    sso_config = settings.SSO_SETTINGS

    auth_url = (
        f"{sso_config['IDP_BASE_URL']}/o/authorize/"
        f"?response_type=code"
        f"&client_id={sso_config['CLIENT_ID']}"
        f"&redirect_uri={sso_config['REDIRECT_URI']}"
        f"&scope={' '.join(sso_config['SCOPES'])}"
    )

    return Response({
        'auth_url': auth_url,
        'message': 'Redirect to this URL for SSO login'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def sso_callback(request):
    """
    Handle callback from IdP
    پردازش callback از IdP
    """
    code = request.GET.get('code')
    error = request.GET.get('error')

    if error:
        return Response({
            'error': f'SSO authentication failed: {error}'
        }, status=status.HTTP_400_BAD_REQUEST)

    if not code:
        return Response({
            'error': 'Authorization code not provided'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Exchange code for access token
        token_data = _exchange_code_for_token(code)
        if not token_data:
            return Response({
                'error': 'Failed to get access token'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get user info from IdP
        user_info = _get_user_info(token_data['access_token'])
        if not user_info:
            return Response({
                'error': 'Failed to get user information'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create or get local user
        from .authentication import SSOAuthentication
        sso_auth = SSOAuthentication()
        user = sso_auth._get_or_create_user(user_info)

        # Generate JWT tokens for internal APIs
        refresh = RefreshToken.for_user(user)

        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'sso_token': token_data['access_token']
        })

    except Exception as e:
        return Response({
            'error': f'SSO callback processing failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _exchange_code_for_token(code):
    """
    Exchange authorization code for access token
    تبدیل کد مجوز به توکن دسترسی
    """
    sso_config = settings.SSO_SETTINGS

    try:
        response = requests.post(
            f"{sso_config['IDP_BASE_URL']}/o/token/",
            data={
                'grant_type': 'authorization_code',
                'client_id': sso_config['CLIENT_ID'],
                'client_secret': sso_config['CLIENT_SECRET'],
                'redirect_uri': sso_config['REDIRECT_URI'],
                'code': code,
            },
            timeout=10
        )

        if response.status_code == 200:
            return response.json()
        return None

    except requests.RequestException:
        return None


def _get_user_info(access_token):
    """
    Get user information from IdP
    دریافت اطلاعات کاربر از IdP
    """
    sso_config = settings.SSO_SETTINGS

    try:
        response = requests.get(
            f"{sso_config['IDP_BASE_URL']}/api/auth/me/",
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10
        )

        if response.status_code == 200:
            return response.json()
        return None

    except requests.RequestException:
        return None