import pytest

from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import BuyerUserProfile, SellerUserProfile
from accounts.api.v1.serializers import BuyerUserProfileSerializer, SellerUserProfileSerializer, CustomUserSerializer

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user():
    def make_user(**kwargs):
        return User.objects.create_user(**kwargs)
    return make_user


@pytest.fixture
def buyer_user(create_user):
    user = create_user(email='buyer_unique@example.com', password='password123@#QW', user_type=User.UserType.BUYER)

    if not BuyerUserProfile.objects.filter(user=user).exists():
        BuyerUserProfile.objects.create(user=user)

    return user


@pytest.fixture
def seller_user(create_user):
    user = create_user(email='seller_unique@example.com', password='password1231@#QW', user_type=User.UserType.SELLER)

    if not SellerUserProfile.objects.filter(user=user).exists():
        SellerUserProfile.objects.create(
            user=user,
            company_name='Test Cars Ltd.',
            website='http://testcars.com',
            rating=4.5,
            total_sales=100
        )

    return user

@pytest.fixture
def buyer_user_profile(buyer_user):
    return BuyerUserProfile.objects.get(user=buyer_user)

@pytest.fixture
def seller_user_profile(seller_user):
    return SellerUserProfile.objects.get(user=seller_user)

@pytest.fixture
def auth_client(api_client, buyer_user):
    api_client.force_authenticate(user=buyer_user)
    return api_client

@pytest.fixture
def auth_client_seller(api_client, seller_user):
    api_client.force_authenticate(user=seller_user)
    return api_client

@pytest.fixture
def refresh_token(buyer_user):
    return RefreshToken.for_user(buyer_user)

@pytest.fixture
def buyer_user_serializer(buyer_user_profile):
    return BuyerUserProfileSerializer(instance=buyer_user_profile)

@pytest.fixture
def seller_user_serializer(seller_user_profile):
    return SellerUserProfileSerializer(instance=seller_user_profile)
