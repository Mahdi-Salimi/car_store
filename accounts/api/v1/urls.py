from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from accounts.api.v1.views import CustomUserRetrieveUpdateView, BuyerUserProfileView, SellerUserProfileView, LoginView, RegisterView, SendOTPView, VerifyOTPView

urlpatterns = [
    path('', CustomUserRetrieveUpdateView.as_view(), name='user-detail'),
    path('buyerprofile/', BuyerUserProfileView.as_view(), name='buyer-profile'),
    path('sellerprofile/', SellerUserProfileView.as_view(), name='seller-profile'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
]
