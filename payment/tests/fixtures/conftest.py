import pytest

from django.contrib.auth import get_user_model
from django.utils import timezone

from ads.models import Ad
from products.models import Car
from payment.models import Payment

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(email='testuser@bama.com', password='password123')


@pytest.fixture
def car_instance():
    return Car.objects.create(
        title="Test Car",
        description="This is a test car",
        price=10000,
        year=2020,
        time=timezone.now(),
    )


@pytest.fixture
def ad(user, car_instance):
    return Ad.objects.create(seller=user, car=car_instance, is_promoted=False)


@pytest.fixture
def payment(user, ad):
    return Payment.objects.create(user=user, ad=ad, amount=100.00, is_successful=True)
