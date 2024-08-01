from django.urls import path
from .views import wallet, user_wallet, contribution_list, contribution_detail

urlpatterns = [
    # ... other url patterns
    path('wallet/', wallet, name='wallet'),
    path('user-wallet/', user_wallet, name="user-wallet"),
    path('contributions/', contribution_list, name='contribution_list'),
    path('contributions/<int:pk>/', contribution_detail, name='contribution_detail'),
]
