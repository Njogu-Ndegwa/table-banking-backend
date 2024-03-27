from django.db import models
from datetime import datetime
from users.models import CustomUser


class Deposit(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="deposits"
    )
    amount = models.IntegerField()
    created_on = models.DateTimeField(default=datetime.now)

