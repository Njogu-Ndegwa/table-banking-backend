from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import json
from rest_framework import status
User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('phone_number', 'id_number', 'full_name', 'password', 'confirm_password')

    def create(self, validated_data):
        password = validated_data.pop('password')
        confirm_password = validated_data.pop('confirm_password')
        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

class LoginSerializer(TokenObtainPairSerializer):
    phone_number = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        return data
    

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
