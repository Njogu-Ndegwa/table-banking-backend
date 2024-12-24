from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Loan, LoanRepayment
from wallet.models import Wallet
from .serializers import LoanSerializer, LoanRepaymentSerializer
# from .business_rules import LoanSystem
from wallet.models import UserWallet
from decimal import Decimal
from services.interest import update_interest_earned
from decorators.decorators import role_required
from proposals.models import LoanProposal
@api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
# @role_required(roles=['PARTNER', 'MEMBER'])
def loan_list(request):
    if request.method == 'GET':
        try:
            loans = Loan.objects.filter(borrower=request.user)
        except Exception as e:
             print(e, "-----21----")
             return Response({"error: User Does not have Loans"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = LoanSerializer(loans, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        borrower = request.data['borrower']
        borrowed_amount = Decimal(request.data['amount_borrowed'])
        interest_rate = Decimal(request.data['interest_rate'])
        main_wallet_id = request.data['wallet']
        try:
            user_wallet = UserWallet.objects.get(user=borrower)
        except Exception as e:
            return Response({"error: User Wallet does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            main_wallet = Wallet.objects.get(id=main_wallet_id)  # Fetching the Wallet instance
        except Wallet.DoesNotExist:
            return Response({"error": "Wallet does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = LoanSerializer(data=request.data)
        wallet = user_wallet.wallet
        wallet_balance = wallet.balance
        try:
            current_loan = Loan.objects.filter(borrower=borrower, status__in=['active', 'defaulted'])
        except Exception as e:
            return Response({"error: Member Does not have a current loan"}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            result = borrow_loan(borrowed_amount, current_loan, wallet_balance, interest_rate)
            new_wallet_balance = result['wallet_balance']
            amount_to_be_paid = result["amount_to_be_paid"]
            serializer.validated_data["amount_to_be_paid"] = amount_to_be_paid
            serializer.validated_data['wallet'] = main_wallet
            wallet.balance = new_wallet_balance
            wallet.save()
            print(wallet, "------50----Wallet")
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@role_required(roles=['PARTNER', 'MEMBER'])
def loan_detail(request, pk):
    try:
        loan = Loan.objects.get(pk=pk)
    except Loan.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = LoanSerializer(loan)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = LoanSerializer(loan, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        loan.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@role_required(roles=['PARTNER', 'MEMBER'])
def loan_repayment_list(request):
    if request.method == 'GET':
        repayments = LoanRepayment.objects.all()
        serializer = LoanRepaymentSerializer(repayments, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = LoanRepaymentSerializer(data=request.data)
        loan= request.data['loan']
        repayment_amount = request.data['amount']
        if serializer.is_valid():
                       # Retrieve the Loan instance
            loan_id = serializer.validated_data.get('loan')  # Adjust this based on your serializer
            print(loan)
            try:
                loan = Loan.objects.get(pk=loan)
            except Loan.DoesNotExist:
                return Response({"error": "Loan not found"}, status=status.HTTP_404_NOT_FOUND)

            try:
                user_wallet = UserWallet.objects.get(user=loan.borrower)
            except Loan.DoesNotExist:
                return Response({"error": "Wallet not found"}, status=status.HTTP_404_NOT_FOUND)
  

            # Check if the loan is paid off
            if loan.is_paid_off():
                return Response({"error": "Loan is already paid off"}, status=status.HTTP_400_BAD_REQUEST)
            
            remaining_balance = loan.calculate_remaining_balance()
            if repayment_amount > remaining_balance:
                return Response(
                    {"error": "Repayment amount exceeds remaining balance."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if remaining_balance == repayment_amount:
                loan.status = "paid_off"

            serializer.validated_data['remaining_balance'] = remaining_balance - repayment_amount
            
            wallet = user_wallet.wallet
            wallet.balance += repayment_amount
            loan_repayment = serializer.save()
            update_interest_earned(loan_repayment)
            loan.save()
            wallet.save()
            # serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@role_required(roles=['PARTNER', 'MEMBER'])
def loan_repayment_detail(request, pk):
    try:
        repayment = LoanRepayment.objects.get(pk=pk)
    except LoanRepayment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = LoanRepaymentSerializer(repayment)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = LoanRepaymentSerializer(repayment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        repayment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

def can_borrow(amount, current_loan, wallet_balance):
        # Rule 1: Don't allow borrowing of money if user has another loan
        if len(current_loan) > 0:
            return False, "User already has an outstanding loan."

        # Rule 2: Don't allow borrowing of money if wallet associated with user is empty
        if wallet_balance <= 0:
            return False, "User's wallet is empty."

        # Rule 3: Don't allow user to borrow more than the total in the wallet
        if amount > wallet_balance:
            return False, "Requested loan amount exceeds wallet balance."

        return True, "Loan can be processed."



def borrow_loan(amount, current_loan, wallet_balance, interest_rate):
    cn_borrow, message = can_borrow(amount, current_loan, wallet_balance)
    if not cn_borrow:
        return {"wallet_balance": None, "amount_to_be_paid": None, "status": False}

    # Rule 4: Deduct borrowed money from wallet
    wallet_balance -= amount

    # Rule 5: Fill in the amount to be paid calculated from interest rate and amount borrowed
    amount_to_be_paid = amount + (amount * interest_rate/100)

    # # Set the current loan to the amount to be paid
    # current_loan = amount_to_be_paid

    return {"wallet_balance": wallet_balance, "amount_to_be_paid": amount_to_be_paid, "status": True}

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(roles=['PARTNER'])
def user_loans_in_wallet(request, wallet):
    # Handle GET request: List all deposits for the current user
    if request.method == 'GET':
        try:
            wallet = Wallet.objects.get(id=wallet)
            # Get all users associated with this wallet
            user_wallets = wallet.userwallet_set.all()
            users = [user_wallet.user for user_wallet in user_wallets]
            # Get all deposits for these users
            loans = Loan.objects.filter(borrower__in=users)

        except Exception as e:
             return Response({"error: There was a problem"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = LoanSerializer(loans, many=True)
        return Response(serializer.data)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(roles=['PARTNER', 'MEMBER'])
def combined_loans_and_proposals(request):
    try:
        # Retrieve loans and loan proposals for the given wallet
        loans = Loan.objects.filter(borrower=request.user)
        loan_proposals = LoanProposal.objects.filter(user=request.user)

        # Prepare the combined data manually
        combined_data = []

        for loan in loans:
            combined_data.append({
                'id': loan.id,
                'amount': loan.amount_borrowed,
                'status': loan.status,
                'date': loan.start_date,
            })

        for proposal in loan_proposals:
            combined_data.append({
                'id': proposal.id,
                'amount': proposal.amount,
                'status': proposal.status,
                'date': proposal.created_at,
            })

        # Sort combined data by date (optional)
        combined_data = sorted(combined_data, key=lambda x: x['date'], reverse=True)

        return Response(combined_data, status=status.HTTP_200_OK)

    except Loan.DoesNotExist:
        return Response({"error": "Loan not found"}, status=status.HTTP_404_NOT_FOUND)
    except LoanProposal.DoesNotExist:
        return Response({"error": "LoanProposal not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)