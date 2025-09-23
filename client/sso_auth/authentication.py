"""
SSO Authentication for Client
احراز هویت SSO برای کلاینت
"""
import requests
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from core.models import UserProfile


class SSOAuthentication(BaseAuthentication):
    """
    SSO Authentication class
    کلاس احراز هویت SSO برای ارتباط با IdP
    """

    def authenticate(self, request):
        """
        Authenticate user via SSO token
        احراز هویت کاربر از طریق توکن SSO
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION')

        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]

        try:
            # Validate token with IdP
            user_data = self._validate_token_with_idp(token)
            if not user_data:
                return None

            # Get or create user
            user = self._get_or_create_user(user_data)
            return (user, token)

        except Exception as e:
            raise AuthenticationFailed(f'SSO authentication failed: {str(e)}')

    def _validate_token_with_idp(self, token):
        """
        Validate token with Identity Provider
        اعتبارسنجی توکن با سرویس هویت‌سنجی
        """
        try:
            idp_url = settings.SSO_SETTINGS['IDP_BASE_URL']
            response = requests.get(
                f"{idp_url}/api/auth/me/",
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            return None

        except requests.RequestException:
            return None

    def _get_or_create_user(self, user_data):
        """
        Get or create user from SSO data
        دریافت یا ایجاد کاربر از داده‌های SSO
        """
        email = user_data.get('email')
        sso_user_id = str(user_data.get('id'))

        # Try to find existing user by SSO ID
        try:
            profile = UserProfile.objects.get(sso_user_id=sso_user_id)
            return profile.user
        except UserProfile.DoesNotExist:
            pass

        # Try to find by email
        try:
            user = User.objects.get(email=email)
            # Update profile with SSO ID
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.sso_user_id = sso_user_id
            profile.save()
            return user
        except User.DoesNotExist:
            pass

        # Create new user
        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', ''),
            is_active=user_data.get('is_active', True)
        )

        # Create profile
        UserProfile.objects.create(
            user=user,
            sso_user_id=sso_user_id
        )

        return user