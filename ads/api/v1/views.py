from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from django.contrib.auth.models import Group

from ads.models import Ad
from .serializers import AdSerializer
from ads.permissions import IsSellerPermission

class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticated, IsSellerPermission]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)