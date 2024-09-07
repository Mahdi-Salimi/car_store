from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdViewSet, PromotedAdViewSet, SellerAdViewSet

router = DefaultRouter()
router.register(r'', AdViewSet, basename='ad')
router.register(r'/promoted', PromotedAdViewSet, basename='promoted_ad')
router.register(r'/my_ads', SellerAdViewSet, basename='seller_ads')

urlpatterns = [
    path('', include(router.urls)),
]
