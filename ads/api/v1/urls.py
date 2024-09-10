from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdViewSet, PromotedAdListView, SellerAdListCreateView, SellerAdRetrieveUpdateDestroyView, SellerContactView, WishlistViewSet

router = DefaultRouter()
router.register(r'ads', AdViewSet, basename='ad')
router.register(r'wishlists', WishlistViewSet, basename='wishlist')

urlpatterns = [
    path('promoted/', PromotedAdListView.as_view(), name='promoted_ad-list'),
    path('my_ads/', SellerAdListCreateView.as_view(), name='seller_ads-list-create'),
    path('my_ads/<int:pk>/', SellerAdRetrieveUpdateDestroyView.as_view(), name='seller_ads-detail'),
    path('<int:ad_id>/seller-contact/', SellerContactView.as_view(), name='seller-contact'),
    path('', include(router.urls)),
]
