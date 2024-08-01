class LoanSystem:
    def __init__(self, wallet_balance, interest_rate, current_loan):
        self.wallet_balance = wallet_balance
        self.interest_rate = interest_rate
        self.current_loan = current_loan

    def can_borrow(self, amount):
        # Rule 1: Don't allow borrowing of money if user has another loan
        if self.current_loan > 0:
            return False, "User already has an outstanding loan."

        # Rule 2: Don't allow borrowing of money if wallet associated with user is empty
        if self.wallet_balance <= 0:
            return False, "User's wallet is empty."

        # Rule 3: Don't allow user to borrow more than the total in the wallet
        if amount > self.wallet_balance:
            return False, "Requested loan amount exceeds wallet balance."

        return True, "Loan can be processed."

    def borrow_loan(self, amount):
        can_borrow, message = self.can_borrow(amount)
        if not can_borrow:
            return False, message

        # Rule 4: Deduct borrowed money from wallet
        self.wallet_balance -= amount

        # Rule 5: Fill in the amount to be paid calculated from interest rate and amount borrowed
        amount_to_be_paid = amount + (amount * self.interest_rate)

        # Set the current loan to the amount to be paid
        self.current_loan = amount_to_be_paid

        return True, f"Loan approved. Amount to be repaid: {amount_to_be_paid}"

# Example usage:
# Initialize the loan system with a wallet balance of 1000 and an interest rate of 10%
loan_system = LoanSystem(wallet_balance=1000, interest_rate=0.10, current_loan=0)

# Try to borrow a loan of 500
success, message = loan_system.borrow_loan(500)
print(message)

# The wallet balance should now be 500 and the amount to be repaid should be 550
print(f"Wallet balance: {loan_system.wallet_balance}, Current loan: {loan_system.current_loan}")
