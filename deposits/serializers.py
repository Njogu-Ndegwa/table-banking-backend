from rest_framework import serializers
from .models import Deposit  # Replace with your actual app name and model

class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        fields = "__all__"