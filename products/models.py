from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model


User = get_user_model()
class Car(models.Model):
    id = models.AutoField(primary_key=True)
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    url = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    time = models.DateTimeField()
    year = models.IntegerField()
    mileage = models.FloatField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    price = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'cars_new'

    def save(self, *args, **kwargs):
        kwargs['using'] = 'cars_database'
        super(Car, self).save(*args, **kwargs)

    @classmethod
    def get_queryset(cls):
        return super(Car, cls).objects.using('cars_database')

    def __str__(self):
        return self.title


class CarImage(models.Model):
    car = models.ForeignKey(Car, related_name='images', on_delete=models.CASCADE)
    image_url = models.CharField(max_length=255)

class Wishlist(models.Model):
    user = models.ForeignKey(User, related_name='wishlists', on_delete=models.CASCADE)
    car = models.ForeignKey(Car, related_name='wishlisted_by', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s wishlist item: {self.car.title}"