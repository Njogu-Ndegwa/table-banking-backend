from django.db import models
from datetime import datetime
from shares.models import Shares
from interest.models import InterestEarned
from django.shortcuts import get_object_or_404
from wallet.models import UserWallet

class Loan(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paid_off', 'Paid Off'),
        ('defaulted', 'Defaulted'),
    ]
    
    borrower = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)
    wallet = models.ForeignKey("wallet.Wallet", on_delete=models.SET_NULL, related_name="loans", null=True, blank=True)  # Nullable wallet field
    amount_borrowed = models.DecimalField(max_digits=10, decimal_places=2)
    amount_to_be_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    term = models.IntegerField()
    start_date = models.DateTimeField(default=datetime.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def is_paid_off(self):
        return self.status == 'paid_off'



    def calculate_remaining_balance(self):
        # Calculate the remaining balance based on repayments
        repayments = LoanRepayment.objects.filter(loan=self)
        total_paid = sum(repayment.amount for repayment in repayments)
        remaining_balance = self.amount_to_be_paid - total_paid
        return remaining_balance



class LoanRepayment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(default=datetime.now)
    remaining_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('completed', 'Completed')], default='pending')

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)  # Call the real save() method
    #     # Update Shares after the deposit is saved
    #     self.update_interest_earned()

    # def update_interest_earned(self):
    #     user = self.loan.borrower
    #     user_data = self.users_in_same_wallet(user)
    #     interest_rate = self.loan.interest_rate
    #     loan_amount = self.loan.amount_borrowed
    #     for user in user_data:
    #         latest_share = Shares.objects.filter(user=user['user']).order_by('-timestamp').first()
    #         if not latest_share:
    #             interest_earned_amount = 0
    #         else:
    #             interest_amount = (loan_amount * interest_rate)/100
    #             print(loan_amount, "-----60----")
    #             print(self.amount, "AMount")
    #             print(interest_amount, "----59----")
    #             interest_earned_amount = (interest_amount * latest_share.share_percentage) / 100
    #             user_wallet = get_object_or_404(UserWallet, user=user['user'])
    #             user_wallet.balance += interest_earned_amount
    #             user_wallet.save()
    #             InterestEarned.objects.create(
    #                 user=user['user'],
    #                 loan_repayment=self,
    #                 interest_amount=interest_earned_amount
    #             )

    # def users_in_same_wallet(request, user):
    #     user_wallet = get_object_or_404(UserWallet, user=user)
    #     wallet = user_wallet.wallet
    #     user_wallets = UserWallet.objects.filter(wallet=wallet)
    #     users = [uw.user for uw in user_wallets]
    #     user_data = [{'id': user.id, 'phone_number': user.phone_number, "user": user} for user in users]
    #     return user_data

