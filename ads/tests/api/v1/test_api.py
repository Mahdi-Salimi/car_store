from django.urls import reverse
from rest_framework import status
from ads.tests.fixtures.conftest import *

from products.models import Car
from ads.models import Ad, Wishlist

def test_create_ad_as_seller(api_client, seller_user, ad_data):
    api_client.force_authenticate(user=seller_user)
    response = api_client.post('/ads/api/v1/ads/', data=ad_data, format='json')
    assert response.status_code == 201
    assert response.data['seller'] == seller_user.id
    assert response.data['car']['title'] == ad_data['car']['title']


def test_create_ad_as_buyer(api_client, buyer_user, ad_data):
    api_client.force_authenticate(user=buyer_user)
    response = api_client.post('/ads/api/v1/ads/', data=ad_data, format='json')

    assert response.status_code == 403


def test_update_ad_as_seller(api_client, seller_user, ad_instance, ad_data):
    api_client.force_authenticate(user=seller_user)

    updated_data = ad_data.copy()
    updated_data['car']['title'] = "Updated Car Title"

    response = api_client.put(f'/ads/api/v1/ads/{ad_instance.id}/', data=updated_data, format='json')
    assert response.status_code == 200
    assert response.data['car']['title'] == "Updated Car Title"


def test_delete_ad_as_seller(api_client, seller_user, ad_instance):
    api_client.force_authenticate(user=seller_user)

    response = api_client.delete(f'/ads/api/v1/ads/{ad_instance.id}/')
    assert response.status_code == 204


def test_update_ad_as_buyer(api_client, buyer_user, ad_instance, ad_data):
    api_client.force_authenticate(user=buyer_user)
    updated_data = ad_data.copy()
    updated_data['car']['title'] = "Updated Car Title"

    response = api_client.put(f'/ads/api/v1/ads/{ad_instance.id}/', data=updated_data, format='json')
    assert response.status_code == 403


def test_delete_ad_as_buyer(api_client, buyer_user, ad_instance):
    api_client.force_authenticate(user=buyer_user)
    response = api_client.delete(f'/ads/api/v1/ads/{ad_instance.id}/')
    assert response.status_code == 403


def test_list_ads(api_client, seller_user):
    api_client.force_authenticate(user=seller_user)
    response = api_client.get('/ads/api/v1/ads/')  # Ensure the correct URL
    assert response.status_code == 200
    assert 'results' in response.data
    assert isinstance(response.data['results'], list)


def test_retrieve_ad(api_client, seller_user, ad_instance):
    api_client.force_authenticate(user=seller_user)
    response = api_client.get(f'/ads/api/v1/ads/{ad_instance.id}/')
    assert response.status_code == 200
    assert response.data['id'] == ad_instance.id


@pytest.mark.django_db
def test_list_ads_with_car_filter(api_client, seller_user):
    api_client.force_authenticate(user=seller_user)
    response = api_client.get('/ads/api/v1/ads/?car__make=Toyota')
    assert response.status_code == 200


@pytest.mark.django_db
def test_list_promoted_ads(api_client, seller_user, promoted_ad_instance, non_promoted_ad_instance):
    api_client.force_authenticate(user=seller_user)
    response = api_client.get('/ads/api/v1/promoted/')
    assert response.status_code == 200
    ads = response.data['results']
    assert all(ad['is_promoted'] for ad in ads), "Non-promoted ads are present in the promoted ads list"

@pytest.mark.django_db
def test_list_ads_by_seller(api_client, seller_user, ad_instance, another_seller_ad_instance):
    api_client.force_authenticate(user=seller_user)
    response = api_client.get('/ads/api/v1/my_ads/')
    assert response.status_code == 200
    ads = response.data['results']
    assert all(ad['seller'] == seller_user.id for ad in ads), "Ads from other sellers are present in the seller's ad list"


@pytest.mark.django_db
def test_filter_ads_by_date(api_client, seller_user):
    api_client.force_authenticate(user=seller_user)
    response = api_client.get('/ads/api/v1/ads/?start_date=2023-01-01&end_date=2023-12-31')
    assert response.status_code == 200


@pytest.mark.django_db
def test_pagination_ads(api_client, seller_user):
    api_client.force_authenticate(user=seller_user)
    response = api_client.get('/ads/api/v1/ads/?page=1&page_size=5')
    assert response.status_code == 200
    assert len(response.data['results']) <= 5

@pytest.mark.django_db
def test_create_ad_invalid_data(api_client, seller_user):
    api_client.force_authenticate(user=seller_user)
    invalid_data = {
        "car": {},
        "is_promoted": False
    }
    response = api_client.post('/ads/api/v1/ads/', data=invalid_data, format='json')
    assert response.status_code == 400
    assert 'car' in response.data

@pytest.mark.django_db
def test_delete_ad_access_control(api_client, seller_user, buyer_user, ad_instance):
    api_client.force_authenticate(user=seller_user)
    response = api_client.delete(f'/ads/api/v1/ads/{ad_instance.id}/')
    assert response.status_code == 204

    api_client.force_authenticate(user=buyer_user)
    response = api_client.delete(f'/ads/api/v1/ads/{ad_instance.id}/')
    assert response.status_code == 403

@pytest.mark.django_db
def test_sort_ads_by_price(api_client, seller_user):
    api_client.force_authenticate(user=seller_user)
    response = api_client.get('/ads/api/v1/ads/?ordering=price')
    assert response.status_code == 200
    ads = response.data['results']
    assert ads == sorted(ads, key=lambda x: x['car']['price'])


@pytest.mark.django_db
def test_add_ad_to_wishlist(api_client, buyer_user, ad_instance):
    api_client.force_authenticate(user=buyer_user)

    response = api_client.post('/ads/api/v1/wishlists/', data={'ad': ad_instance.id}, format='json')
    assert response.status_code == 201
    assert response.data['ad'] == ad_instance.id
    assert response.data['user'] == buyer_user.id


@pytest.mark.django_db
def test_add_ad_to_wishlist_as_seller(api_client, seller_user, ad_instance):
    api_client.force_authenticate(user=seller_user)

    response = api_client.post('/ads/api/v1/wishlists/', data={'ad': ad_instance.id}, format='json')
    assert response.status_code == 403


@pytest.mark.django_db
def test_remove_ad_from_wishlist(api_client, buyer_user, ad_instance):
    api_client.force_authenticate(user=buyer_user)

    # Add an ad to the wishlist first
    wishlist_response = api_client.post('/ads/api/v1/wishlists/', data={'ad': ad_instance.id}, format='json')
    wishlist_id = wishlist_response.data['id']

    # Now remove the ad from the wishlist
    response = api_client.delete(f'/ads/api/v1/wishlists/{wishlist_id}/')
    assert response.status_code == 204


@pytest.mark.django_db
def test_remove_ad_from_wishlist_different_user(api_client, buyer_user, buyer_user2, ad_instance):
    api_client.force_authenticate(user=buyer_user)

    response = api_client.post('/ads/api/v1/wishlists/', data={'ad': ad_instance.id}, format='json')
    assert response.status_code == 201
    wishlist_id = response.data['id']
    response = api_client.get(f'/ads/api/v1/wishlists/{wishlist_id}/')
    assert response.status_code == 200

    api_client.force_authenticate(user=buyer_user2)
    response = api_client.delete(f'/ads/api/v1/wishlists/{wishlist_id}/remove/')
    assert response.status_code == 404



@pytest.mark.django_db
def test_list_wishlist_items(api_client, buyer_user, ad_instance, promoted_ad_instance):
    api_client.force_authenticate(user=buyer_user)

    api_client.post('/ads/api/v1/wishlists/', data={'ad': ad_instance.id}, format='json')
    api_client.post('/ads/api/v1/wishlists/', data={'ad': promoted_ad_instance.id}, format='json')

    response = api_client.get('/ads/api/v1/wishlists/')
    assert response.status_code == 200
    assert len(response.data['results']) == 2
    assert {item['ad'] for item in response.data['results']} == {ad_instance.id, promoted_ad_instance.id}


@pytest.mark.django_db
def test_cannot_add_same_ad_twice_to_wishlist(api_client, buyer_user, ad_instance):
    api_client.force_authenticate(user=buyer_user)

    api_client.post('/ads/api/v1/wishlists/', data={'ad': ad_instance.id}, format='json')
    response = api_client.post('/ads/api/v1/wishlists/', data={'ad': ad_instance.id}, format='json')

    assert response.status_code == 400
    assert 'ad' in response.data