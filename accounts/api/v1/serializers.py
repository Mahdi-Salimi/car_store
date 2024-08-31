from django.contrib.auth import get_user_model, authenticate

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

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

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'user_type', 'phone_number', 'date_of_birth', 'address', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    token = serializers.SerializerMethodField()

    def get_token(self, obj):
        user = authenticate(email=obj['email'], password=obj['password'])
        if user:
            refresh = RefreshToken.for_user(user)
            return {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        return None

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid login credentials")
        return data
