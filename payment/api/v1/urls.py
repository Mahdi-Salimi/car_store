from django.urls import path
from .views import PaymentCreateView

urlpatterns = [
    path('payment/', PaymentCreateView.as_view(), name='payment-create'),
]
