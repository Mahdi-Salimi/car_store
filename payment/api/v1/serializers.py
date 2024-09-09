from rest_framework import serializers
from payment.models import Payment, PROMOTION_FEE
from payment.gateway import mock_payment_gateway
from ads.models import Ad


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['user', 'ad', 'amount', 'is_successful', 'transaction_id', 'created_at']
        read_only_fields = ['user', 'is_successful', 'transaction_id', 'created_at']

    def validate(self, data):
        request = self.context.get('request')
        ad = data.get('ad', None)

        if self.instance:
            ad = self.instance.ad

        if ad.seller != request.user:
            raise serializers.ValidationError("You can only update payments for ads that you own.")

        if not self.instance and Payment.objects.filter(ad=ad, is_successful=True).exists():
            raise serializers.ValidationError("This ad has already been promoted.")

        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        gateway_response = mock_payment_gateway(validated_data['amount'])
        payment = Payment.objects.create(**validated_data)
        payment.process_payment(
            transaction_id=gateway_response['transaction_id'],
            success=gateway_response['success']
        )

        return payment

