from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from products.models import Car

User = get_user_model()

class Ad(models.Model):
    car = models.OneToOneField(Car, on_delete=models.CASCADE)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    is_promoted = models.BooleanField(default=False)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    payment_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('completed', 'Completed')],
        default='pending'
    )

    def __str__(self):
        return f"Ad for {self.car.title} by {self.seller.username}"
