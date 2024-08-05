from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Wallet, UserWallet, Contribution
from .serializers import WalletSerializer, UserWalletSerializer, ContributionSerializer
from django.shortcuts import get_object_or_404
from decorators.decorators import role_required

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@role_required(roles=['PARTNER'])
def wallet(request):
    if request.method == 'GET':
        '''
        Handle getting wallets that connect multiple users
        '''
        wallet = Wallet.objects.all()
        serializer = WalletSerializer(wallet, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        '''
        Handle creating a wallet that will connect multiple users
        '''
        serializer = WalletSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # serializer.save(user=request.user)  # Set the user to the current user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@role_required(roles=['PARTNER'])
def user_wallet(request):
    if request.method == 'GET':
        '''
        Handle getting wallet that belong to a user
        '''
        print(request)
        wallet = UserWallet.objects.all()
        serializer = UserWalletSerializer(wallet, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        '''
        Handle creating a wallet that will connect multiple users
        '''
        serializer = UserWalletSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # serializer.save(user=request.user)  # Set the user to the current user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(roles=['PARTNER'])
def list_users_in_wallets(request, wallet):
    user = request.user

    if not wallet:
        return Response({'error': 'wallet_id parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
    
    wallet = get_object_or_404(Wallet, id=wallet, owner=user)
    user_wallets = UserWallet.objects.filter(wallet=wallet)
    data = [{
        'user': {
            'id': user_wallet.user.id,
            'full_name': user_wallet.user.full_name,
            'phone_number': user_wallet.user.phone_number,
            'id_number': user_wallet.user.id_number,
            'amount': user_wallet.balance
        },
        'balance': user_wallet.balance
    } for user_wallet in user_wallets]
    return Response(data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@role_required(roles=['PARTNER'])
def contribution_list(request):
    """
    List all contributions, or create a new contribution.
    """
    if request.method == 'GET':
        contributions = Contribution.objects.all()
        serializer = ContributionSerializer(contributions, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ContributionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@role_required(roles=['PARTNER'])
def contribution_detail(request, pk):
    """
    Retrieve, update, or delete a contribution.
    """
    try:
        contribution = Contribution.objects.get(pk=pk)
    except Contribution.DoesNotExist:
        return Response({'message': 'Contribution not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ContributionSerializer(contribution)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ContributionSerializer(contribution, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        contribution.delete()
        response = {"message": "Contribution Deleted Successfully"}
        return Response(response, status=status.HTTP_204_NO_CONTENT)

