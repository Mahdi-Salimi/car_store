from rest_framework import viewsets, permissions, filters
from rest_framework import viewsets
from rest_framework.decorators import action

from products.models import Car,CarImage
from products.api.v1.serializers import CarSerializer,CarImageSerializer
from accounts.permissions import IsOwner
from rest_framework.response import Response
from rest_framework import status


from django_filters.rest_framework import DjangoFilterBackend
from products.filters import CarFilter
from products.permissions import IsSuperUserOrReadOnly

class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CarFilter
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['created_at', 'price', 'year']
    permission_classes = [permissions.IsAuthenticated, IsSuperUserOrReadOnly]

class CarImageViewSet(viewsets.ModelViewSet):
    queryset = CarImage.objects.all()
    serializer_class = CarImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        car_id = self.request.query_params.get('car_id')
        if car_id:
            return CarImage.objects.filter(car_id=car_id)
        return super().get_queryset()
