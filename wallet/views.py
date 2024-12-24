from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Wallet, UserWallet, Contribution
from .serializers import WalletSerializer, UserWalletSerializer, ContributionSerializer
from django.shortcuts import get_object_or_404
from decorators.decorators import role_required
from loans.models import Loan, LoanRepayment
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@role_required(roles=['PARTNER'])
def wallet(request):
    if request.method == 'GET':
        '''
        Handle getting wallets that connect multiple users
        '''
        try:
            wallet = Wallet.objects.filter(owner=request.user)
        except Exception as e:
            return Response({"error: Owner has no Wallet"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = WalletSerializer(wallet, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        '''
        Handle creating a wallet that will connect multiple users
        '''
        request.data['owner'] = request.user.id
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
            'id': user_wallet.user.id,
            'full_name': user_wallet.user.full_name,
            'phone_number': user_wallet.user.phone_number,
            'id_number': user_wallet.user.id_number,
            'amount': user_wallet.balance,
            'wallet_name': user_wallet.wallet.name
    } for user_wallet in user_wallets]
    return Response(data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@role_required(roles=['PARTNER'])
def contribution_list(request, wallet):
    """
    List all contributions, or create a new contribution.
    """
    if request.method == 'GET':
        try:
            contributions = Contribution.objects.filter(user_wallet=wallet)
        except Exception as e:
            return Response({"error: Owner has no Wallet"}, status=status.HTTP_400_BAD_REQUEST)
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(roles=['PARTNER'])
def user_contributions_in_wallet(request, wallet):
    # Handle GET request: List all deposits for the current user
    if request.method == 'GET':
        try:
            wallet = Wallet.objects.get(id=wallet)
            # Get all users associated with this wallet
            user_wallets = wallet.userwallet_set.all()
            print(user_wallets, "------144-----")
            # users = [user_wallet.user for user_wallet in user_wallets]
            # Get all deposits for these users
            contributions = Contribution.objects.filter(user_wallet__in=user_wallets)

        except Exception as e:
             return Response({"error: There was a problem"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ContributionSerializer(contributions, many=True)
        return Response(serializer.data)
    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(roles=['PARTNER'])
def wallet_transactions_view(request, wallet_id):
    # Get the Wallet instance or return 404 if not found
    wallet = get_object_or_404(Wallet, id=wallet_id)
    user_wallets = UserWallet.objects.filter(wallet=wallet)
    loans = Loan.objects.filter(borrower__in=user_wallets.values_list('user', flat=True))
    loan_repayments = LoanRepayment.objects.filter(loan__in=loans)
    contributions = Contribution.objects.filter(user_wallet__in=user_wallets)
    print(loans, "------165-----")
    active_loans = loans.filter(status='active')
    transactions = []

    for repayment in loan_repayments:
        borrower = repayment.loan.borrower
        transaction_type = "Loan Repayment"
        transactions.append({
            "id": repayment.id,
            "transaction_type": transaction_type,
            "amount": str(repayment.amount),  # Convert Decimal to string for JSON serialization
            "date": repayment.date,
            "full_name": borrower.full_name,  # Using the full_name field from CustomUser
            "phone_number": borrower.phone_number  # Using the phone_number field from CustomUser
        })

    for contribution in contributions:
        user = contribution.user_wallet.user
        transaction_type = "Withdrawal" if contribution.amount < 0 else "Deposit"
        transactions.append({
            "id": contribution.id,
            "transaction_type": transaction_type,
            "amount": str(contribution.amount),  # Convert Decimal to string for JSON serialization
            "date": contribution.date,
            "full_name": user.full_name,  # Using the full_name field from CustomUser
            "phone_number": user.phone_number  # Using the phone_number field from CustomUser
        })

    for loan in active_loans:
        borrower = loan.borrower
        transactions.append({
            "id": loan.id,
            "transaction_type": "Active Loan",
            "amount": str(loan.amount_borrowed * -1),  # Using the amount_borrowed field
            "date": loan.start_date,
            "full_name": borrower.full_name,  # Using the full_name field from CustomUser
            "phone_number": borrower.phone_number  # Using the phone_number field from CustomUser
        })

    # Sort the transactions by date (optional)
    transactions = sorted(transactions, key=lambda x: x["date"], reverse=True)

    return Response(transactions, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(roles=['MEMBER', 'PARTNER'])
def user_transactions_view(request):

    # Get the UserWallet instance for the authenticated user
    user_wallet = get_object_or_404(UserWallet, user=request.user)

    # Get all loans for the authenticated user
    loans = Loan.objects.filter(borrower=request.user)
    
    # Get all loan repayments for the loans of the authenticated user
    loan_repayments = LoanRepayment.objects.filter(loan__in=loans)
    
    # Get all contributions for the authenticated user's wallet
    contributions = Contribution.objects.filter(user_wallet=user_wallet)
    
    active_loans = loans.filter(status='active')
    
    transactions = []

    # Add loan repayments to transactions
    for repayment in loan_repayments:
        transaction_type = "Loan Repayment"
        transactions.append({
            "id": repayment.id,
            "transaction_type": transaction_type,
            "amount": str(repayment.amount),  # Convert Decimal to string for JSON serialization
            "date": repayment.date,
            "full_name": request.user.full_name,  # Using the full_name field from CustomUser
            "phone_number": request.user.phone_number  # Using the phone_number field from CustomUser
        })

    # Add contributions to transactions
    for contribution in contributions:
        transaction_type = "Withdrawal" if contribution.amount < 0 else "Deposit"
        transactions.append({
            "id": contribution.id,
            "transaction_type": transaction_type,
            "amount": str(contribution.amount),  # Convert Decimal to string for JSON serialization
            "date": contribution.date,
            "full_name": request.user.full_name,  # Using the full_name field from CustomUser
            "phone_number": request.user.phone_number  # Using the phone_number field from CustomUser
        })

    # Add active loans to transactions
    for loan in active_loans:
        transactions.append({
            "id": loan.id,
            "transaction_type": "Active Loan",
            "amount": str(loan.amount_borrowed * -1),  # Using the amount_borrowed field
            "date": loan.start_date,
            "full_name": request.user.full_name,  # Using the full_name field from CustomUser
            "phone_number": request.user.phone_number  # Using the phone_number field from CustomUser
        })

    # Sort the transactions by date (optional)
    transactions = sorted(transactions, key=lambda x: x["date"], reverse=True)

    return Response(transactions, status=status.HTTP_200_OK)

