from rest_framework import viewsets, permissions, filters
from rest_framework import viewsets
from rest_framework.decorators import action

from products.models import Car, Wishlist, CarImage
from products.api.v1.serializers import CarSerializer, WishlistSerializer, CarImageSerializer
from accounts.permissions import IsOwner
from rest_framework.response import Response
from rest_framework import status


from django_filters.rest_framework import DjangoFilterBackend
from products.filters import CarFilter

class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CarFilter
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['created_at', 'price', 'year']
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

class WishlistViewSet(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['delete'])
    def remove(self, request, pk=None):
        try:
            wishlist_item = self.get_object()
            wishlist_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Wishlist.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class CarImageViewSet(viewsets.ModelViewSet):
    queryset = CarImage.objects.all()
    serializer_class = CarImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        car_id = self.request.query_params.get('car_id')
        if car_id:
            return CarImage.objects.filter(car_id=car_id)
        return super().get_queryset()
