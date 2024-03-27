
from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer, CustomUserSerializer
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework_simplejwt.authentication import JWTAuthentication

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response_data = {
            'status': 'success',
            'message': 'User registered successfully',
            'data': serializer.data
        }
        return Response(response_data, status=201, headers=headers)
    

    def handle_exception(self, exc):
        response_data = {
            'status': 'error',
            'message': 'An error occurred while registering the user',
            'error': exc.detail,
        }
        return Response(response_data, status=400)
    
class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(**serializer.validated_data)
        if user and user.is_active:
            # groups = user.groups.all()
            # permissions = user.user_permissions.all()
            refresh = RefreshToken.for_user(user)
            response_data = {
                'status': 'success',
                'message': 'User logged in successfully',
                'data': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'phone_number': user.phone_number,
                    'id_number': user.id_number,
                    'full_name': user.full_name,
                }
            }
            return Response(response_data, status=200)
        else:
            response_data = {
                'status': 'error',
                'message': 'Incorrect credentials'
            }
            return Response(response_data, status=400)

class CustomUserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    authentication_classes = [JWTAuthentication]

    def post(self, request, format=None):
        user = request.user
        groups = user.groups.all()
        permissions = user.user_permissions.all()

        response_data= {
            'groups': groups,
            'permissions': permissions
        }
        return Response(response_data, status=200)
