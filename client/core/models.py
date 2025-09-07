from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
   def create_user(self, email, username, password=None, **extra_fields):
       if not email:
           raise ValueError(_('The Email field must be set'))
       email = self.normalize_email(email)
       user = self.model(email=email, username=username, **extra_fields)
       user.set_password(password)
       user.save(using=self._db)
       return user

   def create_superuser(self, email, username, password=None, **extra_fields):
       extra_fields.setdefault('is_staff', True)
       extra_fields.setdefault('is_superuser', True)

       if extra_fields.get('is_staff') is not True:
           raise ValueError(_('Superuser must have is_staff=True.'))
       if extra_fields.get('is_superuser') is not True:
           raise ValueError(_('Superuser must have is_superuser=True.'))

       return self.create_user(email, username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
   email = models.EmailField(_('email address'), unique=True)
   username = models.CharField(_('username'), max_length=150, unique=True)
   phone_number = models.CharField(_('phone number'), max_length=15, blank=True)
   is_active = models.BooleanField(_('active'), default=True)
   is_staff = models.BooleanField(_('staff status'), default=False)

   objects = CustomUserManager()

   USERNAME_FIELD = 'email'
   REQUIRED_FIELDS = ['username']

   class Meta:
       verbose_name = _('user')
       verbose_name_plural = _('users')

   def __str__(self):
       return self.email

class Product(models.Model):
   user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='products')
   name = models.CharField(max_length=100)
   description = models.TextField(blank=True)
   price = models.DecimalField(max_digits=10, decimal_places=2)
   created_at = models.DateTimeField(auto_now_add=True)

   def __str__(self):
       return self.name