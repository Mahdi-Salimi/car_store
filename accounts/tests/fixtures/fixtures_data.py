import pytest

from django.contrib.auth import get_user_model

from accounts.models import BuyerUserProfile, SellerUserProfile

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
