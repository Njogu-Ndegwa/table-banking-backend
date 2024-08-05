from django.urls import path
from .views import RegisterView, LoginView, CustomUserList, role_list, role_detail

urlpatterns = [
    # ...
    path('signup/', RegisterView.as_view(), name='auth_register'),
    path('login/', LoginView.as_view(), name='auth_login'),
    path('users', CustomUserList.as_view(), name="auth_users"),
    path('users', CustomUserList.as_view(), name="auth_users"),
    path('roles/', role_list, name='role-list'),
    path('roles/<int:pk>/', role_detail, name='role-detail'),
    # ...
]
