from django.urls import reverse
from rest_framework import status
from ads.tests.fixtures.conftest import *

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


@pytest.mark.django_db
def test_list_ads_with_car_filter(api_client, seller_user):
    api_client.force_authenticate(user=seller_user)
    response = api_client.get('/ads/api/v1/?car__make=Toyota')
    assert response.status_code == 200


# @pytest.mark.django_db
# def test_list_promoted_ads(api_client, seller_user, promoted_ad_instance, non_promoted_ad_instance):
#     api_client.force_authenticate(user=seller_user)
#     response = api_client.get('/ads/api/v1/promoted/')
#     assert response.status_code == 200
#     ads = response.data['results']
#     assert all(ad['is_promoted'] for ad in ads), "Non-promoted ads are present in the promoted ads list"
#
# @pytest.mark.django_db
# def test_list_ads_by_seller(api_client, seller_user, ad_instance, another_seller_ad_instance):
#     api_client.force_authenticate(user=seller_user)
#     response = api_client.get('/ads/api/v1/my_ads/')
#     assert response.status_code == 200
#     ads = response.data['results']
#     assert all(ad['seller'] == seller_user.id for ad in ads), "Ads from other sellers are present in the seller's ad list"


@pytest.mark.django_db
def test_filter_ads_by_date(api_client, seller_user):
    api_client.force_authenticate(user=seller_user)
    response = api_client.get('/ads/api/v1/?start_date=2023-01-01&end_date=2023-12-31')
    assert response.status_code == 200


# @pytest.mark.django_db
# def test_filter_ads_by_payment_status(api_client, seller_user, ad_instance, promoted_ad_instance):
#     api_client.force_authenticate(user=seller_user)
#     response = api_client.get('/ads/api/v1/?payment_status=pending')
#     assert response.status_code == 200
#     ads = response.data['results']
#     assert all(ad['payment_status'] == 'pending' for ad in ads), "Non-pending ads are present in the filtered ads list"


@pytest.mark.django_db
def test_pagination_ads(api_client, seller_user):
    api_client.force_authenticate(user=seller_user)
    response = api_client.get('/ads/api/v1/?page=1&page_size=5')
    assert response.status_code == 200
    assert len(response.data['results']) <= 5

@pytest.mark.django_db
def test_create_ad_invalid_data(api_client, seller_user):
    api_client.force_authenticate(user=seller_user)
    invalid_data = {
        "car": {},
        "is_promoted": False
    }
    response = api_client.post('/ads/api/v1/', data=invalid_data, format='json')
    assert response.status_code == 400
    assert 'car' in response.data

@pytest.mark.django_db
def test_delete_ad_access_control(api_client, seller_user, buyer_user, ad_instance):
    api_client.force_authenticate(user=seller_user)
    response = api_client.delete(f'/ads/api/v1/{ad_instance.id}/')
    assert response.status_code == 204

    api_client.force_authenticate(user=buyer_user)
    response = api_client.delete(f'/ads/api/v1/{ad_instance.id}/')
    assert response.status_code == 403

@pytest.mark.django_db
def test_sort_ads_by_price(api_client, seller_user):
    api_client.force_authenticate(user=seller_user)
    response = api_client.get('/ads/api/v1/?ordering=price')
    assert response.status_code == 200
    ads = response.data['results']
    assert ads == sorted(ads, key=lambda x: x['car']['price'])