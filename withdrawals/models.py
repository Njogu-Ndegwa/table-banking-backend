from django.db import models
from datetime import datetime


class Withdraw(models.Model):
    user = models.ForeignKey(
        "users.CustomUser",
        on_delete=models.CASCADE,
        related_name="withdraw"
    )
    amount = models.IntegerField()
    created_on = models.DateTimeField(default=datetime.now)

