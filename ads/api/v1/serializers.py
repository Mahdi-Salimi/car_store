from rest_framework import serializers
from ads.models import Ad
from products.api.v1.serializers import CarSerializer
from products.models import Car, CarImage

class AdSerializer(serializers.ModelSerializer):
    car = CarSerializer()

    class Meta:
        model = Ad
        fields = ['id', 'seller', 'car', 'is_promoted', 'start_date', 'end_date', 'payment_status']
        read_only_fields = ['seller', 'payment_status']

    def create(self, validated_data):
        car_data = validated_data.pop('car')
        images_data = car_data.pop('images', [])
        car = Car.objects.create(**car_data)
        for image_data in images_data:
            CarImage.objects.create(car=car, **image_data)
        ad = Ad.objects.create(car=car, **validated_data)
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
