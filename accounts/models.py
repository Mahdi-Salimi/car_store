import uuid

from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

from accounts.validations.models_validations import validate_phone_number


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    objects = CustomUserManager()

    class UserType(models.TextChoices):
        BUYER = 'b', 'Buyer'
        SELLER = 's', 'Seller'

    username = None
    user_type = models.CharField(max_length=1, choices=UserType.choices, default=UserType.BUYER)
    email = models.EmailField(unique=True, max_length=255)
    phone_number = models.CharField(max_length=15, blank=True, validators=[validate_phone_number])
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True)
    email_verified = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    @property
    def is_buyer(self):
        return self.user_type == self.UserType.BUYER

    @property
    def is_seller(self):
        return self.user_type == self.UserType.SELLER


class BuyerUserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    image = models.ImageField(upload_to='accounts/images', blank=True)

    def __str__(self):
        return f'{self.user.username} (Buyer)'


class SellerUserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    company_name = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='accounts/images', blank=True)
    website = models.URLField(blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    total_sales = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.user.username} (Seller)'


User = get_user_model()


class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    used_at = models.DateTimeField(null=True, blank=True)

    def is_valid(self):
        if self.used_at is not None:
            return False

        return (timezone.now() - self.created_at).total_seconds() < 120

    def set_otp(self, otp):
        self.otp = make_password(otp)

    def check_otp(self, otp):
        return check_password(otp, self.otp)
