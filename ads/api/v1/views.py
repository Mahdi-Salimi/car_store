from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import F,Q
from rest_framework.decorators import action

from accounts.api.v1.serializers import SellerContactSerializer
from rest_framework import filters
from rest_framework.exceptions import PermissionDenied


from django.contrib.auth.models import Group

from ads.models import Ad, Wishlist
from .serializers import AdSerializer, WishlistSerializer
from ads.permissions import IsSellerPermission
from accounts.permissions import IsOwner




class AdViewSet(viewsets.ModelViewSet):
    serializer_class = AdSerializer
    permission_classes = [IsSellerPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['car__title', 'car__mileage', 'car__year', 'start_date', 'end_date']
    ordering_fields = ['start_date', 'end_date', 'is_promoted']

    def get_queryset(self):
        user = self.request.user
        queryset = Ad.objects.all()

        if user.is_authenticated and user.user_type == 'b':
            wishlist_ads = Wishlist.objects.filter(user=user).values_list('ad', flat=True)

            queryset = queryset.filter(
                Q(is_promoted=True) |
                Q(id__in=wishlist_ads) |
                Q(car__title__in=Ad.objects.filter(id__in=wishlist_ads).values_list('car__title', flat=True)) |
                Q(car__mileage__in=Ad.objects.filter(id__in=wishlist_ads).values_list('car__mileage', flat=True))
            )

        return queryset.order_by(F('is_promoted').desc(), 'id')

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

class WishlistViewSet(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if self.request.user.user_type == 's':
            raise PermissionDenied("Sellers are not allowed to add ads to the wishlist.")
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['delete'])
    def remove(self, request, pk=None):
        try:
            wishlist_item = self.get_object()
            wishlist_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Wishlist.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
