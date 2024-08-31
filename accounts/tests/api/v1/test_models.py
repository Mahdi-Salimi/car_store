import pytest

from django.contrib.auth import get_user_model

from accounts.tests.fixtures.fixtures_data import seller_user, buyer_user, buyer_user_profile, seller_user_profile, create_user
from accounts.models import BuyerUserProfile, SellerUserProfile

User = get_user_model()


@pytest.mark.django_db
def test_buyer_user_profile_creation(buyer_user_profile):

    user = buyer_user_profile.user

    assert user.email == 'buyer_unique@example.com'
    assert user.user_type == User.UserType.BUYER
    assert hasattr(buyer_user_profile, 'user')
    assert isinstance(buyer_user_profile.user, User)

    assert BuyerUserProfile.objects.filter(user=user).exists()
    assert buyer_user_profile.pk is not None




@pytest.mark.django_db
def test_seller_user_profile_creation(seller_user_profile):
    user = seller_user_profile.user

    assert user.email == 'seller_unique@example.com'
    assert user.user_type == User.UserType.SELLER
    assert hasattr(seller_user_profile, 'user')
    assert isinstance(seller_user_profile.user, User)

    assert SellerUserProfile.objects.filter(user=user).exists()
    assert seller_user_profile.pk is not None



@pytest.mark.django_db
def test_signal_creates_buyer_profile(buyer_user):

    assert BuyerUserProfile.objects.filter(user=buyer_user).exists()

    profile = BuyerUserProfile.objects.get(user=buyer_user)
    assert profile.user == buyer_user


@pytest.mark.django_db
def test_signal_creates_seller_profile(seller_user):

    assert SellerUserProfile.objects.filter(user=seller_user).exists()
    profile = SellerUserProfile.objects.get(user=seller_user)
    assert profile.user == seller_user
