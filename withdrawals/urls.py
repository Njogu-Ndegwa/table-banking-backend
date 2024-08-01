from django.urls import path
from .views import user_withdrawals


urlpatterns = [
    # ... other url patterns
    path('withdrawals/', user_withdrawals, name='user-withdrawals'),
]
