from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from products.models import Car

User = get_user_model()


class Ad(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('purchased', 'Purchased'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]

    car = models.OneToOneField(Car, on_delete=models.CASCADE, related_name='ad')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ads')
    is_promoted = models.BooleanField(default=False)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    def __str__(self):
        return f"Ad for {self.car.title} by {self.seller.email}"

    def clean(self):
        if self.end_date and self.end_date <= self.start_date:
            raise ValidationError('End date must be later than start date.')

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = self.start_date + timezone.timedelta(days=30)

        self.clean()

        super().save(*args, **kwargs)

    def is_active(self):
        now = timezone.now()
        return self.status == 'active' and self.start_date <= now <= self.end_date

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Advertisement'
        verbose_name_plural = 'Advertisements'

