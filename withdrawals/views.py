from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Withdraw
from .serializers import WithdrawSerializer
from wallet.models import UserWallet, Contribution
from shares.models import Shares
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from interest.models import InterestEarned
from django.db import transaction
from services.shares import update_user_shares

@transaction.atomic
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def user_withdrawals(request):
    # Handle GET request: List all widrawals for the current user
    if request.method == 'GET':
        widrawals = Withdraw.objects.filter(user=request.user)
        serializer = WithdrawSerializer(widrawals, many=True)
        return Response(serializer.data)

    # Handle POST request: Create a new withdrawal for the current user
    elif request.method == 'POST':
        serializer = WithdrawSerializer(data=request.data)
        request.data['user'] = request.user.pk
        user_wallet = UserWallet.objects.get(user=request.user)
        # total_contributions = get_total_contributions_by_user(user_wallet)
        # total_interest = get_total_interest_earned_by_user(request.user)
        # limit = total_contributions + total_interest
        if request.data['amount'] > user_wallet.balance:
            return Response({"message": "You can't withdraw more than your deposits"}, status=status.HTTP_400_BAD_REQUEST)
        # print(total_contributions, total_interest, "-------28-----")
        if serializer.is_valid():
            serializer.save(user=request.user)  # Set the user to the current user
            wallet = user_wallet.wallet
            withdrawal = serializer.save(wallet=wallet)
            user_wallet.balance -= withdrawal.amount
            user_wallet.save()
            wallet.balance -= withdrawal.amount
            wallet.total_balance -= withdrawal.amount
            Contribution.objects.create(
                user_wallet=user_wallet,
                amount=- withdrawal.amount
            )
            wallet.save()
            update_user_shares(request.user, -withdrawal.amount)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    