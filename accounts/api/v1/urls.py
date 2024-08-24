from django.urls import path

from accounts.api.v1.views import CustomUserRetrieveUpdateView, BuyerUserProfileView, SellerUserProfileView

urlpatterns = [
    path('', CustomUserRetrieveUpdateView.as_view(), name='user-detail'),
    path('buyer-profile/', BuyerUserProfileView.as_view(), name='buyer-profile'),
    path('seller-profile/', SellerUserProfileView.as_view(), name='seller-profile'),
]
