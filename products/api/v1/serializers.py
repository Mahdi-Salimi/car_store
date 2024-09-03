from rest_framework import serializers
from products.models import Car, CarImage, Wishlist

class CarImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarImage
        fields = ['id', 'image_url']

class CarSerializer(serializers.ModelSerializer):
    images = CarImageSerializer(many=True, read_only=True)

    class Meta:
        model = Car
        fields = ['id', 'seller', 'url', 'title', 'time', 'year', 'mileage', 'location', 'description', 'images', 'created_at', 'price']
        read_only_fields = ['seller', 'created_at']

class WishlistSerializer(serializers.ModelSerializer):
    car = CarSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'car', 'added_at']
        read_only_fields = ['user', 'added_at']
