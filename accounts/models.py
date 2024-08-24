from django.contrib.auth.models import AbstractUser
from django.db import models

from accounts.validations.models_validations import validate_phone_number
class CustomUser(AbstractUser):
    class UserType(models.TextChoices):
        BUYER = 'b', 'Buyer'
        SELLER = 's', 'Seller'
        ADMIN = 'a', 'Admin'

    user_type = models.CharField(max_length=1, choices=UserType.choices, default=UserType.BUYER)
    email = models.EmailField(unique=True, max_length=255)
    phone_number = models.CharField(max_length=15, blank=True, validators=[validate_phone_number])
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True)
    # profile_picture

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    @property
    def is_buyer(self):
        return self.user_type == self.UserType.BUYER

    @property
    def is_seller(self):
        return self.user_type == self.UserType.SELLER

    @property
    def is_admin(self):
        return self.user_type == self.UserType.ADMIN
