from django.urls import path
from .views import shares_list, shares_detail, user_deposits_in_wallet

urlpatterns = [
    path('shares/', shares_list, name='shares_list'),
    path('shares/<int:pk>/', shares_detail, name='shares_detail'),
    path('shares-wallet/<int:wallet>/', user_deposits_in_wallet, name='user_deposits_in_wallet'),
]
