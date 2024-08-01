# models.py

from django.db import models

class LoanProposal(models.Model):
    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)
    wallet = models.ForeignKey("wallet.Wallet", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=[("Pending", "Pending"), ("Approved", "Approved"), ("Rejected", "Rejected")], default=("Pending"))
    created_at = models.DateTimeField(auto_now_add=True)

class LoanProposalVote(models.Model):
    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)
    proposal = models.ForeignKey(LoanProposal, on_delete=models.CASCADE, related_name='votes')
    vote = models.BooleanField()  # True for "yes", False for "no"
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        # Unique constraint on the combination of 'user' and 'proposal'
        unique_together = ('user', 'proposal')
