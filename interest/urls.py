from django.urls import path
from .views import interest_list_create, interest_detail, user_interests_in_wallet

urlpatterns = [
    path('interest/', interest_list_create, name='interest_list'),
    path('interest/<int:pk>/', interest_detail, name='interest_detail'),
    path('interest-wallet/<int:wallet>/', user_interests_in_wallet, name='user_interests_in_wallet'),
]
