from django.urls import path
from .views import PaymentListCreateView, PaymentRetrieveUpdateDestroyView

urlpatterns = [
    path('payments/', PaymentListCreateView.as_view(), name='payment-list-create'),
    path('payments/<int:pk>/', PaymentRetrieveUpdateDestroyView.as_view(), name='payment-detail'),
]