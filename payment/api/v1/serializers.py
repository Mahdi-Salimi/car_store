from rest_framework import serializers
from payment.models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['user', 'ad', 'amount', 'is_successful', 'transaction_id', 'created_at']
