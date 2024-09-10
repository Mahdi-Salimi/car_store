import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from products.models import Car, CarImage
from django.utils import timezone

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user(django_user_model):
    def make_user(email='user@example.com', password='password123', user_type='b', **kwargs):
        return django_user_model.objects.create_user(
            email=email,
            password=password,
            user_type=user_type,
            is_active=True,
            **kwargs
        )
    return make_user

@pytest.fixture
def seller_user(create_user):
    return create_user(email='seller@example.com', user_type='s')

@pytest.fixture
def buyer_user(create_user):
    return create_user(email='buyer@example.com', user_type='b')

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
def car_instance():
    return Car.objects.create(
        title="Test Car",
        description="This is a test car",
        price=10000,
        year=2020,
    )

@pytest.fixture
def car_image_instance(car_instance):
    return CarImage.objects.create(
        car=car_instance,
        image_url="http://example.com/image1.jpg"
    )
