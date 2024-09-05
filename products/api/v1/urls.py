from django.urls import path, include
from rest_framework.routers import DefaultRouter
from products.api.v1.views import CarViewSet, WishlistViewSet, CarImageViewSet

router = DefaultRouter()
router.register(r'cars', CarViewSet)
router.register(r'wishlists', WishlistViewSet)
router.register(r'car-images', CarImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
