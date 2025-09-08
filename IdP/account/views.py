from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth.models import User
from django.shortcuts import render
from .models import CustomUser
from .serializers import RegisterSerializer

# Register API
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": RegisterSerializer(user, context=self.get_serializer_context()).data,
            "message": "User registered successfully"
        }, status=status.HTTP_201_CREATED)

# Custom Token Obtain View
class CustomTokenObtainPairView(TokenObtainPairView):
    pass

# Custom Token Refresh View
class CustomTokenRefreshView(TokenRefreshView):
    pass


def login(request):
    return render(request, 'registration/login.html')
