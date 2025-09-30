# views.py - Enhanced ViewSets with role-based permissions
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Task
from .serializers import TaskSerializer, UserSerializer
from core.permissions import (
    IsOAuthAuthenticated, IsAdminOrManager,
    IsTaskOwnerOrAssigned, CanEditTask, CanDeleteTask
)
from core.authentication import OAuthBearerAuthentication

User = get_user_model()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for user management"""
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    authentication_classes = [OAuthBearerAuthentication]
    permission_classes = [IsOAuthAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering_fields = ['username', 'first_name', 'created_at']
    ordering = ['username']

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter based on user role
        if self.request.user.role == 'viewer':
            # Viewers can only see themselves and users in their tasks
            return queryset.filter(
                Q(id=self.request.user.id) |
                Q(created_tasks__assigned_to=self.request.user) |
                Q(assigned_tasks__created_by=self.request.user)
            ).distinct()

        return queryset

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user info"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class TaskViewSet(viewsets.ModelViewSet):
    """Enhanced TaskViewSet with role-based permissions"""
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    authentication_classes = [OAuthBearerAuthentication]
    permission_classes = [IsOAuthAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'assigned_to', 'created_by', 'category']
    search_fields = ['title', 'description', 'tags']
    ordering_fields = ['created_at', 'updated_at', 'due_date', 'priority']
    ordering = ['-created_at']

    def get_permissions(self):
        """Override permissions based on action"""
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [IsOAuthAuthenticated, IsTaskOwnerOrAssigned]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsOAuthAuthenticated, CanEditTask]
        elif self.action == 'destroy':
            permission_classes = [IsOAuthAuthenticated, CanDeleteTask]
        else:
            permission_classes = [IsOAuthAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Filter queryset based on user role"""
        queryset = super().get_queryset()
        user = self.request.user

        if user.role == 'admin':
            # Admin can see all tasks
            return queryset
        elif user.role == 'manager':
            # Manager can see all tasks (implement team-based filtering if needed)
            return queryset
        else:
            # Users and viewers can only see tasks they created or are assigned to
            return queryset.filter(
                Q(created_by=user) | Q(assigned_to=user)
            )

    def perform_create(self, serializer):
        """Auto-assign current user as task creator"""
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """Get tasks assigned to current user"""
        tasks = self.get_queryset().filter(assigned_to=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def created_by_me(self, request):
        """Get tasks created by current user"""
        tasks = self.get_queryset().filter(created_by=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign task to a user"""
        task = self.get_object()

        # Check permission to assign
        if not (request.user.role in ['admin', 'manager'] or task.created_by == request.user):
            return Response(
                {'error': 'You do not have permission to assign this task'},
                status=status.HTTP_403_FORBIDDEN
            )

        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            assignee = User.objects.get(id=user_id, is_active=True)
            task.assigned_to = assignee
            task.save()

            serializer = self.get_serializer(task)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'error': 'Invalid user'}, status=status.HTTP_400_BAD_REQUEST)
