"""
Core Views for Client Internal APIs
ویوهای اصلی برای APIهای داخلی کلاینت
"""
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Task, Category, UserProfile
from .serializers import (
    TaskSerializer, CategorySerializer,
    UserProfileSerializer, UserSerializer
)


class TaskViewSet(viewsets.ModelViewSet):
    """
    Task ViewSet for CRUD operations
    ویو ست وظایف برای عملیات CRUD
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return tasks for current user"""
        return Task.objects.filter(assigned_to=self.request.user)

    def perform_create(self, serializer):
        """Set created_by to current user"""
        serializer.save(
            created_by=self.request.user,
            assigned_to=self.request.user
        )

    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """Get current user's tasks"""
        tasks = self.get_queryset()
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get task statistics for current user"""
        tasks = self.get_queryset()
        stats = {
            'total': tasks.count(),
            'pending': tasks.filter(status='pending').count(),
            'in_progress': tasks.filter(status='in_progress').count(),
            'completed': tasks.filter(status='completed').count(),
            'cancelled': tasks.filter(status='cancelled').count(),
        }
        return Response(stats)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    Category ViewSet for managing categories
    ویو ست دسته‌بندی برای مدیریت دسته‌ها
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def add_tasks(self, request, pk=None):
        """Add tasks to category (M2M operation)"""
        category = self.get_object()
        task_ids = request.data.get('task_ids', [])

        # Validate task IDs belong to current user
        user_tasks = Task.objects.filter(
            id__in=task_ids,
            assigned_to=request.user
        )

        if len(user_tasks) != len(task_ids):
            return Response({
                'error': 'Some tasks do not belong to you or do not exist'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Add tasks to category
        category.tasks.add(*user_tasks)

        return Response({
            'message': f'{len(user_tasks)} tasks added to category',
            'category': CategorySerializer(category).data
        })

    @action(detail=True, methods=['post'])
    def remove_tasks(self, request, pk=None):
        """Remove tasks from category"""
        category = self.get_object()
        task_ids = request.data.get('task_ids', [])

        # Remove tasks from category
        category.tasks.remove(*task_ids)

        return Response({
            'message': f'Tasks removed from category',
            'category': CategorySerializer(category).data
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Get current user's profile
    دریافت پروفایل کاربر فعلی
    """
    try:
        profile = request.user.profile
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    except UserProfile.DoesNotExist:
        # Create profile if doesn't exist
        profile = UserProfile.objects.create(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    Update current user's profile
    به‌روزرسانی پروفایل کاربر فعلی
    """
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    serializer = UserProfileSerializer(
        profile,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    """
    Dashboard endpoint with user stats
    اندپوینت داشبورد با آمار کاربر
    """
    user = request.user

    # Get user tasks
    tasks = Task.objects.filter(assigned_to=user)

    # Get categories with user's tasks
    categories = Category.objects.filter(
        tasks__assigned_to=user
    ).distinct()

    dashboard_data = {
        'user': UserSerializer(user).data,
        'tasks_stats': {
            'total': tasks.count(),
            'pending': tasks.filter(status='pending').count(),
            'in_progress': tasks.filter(status='in_progress').count(),
            'completed': tasks.filter(status='completed').count(),
        },
        'recent_tasks': TaskSerializer(
            tasks.order_by('-created_at')[:5],
            many=True
        ).data,
        'categories_count': categories.count(),
    }

    return Response(dashboard_data)