"""
Custom User Model for IdP
مدل کاربر سفارشی برای سرویس هویت‌سنجی
"""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from account.manager import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User Model
    مدل کاربر سفارشی با امکانات اضافی
    """
    email = models.EmailField(
        'email address',
        unique=True,
        help_text='Required. Enter a valid email address.'
    )
    first_name = models.CharField(
        'first name',
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        'last name',
        max_length=150,
        blank=True
    )
    is_active = models.BooleanField(
        'active',
        default=True,
        help_text='Designates whether this user should be treated as active.'
    )
    is_staff = models.BooleanField(
        'staff status',
        default=False,
        help_text='Designates whether the user can log into this admin site.'
    )
    date_joined = models.DateTimeField(
        'date joined',
        default=timezone.now
    )
    last_login = models.DateTimeField(
        'last login',
        blank=True,
        null=True
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'users'

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        """Return the full name of the user"""
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        """Return the short name for the user"""
        return self.first_name