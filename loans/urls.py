from django.urls import path
from .views import loan_list, loan_repayment_list

urlpatterns = [
    # ... other url patterns
    path('loan/', loan_list, name='loan-list'),
    path('loan-repayment/', loan_repayment_list, name="loan_repayment_list")
]
