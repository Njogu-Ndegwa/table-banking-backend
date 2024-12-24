from django.urls import path
from .views import loan_list, loan_repayment_list, user_loans_in_wallet, \
                    combined_loans_and_proposals

urlpatterns = [
    # ... other url patterns
    path('loan/', loan_list, name='loan-list'),
    path('loan-repayment/', loan_repayment_list, name="loan_repayment_list"),
    path('user-loans/<int:wallet>/',  user_loans_in_wallet, name=" user-loans-in-wallet"),
    path('loans-and-proposals/', combined_loans_and_proposals, name="combined_loans_and_proposalst"),
]
