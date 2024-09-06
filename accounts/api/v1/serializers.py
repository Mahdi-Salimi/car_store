from django.contrib.auth import get_user_model, authenticate

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode


from accounts.models import BuyerUserProfile, SellerUserProfile

User = get_user_model()

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'user_type', 'phone_number', 'date_of_birth', 'address']

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

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

class SellerUserProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = SellerUserProfile
        fields = ['user', 'company_name', 'website', 'rating', 'total_sales']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

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
            raise AuthenticationFailed("Invalid login credentials")
        return data

class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        user = User.objects.get(email=data['email'])
        try:
            otp_record = user.otp_set.latest('created_at')
        except OTP.DoesNotExist:
            raise serializers.ValidationError("OTP does not exist or has expired.")

        if not otp_record.is_valid():
            raise serializers.ValidationError("OTP has expired.")

        if not otp_record.check_otp(data['otp']):
            raise serializers.ValidationError("Invalid OTP.")

        return data

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, data):
        try:
            uid = urlsafe_base64_decode(data['uidb64']).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError('Invalid token or user ID')

        if not default_token_generator.check_token(user, data['token']):
            raise serializers.ValidationError('Invalid token')

        return data

    def save(self):
        uid = urlsafe_base64_decode(self.validated_data['uidb64']).decode()
        user = User.objects.get(pk=uid)
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
