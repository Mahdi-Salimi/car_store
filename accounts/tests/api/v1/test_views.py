import pytest

from django.urls import reverse

from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch

from accounts.tests.fixtures.fixtures_data import api_client, buyer_user, seller_user, create_user, auth_client, refresh_token, auth_client_seller
from accounts.models import BuyerUserProfile

@pytest.mark.django_db
def test_register_view_success(api_client):
    url = reverse('register')
    data = {
        'email': 'newuser@example.com',
        'password': 'newpassword',
        'user_type': 'b'
    }
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert 'access_token' in response.data
    assert 'refresh_token' in response.data

@pytest.mark.django_db
def test_register_view_missing_field(api_client):
    url = reverse('register')
    data = {
        'email': 'newuser@example.com',
        'user_type': 'b'
    }
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_register_view_duplicate_email(api_client, buyer_user):
    url = reverse('register')
    data = {
        'email': buyer_user.email,
        'password': 'newpassword',
        'user_type': 'b'
    }
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_login_view_success(api_client, buyer_user):
    url = reverse('login')
    data = {
        'email': buyer_user.email,
        'password': 'password123@#QW'
    }
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_200_OK
    assert 'token' in response.data

@pytest.mark.django_db
def test_login_view_invalid_credentials(api_client, buyer_user):
    url = reverse('login')
    data = {
        'email': buyer_user.email,
        'password': 'wrongpassword'
    }
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert 'token' not in response.data

@pytest.mark.django_db
def test_login_view_missing_field(api_client):
    url = reverse('login')
    data = {
        'email': 'buyer@example.com',
    }
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_custom_user_detail_view_success(auth_client, buyer_user):
    url = reverse('user-detail')
    response = auth_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['email'] == buyer_user.email

@pytest.mark.django_db
def test_custom_user_detail_view_unauthenticated(api_client):
    url = reverse('user-detail')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_custom_user_detail_view_update_success(auth_client, buyer_user):
    url = reverse('user-detail')
    data = {
        'phone_number': '09123453434'
    }
    response = auth_client.patch(url, data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['phone_number'] == '09123453434'

@pytest.mark.django_db
def test_custom_user_detail_view_update_invalid(auth_client, buyer_user):
    url = reverse('user-detail')
    data = {
        'email': ''
    }
    response = auth_client.patch(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_token_refresh_view_success(api_client, buyer_user):
    url = reverse('token_refresh')
    refresh = RefreshToken.for_user(buyer_user)
    data = {'refresh': str(refresh)}
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data

@pytest.mark.django_db
def test_token_refresh_view_invalid_token(api_client, refresh_token):
    url = reverse('token_refresh')
    data = {'refresh': 'invalidtoken'}
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# @pytest.mark.django_db
# def test_is_owner_permission_success(auth_client, buyer_user, auth_client_seller):
#     url = reverse('buyer-profile')
#
#     response = auth_client.get(url)
#     assert response.status_code == status.HTTP_200_OK
#
#     response = auth_client_seller.get(url)
#     assert response.status_code == status.HTTP_403_FORBIDDEN
#
# @pytest.mark.django_db
# def test_is_owner_permission_forbidden(auth_client, buyer_user, seller_user):
#     url = reverse('seller-profile')
#     auth_client.force_authenticate(user=buyer_user)
#     response = auth_client.get(url)
#     assert response.status_code == status.HTTP_403_FORBIDDEN
