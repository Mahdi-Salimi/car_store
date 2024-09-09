from django.urls import path, include

urlpatterns = [
    path('api/v1/', include('payment.api.v1.urls')),
    ]