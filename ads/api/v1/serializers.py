from rest_framework import serializers
from django.db import transaction

from ads.models import Ad, Wishlist
from products.api.v1.serializers import CarSerializer
from products.models import Car, CarImage


class AdSerializer(serializers.ModelSerializer):
    car = CarSerializer()

    class Meta:
        model = Ad
        fields = ['id', 'seller', 'car', 'is_promoted', 'start_date', 'end_date', 'status']
        read_only_fields = ['seller', 'start_date', 'end_date', 'status', 'is_promoted']

    def create(self, validated_data):
        validated_data.pop('seller', None)
        car_data = validated_data.pop('car')
        images_data = car_data.pop('images', [])

        with transaction.atomic():
            car = Car.objects.create(**car_data)
            for image_data in images_data:
                CarImage.objects.create(car=car, **image_data)
            ad = Ad.objects.create(car=car, seller=self.context['request'].user, **validated_data)

        return ad

    def update(self, instance, validated_data):
        car_data = validated_data.pop('car', None)

        if car_data:
            images_data = car_data.pop('images', [])
            for attr, value in car_data.items():
                setattr(instance.car, attr, value)
            instance.car.save()

            instance.car.images.all().delete()
            for image_data in images_data:
                CarImage.objects.create(car=instance.car, **image_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class WishlistSerializer(serializers.ModelSerializer):
    ad = serializers.PrimaryKeyRelatedField(queryset=Ad.objects.all())

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'ad', 'added_at']
        read_only_fields = ['user', 'added_at']

    def validate_ad(self, value):
        user = self.context['request'].user
        if Wishlist.objects.filter(user=user, ad=value).exists():
            raise serializers.ValidationError("You have already added this ad to your wishlist.")
        return value
