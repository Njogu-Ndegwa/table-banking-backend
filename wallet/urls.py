from django.urls import path
from .views import wallet, user_wallet, contribution_list, \
      contribution_detail, list_users_in_wallets, user_contributions_in_wallet, \
      wallet_transactions_view, user_transactions_view

urlpatterns = [
    # ... other url patterns
    path('wallet/', wallet, name='wallet'),
    path('user-wallet/', user_wallet, name="user-wallet"),
    path('users-in-wallet/<int:wallet>/', list_users_in_wallets, name="list-users-in-wallets"),
    path('contributions-userwallet/<int:wallet>', contribution_list, name='contribution_list'),
    path('contributions-wallet/<int:wallet>', user_contributions_in_wallet, name='user_contributions_in_wallet'),
    path('contributions/<int:pk>/', contribution_detail, name='contribution_detail'),
    path('transactions/<int:wallet_id>/', wallet_transactions_view, name='wallet_transactions_view'),
    path('user-transactions/', user_transactions_view, name='user_transactions_view'),
]
