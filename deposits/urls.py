from django.urls import path
from .views import user_deposits

urlpatterns = [
    # ... other url patterns
    path('deposits/', user_deposits, name='user-deposits'),
]
