import pytest

from django.contrib.auth import get_user_model

from accounts.models import BuyerUserProfile, SellerUserProfile
from accounts.api.v1.serializers import BuyerUserProfileSerializer, SellerUserProfileSerializer, CustomUserSerializer

User = get_user_model()

@pytest.fixture
def buyer_user():
    return User.objects.create_user(
        email='buyer@example.com',
        password='password123',
        user_type=User.UserType.BUYER
    )

@pytest.fixture
def seller_user():
    return User.objects.create_user(
        email='seller@example.com',
        password='password123',
        user_type=User.UserType.SELLER
    )

@pytest.fixture
def buyer_user_profile(buyer_user):
    profile = BuyerUserProfile.objects.get(user=buyer_user)
    profile.save()
    return profile

@pytest.fixture
def seller_user_profile(seller_user):
    profile = SellerUserProfile.objects.get(user=seller_user)
    profile.company_name = 'Test Cars Ltd.'
    profile.website = 'http://testcars.com'
    profile.rating = 4.5
    profile.total_sales = 100
    profile.save()
    return profile

# serializers fixtures

@pytest.fixture
def buyer_user_serializer():
    user = User.objects.create_user(
        email='buyer@example.com',
        password='password123',
        user_type=User.UserType.BUYER
    )
    profile = BuyerUserProfile.objects.get(user=user)
    return BuyerUserProfileSerializer(instance=profile)

@pytest.fixture
def seller_user_serializer():
    user = User.objects.create_user(
        email='seller@example.com',
        password='password123',
        user_type=User.UserType.SELLER
    )
    profile = SellerUserProfile.objects.get(user=user)
    profile.company_name = 'Test Cars Ltd.'
    profile.website = 'http://testcars.com'
    profile.rating = 4.5
    profile.total_sales = 100
    profile.save()
    return SellerUserProfileSerializer(instance=profile)

@pytest.fixture
def custom_user_serializer():
    buyer_user = User.objects.create_user(
        email='buyer_custom@example.com',
        password='password123',
        user_type=User.UserType.BUYER
    )
    seller_user = User.objects.create_user(
        email='seller_custom@example.com',
        password='password123',
        user_type=User.UserType.SELLER
    )
    return CustomUserSerializer(instance=buyer_user), CustomUserSerializer(instance=seller_user)

