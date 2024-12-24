
from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer, CustomUserSerializer
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from .models import Role
from .serializers import RoleSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from decorators.decorators import role_required

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
            roles = user.roles.all()  # Access the actual roles related to the user
            roles_list = [role.name for role in roles]  # Assuming Role model has a `name` field
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
                    'roles': roles_list
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
    

@api_view(['GET', 'POST'])
def role_list(request):
    """
    List all roles, or create a new role.
    """
    if request.method == 'GET':
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def role_detail(request, pk):
    """
    Retrieve, update or delete a role.
    """
    try:
        role = Role.objects.get(pk=pk)
    except Role.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = RoleSerializer(role)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = RoleSerializer(role, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        role.delete()
        response = {"message": "Role Deleted Successfully"}
        return Response(response, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@role_required(roles=['PARTNER'])
def create_member(request):
    user = request.user
    
    phone_number = request.data.get('phone_number')
    id_number = request.data.get('id_number')
    full_name = request.data.get('full_name')
    
    if not phone_number or not id_number or not full_name:
        return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(phone_number=phone_number).exists() or User.objects.filter(id_number=id_number).exists():
        return Response({"error": "A user with this phone number or ID number already exists."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Generate a default password
    default_password = "password"

    # Retrieve the list of role IDs from the request
    role_ids = request.data.get('roles', [])
    
    if not isinstance(role_ids, list):
        return Response({"error": "Roles should be provided as a list."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create the new member user
    member_user = User.objects.create_user(
        phone_number=phone_number,
        id_number=id_number,
        full_name=full_name,
        password=default_password  # Set the default password
    )
    
    # Set additional fields
    member_user.is_active = True
    member_user.is_admin = False
    member_user.partner = user  # Associate the Member with the Partner
    member_user.save()

    # Assign each role to the member user
    for role_id in role_ids:
        try:
            role = Role.objects.get(id=role_id)
            member_user.roles.add(role)
        except Role.DoesNotExist:
            return Response({"error": f"Role with id {role_id} does not exist."}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        "message": "Member created successfully.",
        "status": "success",
        "user_id": member_user.id,
        "partner": {
            "id": user.id,
            "phone_number": user.phone_number,
            "full_name": user.full_name,
            "id_number": user.id_number,
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(roles=['PARTNER'])
def get_members(request):
    user = request.user
    
    # Retrieve all Members associated with the Partner
    members = User.objects.filter(partner=user)
    
    # Serialize the member data
    members_data = [
        {
            "id": member.id,
            "phone_number": member.phone_number,
            "full_name": member.full_name,       
            "roles": list(member.roles.values_list('name', flat=True)),  # List of role names
        }
        for member in members
    ]
    
    return Response({"members": members_data}, status=status.HTTP_200_OK)