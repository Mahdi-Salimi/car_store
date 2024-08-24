import pytest
from django.contrib.auth import get_user_model
from accounts.models import BuyerUserProfile, SellerUserProfile

User = get_user_model()

@pytest.fixture
def buyer_user_profile():
    user = User.objects.create_user(
        email='buyer@example.com',
        password='password123',
        user_type=User.UserType.BUYER
    )
    return BuyerUserProfile.objects.create(
        user=user,
    )

@pytest.fixture
def seller_user_profile():
    user = User.objects.create_user(
        email='seller@example.com',
        password='password123',
        user_type=User.UserType.SELLER
    )
    # Additional fields for SellerUserProfile
    return SellerUserProfile.objects.create(
        user=user,
        company_name='Test Cars Ltd.',
        website='http://testcars.com',
        rating=4.5,
        total_sales=100
    )
