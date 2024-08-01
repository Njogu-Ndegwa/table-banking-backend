from django.db import models
from datetime import datetime

class Deposit(models.Model):
    user = models.ForeignKey(
        "users.CustomUser",
        on_delete=models.CASCADE,
        related_name="deposits"
    )
    amount = models.IntegerField()
    created_on = models.DateTimeField(default=datetime.now)






