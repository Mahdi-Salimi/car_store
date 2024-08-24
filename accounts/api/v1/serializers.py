from rest_framework import serializers
from django.contrib.auth import get_user_model

from accounts.models import BuyerUserProfile, SellerUserProfile

User = get_user_model()

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'user_type', 'phone_number', 'date_of_birth', 'address']
        read_only_fields = ['email']

class CustomUserFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['email']


class BuyerUserProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = BuyerUserProfile
        fields = ['user']

class SellerUserProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = SellerUserProfile
        fields = ['user', 'company_name', 'website', 'rating', 'total_sales']
