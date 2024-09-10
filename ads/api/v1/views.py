from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import F
from accounts.api.v1.serializers import SellerContactSerializer
from rest_framework import filters
from rest_framework.exceptions import PermissionDenied


from django.contrib.auth.models import Group

from ads.models import Ad
from .serializers import AdSerializer
from ads.permissions import IsSellerPermission

class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all().order_by(F('is_promoted').desc(), 'id')
    serializer_class = AdSerializer
    permission_classes = [IsSellerPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['car__title', 'car__mileage', 'car__year', 'start_date', 'end_date']
    ordering_fields = ['start_date', 'end_date', 'is_promoted']

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

class PromotedAdListView(generics.ListAPIView):
    queryset = Ad.objects.filter(is_promoted=True)
    serializer_class = AdSerializer

class SellerAdListCreateView(generics.ListCreateAPIView):
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticated, IsSellerPermission]

    def get_queryset(self):
        return Ad.objects.filter(seller=self.request.user)

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

class SellerAdRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticated, IsSellerPermission]

    def get_queryset(self):
        return Ad.objects.filter(seller=self.request.user)


class SellerContactView(generics.RetrieveAPIView):
    serializer_class = SellerContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        ad_id = self.kwargs['ad_id']
        ad = get_object_or_404(Ad, id=ad_id)
        seller = ad.seller

        if not self.request.user.email_verified:
            raise PermissionDenied(detail="Please verify your email first.")

        return seller