from django.urls import path
from .views import RegisterView, LoginView, CustomUserList, \
    role_list, role_detail, create_member, get_members

urlpatterns = [
    # ...
    path('signup/', RegisterView.as_view(), name='auth_register'),
    path('login/', LoginView.as_view(), name='auth_login'),
    path('users', CustomUserList.as_view(), name="auth_users"),
    path('roles/', role_list, name='role-list'),
    path('roles/<int:pk>/', role_detail, name='role-detail'),
    path('create-member/', create_member, name='create-member'),
    path('get-members/', get_members, name='get-members'),
    # ...
]
