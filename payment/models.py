from django.db import models
from django.utils import timezone
from ads.models import Ad
from django.contrib.auth import get_user_model

User = get_user_model()

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='payments')
    amount = models.FloatField()
    is_successful = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Payment for {self.ad} by {self.user.username}"
