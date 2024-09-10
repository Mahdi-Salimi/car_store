from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()
class Car(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    time = models.DateTimeField(null=True, blank=True)
    year = models.IntegerField()
    mileage = models.FloatField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    price = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ('url', 'time')

    def __str__(self):
        return self.title


class CarImage(models.Model):
    car = models.ForeignKey(Car, related_name='images', on_delete=models.CASCADE)
    image_url = models.CharField(max_length=255)

