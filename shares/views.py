from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Shares
from wallet.models import Wallet
from .serializers import SharesSerializer
from decorators.decorators import role_required
from rest_framework.permissions import IsAuthenticated
from django.db.models import OuterRef, Subquery

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@role_required(roles=['PARTNER', 'MEMBER'])
def shares_list(request):
    """
    List all shares, or create a new share.
    """
    if request.method == 'GET':
        try:
            shares = Shares.objects.filter(user=request.user)
        except Exception as e:
             return Response({"error: User Does not have Deposits"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = SharesSerializer(shares, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = SharesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@role_required(roles=['PARTNER', 'MEMBER'])
def shares_detail(request, pk):
    """
    Retrieve, update or delete a share.
    """
    try:
        share = Shares.objects.get(pk=pk)
    except Shares.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SharesSerializer(share)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = SharesSerializer(share, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        share.delete()
        response = {"message": "Item Deleted Successfully"}
        return Response(response, status=status.HTTP_204_NO_CONTENT)


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
            # Subquery to get the latest share for each user
            latest_shares_subquery = Shares.objects.filter(
                user=OuterRef('user')
            ).order_by('-timestamp').values('id')[:1]
            # Annotate the latest share for each user
            latest_shares = Shares.objects.filter(
                user__in=users
            ).filter(
                id__in=Subquery(latest_shares_subquery)
            )
        except Exception as e:
            return Response({"error": "There was a problem"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = SharesSerializer(latest_shares, many=True)
        return Response(serializer.data)
