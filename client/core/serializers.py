"""
Serializers for Client Core App
سریالایزرهای اپ اصلی کلاینت
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Task, Category, UserProfile


class UserSerializer(serializers.ModelSerializer):
    """
    User Serializer
    سریالایزر کاربر
    """
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name',
            'last_name', 'full_name', 'is_active', 'date_joined'
        ]
        read_only_fields = ['id', 'username', 'date_joined']

    def get_full_name(self, obj):
        """Get user's full name"""
        return f"{obj.first_name} {obj.last_name}".strip()


class UserProfileSerializer(serializers.ModelSerializer):
    """
    User Profile Serializer
    سریالایزر پروفایل کاربر
    """
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'sso_user_id', 'phone',
            'avatar', 'bio', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'sso_user_id', 'created_at', 'updated_at']


class TaskSerializer(serializers.ModelSerializer):
    """
    Task Serializer
    سریالایزر وظایف
    """
    assigned_to = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    categories = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status',
            'assigned_to', 'created_by', 'categories',
            'created_at', 'updated_at', 'due_date'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_due_date(self, value):
        """Validate due date is in future"""
        from django.utils import timezone
        if value and value < timezone.now():
            raise serializers.ValidationError(
                "Due date cannot be in the past"
            )
        return value


class CategorySerializer(serializers.ModelSerializer):
    """
    Category Serializer with M2M tasks
    سریالایزر دسته‌بندی با وظایف M2M
    """
    tasks = TaskSerializer(many=True, read_only=True)
    tasks_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'tasks',
            'tasks_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_tasks_count(self, obj):
        """Get number of tasks in category"""
        return obj.tasks.count()


class CategorySimpleSerializer(serializers.ModelSerializer):
    """
    Simple Category Serializer without tasks
    سریالایزر ساده دسته‌بندی بدون وظایف
    """
    tasks_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'tasks_count', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_tasks_count(self, obj):
        """Get number of tasks in category"""
        return obj.tasks.count()


class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Task Creation Serializer
    سریالایزر ایجاد وظیفه
    """

    class Meta:
        model = Task
        fields = [
            'title', 'description', 'status', 'due_date'
        ]

    def validate_due_date(self, value):
        """Validate due date is in future"""
        from django.utils import timezone
        if value and value < timezone.now():
            raise serializers.ValidationError(
                "Due date cannot be in the past"
            )
        return value