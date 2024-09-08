from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdViewSet, PromotedAdListView, SellerAdListCreateView, SellerAdRetrieveUpdateDestroyView

router = DefaultRouter()
router.register(r'', AdViewSet, basename='ad')


urlpatterns = [
    path('promoted/', PromotedAdListView.as_view(), name='promoted_ad-list'),
    path('my_ads/', SellerAdListCreateView.as_view(), name='seller_ads-list-create'),
    path('my_ads/<int:pk>/', SellerAdRetrieveUpdateDestroyView.as_view(), name='seller_ads-detail'),
    path('', include(router.urls)),

]

