from django.urls import path
from .views import interest_list_create, interest_detail

urlpatterns = [
    path('interest/', interest_list_create, name='interest_list'),
    path('interest/<int:pk>/', interest_detail, name='interest_detail'),
]
