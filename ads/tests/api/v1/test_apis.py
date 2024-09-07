from django.urls import reverse
from rest_framework import status
from ads.tests.fixtures.fixtures_data import *

from products.models import Car
from ads.models import Ad

def test_create_ad_as_seller(api_client, seller_user, ad_data):
    api_client.force_authenticate(user=seller_user)
    response = api_client.post('/ads/api/v1/', data=ad_data, format='json')
    assert response.status_code == 201
    assert response.data['seller'] == seller_user.id
    assert response.data['car']['title'] == ad_data['car']['title']


def test_create_ad_as_buyer(api_client, buyer_user, ad_data):
    api_client.force_authenticate(user=buyer_user)
    response = api_client.post('/ads/api/v1/', data=ad_data, format='json')

    assert response.status_code == 403


def test_update_ad_as_seller(api_client, seller_user, ad_instance, ad_data):
    api_client.force_authenticate(user=seller_user)

    updated_data = ad_data.copy()
    updated_data['car']['title'] = "Updated Car Title"

    response = api_client.put(f'/ads/api/v1/{ad_instance.id}/', data=updated_data, format='json')
    assert response.status_code == 200
    assert response.data['car']['title'] == "Updated Car Title"


def test_delete_ad_as_seller(api_client, seller_user, ad_instance):
    api_client.force_authenticate(user=seller_user)

    response = api_client.delete(f'/ads/api/v1/{ad_instance.id}/')
    assert response.status_code == 204


def test_update_ad_as_buyer(api_client, buyer_user, ad_instance, ad_data):
    api_client.force_authenticate(user=buyer_user)
    updated_data = ad_data.copy()
    updated_data['car']['title'] = "Updated Car Title"

    response = api_client.put(f'/ads/api/v1/{ad_instance.id}/', data=updated_data, format='json')
    assert response.status_code == 403


def test_delete_ad_as_buyer(api_client, buyer_user, ad_instance):
    api_client.force_authenticate(user=buyer_user)
    response = api_client.delete(f'/ads/api/v1/{ad_instance.id}/')
    assert response.status_code == 403


def test_list_ads(api_client, seller_user):
    api_client.force_authenticate(user=seller_user)
    response = api_client.get('/ads/api/v1/')  # Ensure the correct URL
    assert response.status_code == 200
    assert 'results' in response.data
    assert isinstance(response.data['results'], list)


def test_retrieve_ad(api_client, seller_user, ad_instance):
    api_client.force_authenticate(user=seller_user)
    response = api_client.get(f'/ads/api/v1/{ad_instance.id}/')
    assert response.status_code == 200
    assert response.data['id'] == ad_instance.id
