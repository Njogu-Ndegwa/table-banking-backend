from django.urls import path
from .views import user_withdrawals, user_withdrawals_in_wallet


urlpatterns = [
    # ... other url patterns
    path('withdrawals/', user_withdrawals, name='user-withdrawals'),
    path('user-withdrawals/<int:wallet>/', user_withdrawals_in_wallet, name='user-withdrawals-in-wallet')
]
