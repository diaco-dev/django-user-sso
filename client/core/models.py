"""
Core Models for Client App
مدل‌های اصلی برای اپلیکیشن کلاینت
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    """
    Extended user profile for SSO users
    پروفایل توسعه یافته برای کاربران SSO
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    sso_user_id = models.CharField(
        'SSO User ID',
        max_length=255,
        unique=True,
        null=True,
        blank=True
    )
    phone = models.CharField(
        'Phone Number',
        max_length=15,
        blank=True
    )
    avatar = models.URLField(
        'Avatar URL',
        blank=True
    )
    bio = models.TextField(
        'Biography',
        blank=True
    )
    created_at = models.DateTimeField(
        'Created At',
        default=timezone.now
    )
    updated_at = models.DateTimeField(
        'Updated At',
        auto_now=True
    )

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        db_table = 'user_profiles'

    def __str__(self):
        return f"{self.user.username} Profile"


class Task(models.Model):
    """
    Sample model for testing M2M functionality
    مدل نمونه برای تست عملکرد M2M
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(
        'Title',
        max_length=200
    )
    description = models.TextField(
        'Description',
        blank=True
    )
    status = models.CharField(
        'Status',
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_tasks'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tasks'
    )
    created_at = models.DateTimeField(
        'Created At',
        default=timezone.now
    )
    updated_at = models.DateTimeField(
        'Updated At',
        auto_now=True
    )
    due_date = models.DateTimeField(
        'Due Date',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        db_table = 'tasks'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Category(models.Model):
    """
    Category model for organizing tasks
    مدل دسته‌بندی برای سازماندهی وظایف
    """
    name = models.CharField(
        'Name',
        max_length=100,
        unique=True
    )
    description = models.TextField(
        'Description',
        blank=True
    )
    tasks = models.ManyToManyField(
        Task,
        blank=True,
        related_name='categories'
    )
    created_at = models.DateTimeField(
        'Created At',
        default=timezone.now
    )

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        db_table = 'categories'

    def __str__(self):
        return self.name