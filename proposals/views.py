# views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import LoanProposal, LoanProposalVote
from .serializers import LoanProposalSerializer, LoanProposalVoteSerializer
from rest_framework.permissions import IsAuthenticated
from wallet.models import UserWallet
import requests

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def loan_proposal(request):
    if request.method == "GET":
        proposals = LoanProposal.objects.all()
        serializer = LoanProposalSerializer(proposals, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = LoanProposalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def loan_proposal_detail(request, pk):
    try:
        proposal = LoanProposal.objects.get(pk=pk)
    except LoanProposal.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = LoanProposalSerializer(proposal)
    return Response(serializer.data)

@api_view(["GET","POST"])
@permission_classes([IsAuthenticated])
def loan_proposal_vote(request):
    if request.method == "GET":
        votes = LoanProposalVote.objects.all()
        serializer = LoanProposalVoteSerializer(votes, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        try:
            proposal = LoanProposal.objects.get(pk=request.data.get('proposal'))
        except LoanProposal.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


        vote = request.data.get("vote")
        if vote is None:
            return Response({"error": "Vote field is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            LoanProposalVote.objects.create(user=request.user, proposal=proposal, vote=vote)
        except Exception as e:
            print(e)
            return Response({"error": "You can not vote for the same proposal more than twice."}, status=status.HTTP_400_BAD_REQUEST)
        
        total_voters = count_users_connected_to_wallet(proposal.wallet)
        total_votes = count_votes_for_proposal(proposal)
        print(total_voters, total_votes)
       
        # Check if all members have voted "yes" for this proposal
        if proposal.votes.filter(vote=False).exists() or total_votes < total_voters:
            return Response({"message": "Not all members voted yes."}, status=status.HTTP_200_OK)
        else:
            url = "http://localhost:8000/api/loan/"
            borrower = proposal.user.pk
            amount = proposal.amount
            interest_rate = 10
            term = 2
            print(borrower, "----73-----")
            data = {
                "borrower": borrower,
                "amount_borrowed": amount,
                "interest_rate": interest_rate,
                "term": term
            }
            requests.post(url=url, data=data)
            return Response({"message": "All members voted yes."}, status=status.HTTP_200_OK)


def count_users_connected_to_wallet(wallet_id):
    # Use the Django ORM to filter UserWallet objects by the wallet_id and count them
    user_wallet_count = UserWallet.objects.filter(wallet=wallet_id).count()
    
    return user_wallet_count


def count_votes_for_proposal(proposal_id):
    # Assuming LoanProposalVote has a foreign key to LoanProposal called 'proposal'
    # and LoanProposal has a primary key called 'id'
    total_votes = LoanProposalVote.objects.filter(proposal=proposal_id).count()
    return total_votes
