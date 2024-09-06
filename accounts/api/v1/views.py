from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.throttling import ScopedRateThrottle

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes



from accounts.utils import generate_otp
from accounts.tasks import send_otp_email, send_password_reset_email

from accounts.api.v1.serializers import CustomUserSerializer, CustomUserFullSerializer, BuyerUserProfileSerializer, \
    SellerUserProfileSerializer, RegisterSerializer, LoginSerializer, SendOTPSerializer, VerifyOTPSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer, ChangePasswordSerializer
from accounts.models import BuyerUserProfile, SellerUserProfile, OTP
from accounts.permissions import IsOwner

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
            user = User.objects.get(email=serializer.validated_data['email'])

            otp_record = user.otp_set.latest('created_at')
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
        try:
            refresh_token = request.data.get("refresh_token")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout successful."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]
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

        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Password changed successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)