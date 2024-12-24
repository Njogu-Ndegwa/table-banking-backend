from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import InterestEarned
from wallet.models import Wallet
from .serializers import InterestEarnedSerializer
from decorators.decorators import role_required
from rest_framework.permissions import IsAuthenticated

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@role_required(roles=['PARTNER', 'MEMBER'])
def interest_list_create(request):
    """
    List all interest records, or create a new interest record.
    """
    if request.method == 'GET':
        try:
            interests = InterestEarned.objects.filter(user=request.user)
        except Exception as e:
             return Response({"error: Problem Showing the Interest Earned"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = InterestEarnedSerializer(interests, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = InterestEarnedSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@role_required(roles=['PARTNER', 'MEMBER'])
def interest_detail(request, pk):
    """
    Retrieve, update, or delete an interest record.
    """
    try:
        interest = InterestEarned.objects.get(pk=pk)
    except InterestEarned.DoesNotExist:
        return Response({'message': 'The interest record does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = InterestEarnedSerializer(interest)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = InterestEarnedSerializer(interest, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        interest.delete()
        return Response({'message': 'Interest record was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(roles=['PARTNER'])
def user_interests_in_wallet(request, wallet):
    # Handle GET request: List all deposits for the current user
    if request.method == 'GET':
        try:
            wallet = Wallet.objects.get(id=wallet)
            # Get all users associated with this wallet
            user_wallets = wallet.userwallet_set.all()
            users = [user_wallet.user for user_wallet in user_wallets]
            print(users, "----73----")
            # Get all deposits for these users
            interest = InterestEarned.objects.filter(user__in=users)
        except Exception as e:
             return Response({"error: There was a problem"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = InterestEarnedSerializer(interest, many=True)
        return Response(serializer.data)
