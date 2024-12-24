from django.urls import path
from .views import user_deposits, user_deposits_in_wallet

urlpatterns = [
    # ... other url patterns
    path('deposits/', user_deposits, name='user-deposits'),
    path('user-deposits/<int:wallet>/', user_deposits_in_wallet, name='user-deposits-in-wallet'),
]
