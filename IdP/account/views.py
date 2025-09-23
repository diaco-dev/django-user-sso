from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import login
import logging

from .models import User, UserProfile
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserProfileSerializer
)

logger = logging.getLogger(__name__)


class UserRegistrationView(generics.CreateAPIView):
    """
    User registration endpoint
    نقطه پایانی ثبت‌نام کاربر
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens for the new user
        refresh = RefreshToken.for_user(user)

        logger.info(f"New user registered: {user.email}")

        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
import logging
from django.views.decorators.csrf import csrf_exempt
logger = logging.getLogger(__name__)
@csrf_exempt
def login_view(request):
    """
    Handle user login
    مدیریت ورود کاربر
    """
    if request.method == 'GET':
        # Display login form
        next_url = request.GET.get('next', '/')
        return render(request, 'account/login.html', {'next': next_url})

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            logger.info(f"User {username} logged in successfully")
            next_url = request.POST.get('next', reverse('account_profile'))
            return HttpResponseRedirect(next_url)
        else:
            logger.warning(f"Failed login attempt for username: {username}")
            messages.error(request, 'Invalid username or password')
            return render(request, 'account/login.html', {'next': request.POST.get('next', '')})

    logger.error(f"Invalid request method: {request.method}")
    return render(request, 'account/login.html', {'error': 'Method not allowed'})

@api_view(['GET'])
@csrf_exempt
@permission_classes([IsAuthenticated])
def user_profile_view(request):
    """
    Get current user profile
    دریافت پروفایل کاربر جاری
    """
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile_view(request):
    """
    Update user profile
    بروزرسانی پروفایل کاربر
    """
    user = request.user

    # Update user basic info
    user_serializer = UserSerializer(user, data=request.data, partial=True)
    if user_serializer.is_valid():
        user_serializer.save()

    # Update user profile
    profile, created = UserProfile.objects.get_or_create(user=user)
    profile_data = request.data.get('profile', {})
    profile_serializer = UserProfileSerializer(profile, data=profile_data, partial=True)

    if profile_serializer.is_valid():
        profile_serializer.save()

        return Response({
            'user': UserSerializer(user).data,
            'message': 'Profile updated successfully'
        })

    errors = {}
    if hasattr(user_serializer, 'errors'):
        errors.update(user_serializer.errors)
    if hasattr(profile_serializer, 'errors'):
        errors.update({'profile': profile_serializer.errors})

    return Response(errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    User logout endpoint
    نقطه پایانی خروج کاربر
    """
    try:
        refresh_token = request.data.get("refresh")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()

        logger.info(f"User logged out: {request.user.email}")

        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': 'Invalid token'
        }, status=status.HTTP_400_BAD_REQUEST)