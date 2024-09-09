from rest_framework import serializers
from payment.models import Payment, PROMOTION_FEE
from payment.gateway import mock_payment_gateway


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['user', 'ad', 'amount', 'is_successful', 'transaction_id', 'created_at']

    def validate_amount(self, value):
        if value != PROMOTION_FEE:
            raise serializers.ValidationError(f"Payment amount must be exactly {PROMOTION_FEE}.")
        return value

    def create(self, validated_data):
        payment = Payment.objects.create(**validated_data)
        gateway_response = mock_payment_gateway(validated_data['amount'])

        payment.process_payment(
            transaction_id=gateway_response['transaction_id'],
            success=gateway_response['success']
        )

        return payment
