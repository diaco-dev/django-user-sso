"""
Custom User Manager for IdP
مدیر کاربر سفارشی برای ایجاد کاربران
"""
from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


class UserManager(BaseUserManager):
    """
    Custom User Manager
    مدیر سفارشی برای مدیریت کاربران
    """

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password
        ایجاد و ذخیره کاربر با ایمیل و رمز عبور داده شده
        """
        if not email:
            raise ValueError('The Email field must be set')

        try:
            validate_email(email)
        except ValidationError:
            raise ValueError('Invalid email address')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user
        ایجاد کاربر عادی
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser
        ایجاد کاربر ادمین
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)