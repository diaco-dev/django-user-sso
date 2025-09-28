# serializers.py - Enhanced serializers with user relationships
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Task

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'role']
        read_only_fields = ['id', 'username']


class TaskSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    # comments = TaskCommentSerializer(many=True, read_only=True)
    # comments_count = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'created_by', 'assigned_to', 'assigned_to_id',
            'created_at', 'updated_at', 'due_date', 'completed_at',
            'tags', 'category',
            'can_edit', 'can_delete'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'completed_at', 'created_by']

    def get_can_edit(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False

        user = request.user
        return (
                user.role == 'admin' or
                user.role == 'manager' or
                (user.role == 'user' and obj.created_by == user)
        )

    def get_can_delete(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False

        user = request.user
        return user.role == 'admin' or obj.created_by == user

    def create(self, validated_data):
        # Auto-assign current user as creator
        validated_data['created_by'] = self.context['request'].user

        # Handle assigned_to_id
        assigned_to_id = validated_data.pop('assigned_to_id', None)
        if assigned_to_id:
            try:
                assigned_user = User.objects.get(id=assigned_to_id)
                validated_data['assigned_to'] = assigned_user
            except User.DoesNotExist:
                raise serializers.ValidationError({'assigned_to_id': 'Invalid user ID'})

        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Handle assigned_to_id
        assigned_to_id = validated_data.pop('assigned_to_id', None)
        if assigned_to_id is not None:
            if assigned_to_id:
                try:
                    assigned_user = User.objects.get(id=assigned_to_id)
                    validated_data['assigned_to'] = assigned_user
                except User.DoesNotExist:
                    raise serializers.ValidationError({'assigned_to_id': 'Invalid user ID'})
            else:
                validated_data['assigned_to'] = None

        return super().update(instance, validated_data)

    def validate_assigned_to_id(self, value):
        if value and not User.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Invalid or inactive user")
        return value
