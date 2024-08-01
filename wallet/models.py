from django.db import models
from datetime import datetime


class Wallet(models.Model):
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class UserWallet(models.Model):
    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ('user', 'wallet')


class Contribution(models.Model):
    user_wallet = models.ForeignKey(UserWallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)



