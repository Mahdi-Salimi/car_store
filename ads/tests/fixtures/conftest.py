import pytest
from django.contrib.auth.models import Group
from rest_framework.test import APIClient
from products.models import Car, CarImage
from ads.models import Ad
from django.utils import timezone

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def seller_user(django_user_model):
    user = django_user_model.objects.create_user(
        email='seller@example.com',
        password='password123',
        user_type='s',
        is_active=True
    )
    seller_group, _ = Group.objects.get_or_create(name='Seller')
    user.groups.add(seller_group)
    return user

@pytest.fixture
def buyer_user(django_user_model):
    user = django_user_model.objects.create_user(
        email='buyer@example.com',
        password='password123',
        user_type='b',
        is_active=True
    )
    buyer_group, _ = Group.objects.get_or_create(name='Buyer')
    user.groups.add(buyer_group)
    return user

@pytest.fixture
def buyer_user2(django_user_model):
    user = django_user_model.objects.create_user(
        email='buyer2@example.com',
        password='password123',
        user_type='b',
        is_active=True
    )
    buyer_group, _ = Group.objects.get_or_create(name='Buyer')
    user.groups.add(buyer_group)
    return user

@pytest.fixture
def car_data():
    return {
        "title": "Test Car",
        "description": "This is a test car",
        "price": 10000,
        "year": 2020,
        "images": [
            {"url": "http://example.com/image1.jpg"},
            {"url": "http://example.com/image2.jpg"}
        ]
    }

@pytest.fixture
def ad_data(car_data):
    return {
        "car": car_data,
        "is_promoted": False,
        "start_date": timezone.now(),
        "end_date": timezone.now() + timezone.timedelta(days=30),

    }

@pytest.fixture
def car_instance():
    return Car.objects.create(
        title="Test Car",
        description="This is a test car",
        price=10000,
        year=2020,
        time= timezone.now(),
    )

@pytest.fixture
def ad_instance(car_instance, seller_user):
    return Ad.objects.create(
        car=car_instance,
        seller=seller_user,
        is_promoted=False,
        start_date=timezone.now(),
        end_date=timezone.now() + timezone.timedelta(days=30),
        status="active"
    )

@pytest.fixture
def another_car_instance():
    return Car.objects.create(
        title="Another Test Car",
        description="This is another test car",
        price=12000,
        year=2021,
        time=timezone.now(),
    )
@pytest.fixture
def promoted_ad_instance(car_instance, seller_user, another_car_instance):
    return Ad.objects.create(
        car=another_car_instance,
        seller=seller_user,
        is_promoted=True,
        start_date=timezone.now(),
        end_date=timezone.now() + timezone.timedelta(days=30),
        status="pending"
    )

@pytest.fixture
def non_promoted_ad_instance(car_instance, seller_user):
    return Ad.objects.create(
        car=car_instance,
        seller=seller_user,
        is_promoted=False,
        start_date=timezone.now(),
        end_date=timezone.now() + timezone.timedelta(days=30),
        status="active"
    )

@pytest.fixture
def another_seller_ad_instance(another_car_instance, buyer_user):
    return Ad.objects.create(
        car=another_car_instance,
        seller=buyer_user,
        is_promoted=False,
        start_date=timezone.now(),
        end_date=timezone.now() + timezone.timedelta(days=30),
        status="active"
    )



