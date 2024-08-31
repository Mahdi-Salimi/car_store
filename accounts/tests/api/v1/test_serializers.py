import pytest

from accounts.tests.fixtures.fixtures_data import (
    buyer_user_serializer,
    seller_user_serializer,
    seller_user_profile,
    buyer_user_profile,
    buyer_user,
    seller_user,
    create_user,
)

@pytest.mark.django_db
def test_buyer_profile_serializer(buyer_user_serializer):
    data = buyer_user_serializer.data
    assert data['user']['email'] == 'buyer_unique@example.com'
    assert data['user']['user_type'] == 'b'

@pytest.mark.django_db
def test_seller_profile_serializer(seller_user_serializer):
    data = seller_user_serializer.data
    assert data['user']['email'] == 'seller_unique@example.com'
    assert data['user']['user_type'] == 's'


