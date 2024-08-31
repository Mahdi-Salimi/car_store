from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken


from accounts.api.v1.serializers import CustomUserSerializer, CustomUserFullSerializer, BuyerUserProfileSerializer, SellerUserProfileSerializer, RegisterSerializer, LoginSerializer
from accounts.models import BuyerUserProfile, SellerUserProfile
from accounts.permissions import IsOwner

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

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
