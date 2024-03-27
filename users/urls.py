from django.urls import path
from .views import RegisterView, LoginView, CustomUserList

urlpatterns = [
    # ...
    path('signup/', RegisterView.as_view(), name='auth_register'),
    path('login/', LoginView.as_view(), name='auth_login'),
    path('users', CustomUserList.as_view(), name="auth_users")
    # ...
]
