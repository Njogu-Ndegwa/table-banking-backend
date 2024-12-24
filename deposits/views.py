from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Deposit
from .serializers import DepositSerializer
from wallet.models import UserWallet, Contribution, Wallet
from services.shares import update_user_shares
from decorators.decorators import role_required
from rest_framework.permissions import IsAuthenticated

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@role_required(roles=['PARTNER', 'MEMBER'])
def user_deposits(request):
    # Handle GET request: List all deposits for the current user
    if request.method == 'GET':
        try:
            deposits = Deposit.objects.filter(user=request.user)
        except Exception as e:
             return Response({"error: User Does not have Deposits"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = DepositSerializer(deposits, many=True)
        return Response(serializer.data)

    # Handle POST request: Create a new deposit for the current user
    elif request.method == 'POST':
        request.data['user'] = request.user.pk
        serializer = DepositSerializer(data=request.data)
        try:
            user_wallet = UserWallet.objects.get(user=request.user)
        except Exception as e:
                return Response({"error: User Wallet Doesn't Exist"}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Set the user to the current user
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
            update_user_shares(request.user, deposit.amount)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(roles=['PARTNER'])
def user_deposits_in_wallet(request, wallet):
    # Handle GET request: List all deposits for the current user
    if request.method == 'GET':
        try:
            wallet = Wallet.objects.get(id=wallet)
            # Get all users associated with this wallet
            user_wallets = wallet.userwallet_set.all()
            users = [user_wallet.user for user_wallet in user_wallets]
            # Get all deposits for these users
            deposits = Deposit.objects.filter(user__in=users)
            print(deposits, "-----63----")
        except Exception as e:
             return Response({"error: There was a problem"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = DepositSerializer(deposits, many=True)
        return Response(serializer.data)

