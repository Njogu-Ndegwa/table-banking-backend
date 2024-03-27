from rest_framework import serializers
from .models import Deposit  # Replace with your actual app name and model

class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        fields = ['id', 'user', 'amount']  # Add other fields if necessary
        extra_kwargs = {
            'user': {'read_only': True}
        }

    # def create(self, validated_data):
    #     # Assign the user from the request context to the deposit
    #     print(self.context, "-----14----")
    #     user = self.context['request'].user

    #     deposit = Deposit.objects.create(user=user, **validated_data)
    #     return deposit
