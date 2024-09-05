from rest_framework import viewsets, permissions, filters
from rest_framework.pagination import PageNumberPagination

from products.models import Car, Wishlist, CarImage
from ads.api.v1.serializers import CarSerializer, WishlistSerializer, CarImageSerializer
from accounts.permissions import IsOwner

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'location', 'seller__username']
    ordering_fields = ['created_at', 'price', 'year']
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

class WishlistViewSet(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CarImageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CarImage.objects.all()
    serializer_class = CarImageSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
