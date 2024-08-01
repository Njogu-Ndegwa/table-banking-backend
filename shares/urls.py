from django.urls import path
from .views import shares_list, shares_detail

urlpatterns = [
    path('shares/', shares_list, name='shares_list'),
    path('shares/<int:pk>/', shares_detail, name='shares_detail'),
]
