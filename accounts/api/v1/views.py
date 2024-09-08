from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.throttling import ScopedRateThrottle

from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site



from accounts.utils import generate_otp
from accounts.tasks import send_otp_email, send_password_reset_email, send_verification_email

from accounts.api.v1.serializers import CustomUserSerializer, CustomUserFullSerializer, BuyerUserProfileSerializer, \
    SellerUserProfileSerializer, RegisterSerializer, LoginSerializer, SendOTPSerializer, VerifyOTPSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer, ChangePasswordSerializer
from accounts.models import BuyerUserProfile, SellerUserProfile, OTP
from accounts.permissions import IsOwner
from config.settings import CACHE_TTL

User = get_user_model()


class CustomUserRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self):
        return self.request.user


class BuyerUserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = BuyerUserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self):
        return BuyerUserProfile.objects.get(user=self.request.user)


class SellerUserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = SellerUserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self):
        return SellerUserProfile.objects.get(user=self.request.user)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        return Response({
            "refresh_token": str(refresh),
            "access_token": str(access_token),
            "message": "User registered successfully."
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    throttle_scope = 'login'
    throttle_classes = [ScopedRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SendOTPView(APIView):
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(email=serializer.validated_data['email'])
            otp = generate_otp()
            otp_record = OTP.objects.create(user=user)
            otp_record.set_otp(otp)
            otp_record.save()

            send_otp_email.delay(user.email, otp)

            return Response({"message": "OTP sent successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    throttle_scope = 'login'
    throttle_classes = [ScopedRateThrottle]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(email=serializer.validated_data['email'])
            except User.DoesNotExist:
                return Response(
                    {"non_field_errors": ["User does not exist."]},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                otp_record = user.otp_set.latest('created_at')
            except OTP.DoesNotExist:
                return Response(
                    {"non_field_errors": ["OTP not found for this user."]},
                    status=status.HTTP_400_BAD_REQUEST
                )

            otp_record.used_at = timezone.now()
            otp_record.save()

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            return Response({
                "access_token": access_token,
                "refresh_token": refresh_token
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh_token")

        if refresh_token is None:
            return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout successful."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=serializer.validated_data['email'])

        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = reverse('password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})
        token_url = f"{request.scheme}://{request.get_host()}{reset_url}"

        send_password_reset_email.delay(user.email, token_url)

        return Response({"detail": "Password reset email sent."}, status=status.HTTP_200_OK)

class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = get_user_model()
    permission_classes = [IsAuthenticated]

    def get_object(self, queryset=None):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'detail': 'Password changed successfully'}, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        serializer.save()

class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.delete()
        return Response({'detail': 'Account deleted successfully'}, status=status.HTTP_200_OK)

class EmailVerificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.email:
            return Response({"detail": "No email associated with this account."}, status=400)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        verification_url = f"http://{get_current_site(request).domain}/accounts/api/v1/verify-email/{uid}/{token}/"

        send_verification_email.delay(user.email, verification_url)

        return Response({"detail": "Verification email sent."}, status=200)

class VerifyEmailView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.email_verified = True
            user.save()
            return Response({"detail": "Email verified successfully."}, status=200)
        else:
            return Response({"detail": "Invalid verification link or token."}, status=400)


