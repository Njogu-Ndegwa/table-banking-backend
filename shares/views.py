from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Shares
from .serializers import SharesSerializer

@api_view(['GET', 'POST'])
def shares_list(request):
    """
    List all shares, or create a new share.
    """
    if request.method == 'GET':
        shares = Shares.objects.all()
        serializer = SharesSerializer(shares, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = SharesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
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
