# views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import LoanProposal, LoanProposalVote
from .serializers import LoanProposalSerializer, LoanProposalVoteSerializer
from rest_framework.permissions import IsAuthenticated
from wallet.models import UserWallet, Wallet
import requests
from decorators.decorators import role_required


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
@role_required(roles=['PARTNER', 'MEMBER'])
def loan_proposal(request):
    if request.method == "GET":
        try:
            proposals = LoanProposal.objects.filter(user=request.user)
        except Exception as e:
             return Response({"error: User Does not have any Proposals"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = LoanProposalSerializer(proposals, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = LoanProposalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@role_required(roles=['PARTNER', 'MEMBER'])
def loan_proposal_detail(request, pk):
    try:
        proposal = LoanProposal.objects.get(pk=pk)
    except LoanProposal.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = LoanProposalSerializer(proposal)
    return Response(serializer.data)

@api_view(["GET","POST"])
@permission_classes([IsAuthenticated])
@role_required(roles=['PARTNER', 'MEMBER'])
def loan_proposal_vote(request):
    if request.method == "GET":
        try:
            votes = LoanProposalVote.objects.filter(user=request.user)
        except Exception as e:
             return Response({"error: User Does not have any Votes"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = LoanProposalVoteSerializer(votes, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        try:
            proposal = LoanProposal.objects.get(pk=request.data.get('proposal'))
        except LoanProposal.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


        vote = request.data.get("vote")
        wallet = request.data.get('wallet')
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
            print(amount, "---74")
            print(interest_rate, "-----87---")
            print(term, "----88----")
            data = {
                "borrower": borrower,
                "amount_borrowed": amount,
                "interest_rate": interest_rate,
                "term": term,
                "wallet": wallet
            }
            token = request.headers.get('Authorization')
            headers = {
                            "Authorization": token
                      }
            try:
                requests.post(url=url, data=data)
            except Exception as e:
                return Response({"error": "There was a problem creating a loan"}, status=status.HTTP_400_BAD_REQUEST)
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



@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(roles=['PARTNER', 'MEMBER'])
def loan_proposals_in_wallet(request, wallet):
    if request.method == 'GET':
        try:
            wallet = Wallet.objects.get(id=wallet)
            # Get all users associated with this wallet
            user_wallets = wallet.userwallet_set.all()
            users = [user_wallet.user for user_wallet in user_wallets]
            # Get all pending loan proposals for these users
            loan_proposals = LoanProposal.objects.filter(user__in=users, status='Pending')

        except Exception as e:
            return Response({"error: There was a problem"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = LoanProposalSerializer(loan_proposals, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(roles=['PARTNER', 'MEMBER'])
def votes_in_loan_proposal(request, proposal):
    # Handle GET request: List all deposits for the current user
    if request.method == 'GET':
        try:
            # Get all deposits for these users
            vote = LoanProposalVote.objects.filter(proposal=proposal)

        except Exception as e:
             return Response({"error: There was a problem"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = LoanProposalVoteSerializer(vote, many=True)
        return Response(serializer.data)

