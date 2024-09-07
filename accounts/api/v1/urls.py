from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from accounts.api.v1.views import CustomUserRetrieveUpdateView, BuyerUserProfileView, SellerUserProfileView, LoginView, \
    RegisterView, SendOTPView, VerifyOTPView, LogoutView, PasswordResetView, PasswordResetConfirmView, ChangePasswordView, DeleteAccountView, \
    VerifyEmailView, EmailVerificationView

urlpatterns = [
    path('', CustomUserRetrieveUpdateView.as_view(), name='user-detail'),
    path('buyerprofile/', BuyerUserProfileView.as_view(), name='buyer-profile'),
    path('sellerprofile/', SellerUserProfileView.as_view(), name='seller-profile'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('send_otp_login/', SendOTPView.as_view(), name='send-otp-login'),
    path('verify_otp_login/', VerifyOTPView.as_view(), name='verify-otp-login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password-reset/', PasswordResetView.as_view(), name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('delete-account/', DeleteAccountView.as_view(), name='delete-account'),
    path('verify-email/', EmailVerificationView.as_view(), name='verify-email'),
    path('verify-email/<uidb64>/<token>/', VerifyEmailView.as_view(), name='verify-email-confirm'),
    # path('user-activity/', UserActivityView.as_view(), name='user-activity'),
]
