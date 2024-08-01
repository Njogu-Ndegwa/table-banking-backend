from django.db import models

class Shares(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    share_change = models.DecimalField(max_digits=10, decimal_places=2)  # Positive for deposits, negative for withdrawals
    share_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)


    