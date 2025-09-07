from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from core.models import CustomUser
from django.core.exceptions import ObjectDoesNotExist

class CustomOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    def create_user(self, claims):
        email = claims.get('email')
        username = claims.get('preferred_username')
        phone_number = claims.get('phone_number', '')

        # Check if user already exists
        try:
            user = self.UserModel.objects.get(email=email)
        except ObjectDoesNotExist:
            user = self.UserModel.objects.create_user(
                email=email,
                username=username,
                phone_number=phone_number
            )
        return user

    def update_user(self, user, claims):
        user.email = claims.get('email')
        user.username = claims.get('preferred_username')
        user.phone_number = claims.get('phone_number', '')
        user.save()
        return user