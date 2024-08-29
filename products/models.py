from django.db import models
from django.utils import timezone

class Car(models.Model):
    id = models.AutoField(primary_key=True)
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