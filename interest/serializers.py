from rest_framework import serializers
from .models import InterestEarned  # Replace with your actual app name and model

class InterestEarnedSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterestEarned
        fields = "__all__"