from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Deposit
from .serializers import DepositSerializer
from wallet.models import UserWallet, Contribution
from services.shares import update_user_shares

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def user_deposits(request):
    # Handle GET request: List all deposits for the current user
    if request.method == 'GET':
        deposits = Deposit.objects.filter(user=request.user)
        serializer = DepositSerializer(deposits, many=True)
        return Response(serializer.data)

    # Handle POST request: Create a new deposit for the current user
    elif request.method == 'POST':
        print(request.data, "----22---")
        print(request.user, "------23---")
        request.data['user'] = request.user.pk
        serializer = DepositSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Set the user to the current user
            user_wallet = UserWallet.objects.get(user=request.user)
            wallet = user_wallet.wallet
            deposit = serializer.save(wallet=wallet)
            user_wallet.balance += deposit.amount
            user_wallet.save()
            wallet.balance += deposit.amount
            wallet.total_balance += deposit.amount
            Contribution.objects.create(
                user_wallet= user_wallet,
                amount = deposit.amount
            )
            wallet.save()
            print(request.user, "-----36----")
            update_user_shares(request.user, deposit.amount)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


