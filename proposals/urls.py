from django.urls import path
from .views import loan_proposal, loan_proposal_vote, \
                    loan_proposals_in_wallet, votes_in_loan_proposal

urlpatterns = [
    # ... other url patterns
    path('proposal/', loan_proposal, name='create_loan_proposal'),
    path('vote/', loan_proposal_vote, name="loan_proposal_vote"),
    path('proposal-wallet/<int:wallet>/', loan_proposals_in_wallet, name="loan_proposals_in_wallet"),
    path('vote-proposal/<int:proposal>/', votes_in_loan_proposal, name="votes_in_loan_proposal"),
]
