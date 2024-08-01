from django.db import models

class InterestEarned(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    loan_repayment = models.ForeignKey('loans.LoanRepayment', on_delete=models.CASCADE)
    interest_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)