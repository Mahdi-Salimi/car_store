import pytest

from django.contrib.auth import get_user_model

from accounts.tests.fixtures.fixtures_data import buyer_user_profile, seller_user_profile


User = get_user_model()


@pytest.mark.django_db
def test_buyer_user_profile_creation(buyer_user_profile):

    user = buyer_user_profile.user

    assert user.email == 'buyer@example.com'
    assert user.user_type == User.UserType.BUYER
    assert hasattr(buyer_user_profile, 'user')
    assert isinstance(buyer_user_profile.user, User)


@pytest.mark.django_db
def test_seller_user_profile_creation(seller_user_profile):
    user = seller_user_profile.user

    assert user.email == 'seller@example.com'
    assert user.user_type == User.UserType.SELLER
    assert hasattr(seller_user_profile, 'user')
    assert isinstance(seller_user_profile.user, User)

    assert seller_user_profile.company_name == 'Test Cars Ltd.'
    assert seller_user_profile.website == 'http://testcars.com'
    assert seller_user_profile.rating == 4.5
    assert seller_user_profile.total_sales == 100
