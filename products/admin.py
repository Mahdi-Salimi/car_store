from django.contrib import admin
from products.models import Car, CarImage, Wishlist

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['title', 'year', 'price', 'created_at']
    search_fields = ['title', 'description']

@admin.register(CarImage)
class CarImageAdmin(admin.ModelAdmin):
    list_display = ['car', 'image_url']

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'car', 'added_at']
