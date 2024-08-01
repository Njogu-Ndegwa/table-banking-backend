from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Loan, LoanRepayment
from .serializers import LoanSerializer, LoanRepaymentSerializer
# from .business_rules import LoanSystem
from wallet.models import UserWallet
from decimal import Decimal
from services.interest import update_interest_earned
@api_view(['GET', 'POST'])
def loan_list(request):
    if request.method == 'GET':
        loans = Loan.objects.all()
        serializer = LoanSerializer(loans, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = LoanSerializer(data=request.data)
        borrower = request.data['borrower']
        borrowed_amount = Decimal(request.data['amount_borrowed'])
        interest_rate = Decimal(request.data['interest_rate'])
        user_wallet = UserWallet.objects.get(user=borrower)
        wallet = user_wallet.wallet
        wallet_balance = wallet.balance
        current_loan = Loan.objects.filter(borrower=borrower, status__in=['active', 'defaulted'])

        if serializer.is_valid():
            result = borrow_loan(borrowed_amount, current_loan, wallet_balance, interest_rate)
            new_wallet_balance = result['wallet_balance']
            amount_to_be_paid = result["amount_to_be_paid"]
            serializer.validated_data["amount_to_be_paid"] = amount_to_be_paid
            wallet.balance = new_wallet_balance
            wallet.save()
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET', 'PUT', 'DELETE'])
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

