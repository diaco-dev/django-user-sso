from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from core.models import CustomUser
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)

class CustomOIDCAuthenticationBackend(OIDCAuthenticationBackend):
  def create_user(self, claims):
      logger.debug(f"Creating user with claims: {claims}")
      email = claims.get('email')
      username = claims.get('preferred_username')
      phone_number = claims.get('phone_number', '')

      if not email or not username:
          logger.error("Missing email or username in claims")
          raise ValueError("Email and username are required")

      try:
          user = self.UserModel.objects.get(email=email)
          logger.debug(f"User {email} already exists")
      except ObjectDoesNotExist:
          user = self.UserModel.objects.create_user(
              email=email,
              username=username,
              phone_number=phone_number
          )
          logger.debug(f"Created new user: {email}")
      return user

  def update_user(self, user, claims):
      logger.debug(f"Updating user {user.email} with claims: {claims}")
      user.email = claims.get('email')
      user.username = claims.get('preferred_username')
      user.phone_number = claims.get('phone_number', '')
      user.save()
      return user