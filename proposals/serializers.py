from rest_framework import serializers
from .models import LoanProposal, LoanProposalVote

class LoanProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanProposal
        fields = "__all__"

class LoanProposalVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanProposalVote
        fields = "__all__"
