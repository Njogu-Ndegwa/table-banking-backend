from rest_framework import serializers
from .models import Withdraw  # Replace with your actual app name and model

class WithdrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdraw
        fields = "__all__"