from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Deposit
from .serializers import DepositSerializer

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
        serializer = DepositSerializer(data=request.data)
        print(serializer, "----20----")
        if serializer.is_valid():
            serializer.save(user=request.user)  # Set the user to the current user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
