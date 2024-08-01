from django.urls import path
from .views import loan_proposal, loan_proposal_vote

urlpatterns = [
    # ... other url patterns
    path('proposal/', loan_proposal, name='create_loan_proposal'),
    path('vote/', loan_proposal_vote, name="loan_proposal_vote")
]
