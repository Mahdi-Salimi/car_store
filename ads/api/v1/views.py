from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from django.contrib.auth.models import Group

from ads.models import Ad
from .serializers import AdSerializer
from ads.permissions import IsSellerPermission

class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticated, IsSellerPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['car__title', 'car__mileage', 'car__year', 'start_date', 'end_date']
    ordering_fields = ['start_date', 'end_date', 'is_promoted']

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

class PromotedAdListView(generics.ListAPIView):
    queryset = Ad.objects.filter(is_promoted=True)
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticated]

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
