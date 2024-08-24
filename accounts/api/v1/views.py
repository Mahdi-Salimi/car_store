from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from accounts.api.v1.serializers import CustomUserSerializer, BuyerUserProfileSerializer, SellerUserProfileSerializer
from accounts.models import BuyerUserProfile, SellerUserProfile

class CustomUserRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class BuyerUserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = BuyerUserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return BuyerUserProfile.objects.get(user=self.request.user)


class SellerUserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = SellerUserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return SellerUserProfile.objects.get(user=self.request.user)
