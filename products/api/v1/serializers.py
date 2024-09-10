from rest_framework import serializers
from products.models import Car, CarImage
class CarImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarImage
        fields = ['id', 'image_url']

class CarSerializer(serializers.ModelSerializer):
    images = CarImageSerializer(many=True, read_only=True)

    class Meta:
        model = Car
        fields = ['id', 'url', 'title', 'time', 'year', 'mileage', 'location', 'description', 'images', 'created_at', 'price']
        read_only_fields = ['id', 'url', 'time', 'created_at']


