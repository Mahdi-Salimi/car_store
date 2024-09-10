import pytest
from django.urls import reverse
from rest_framework import status
from products.tests.fixtures.conftest import *

@pytest.mark.django_db
def test_car_list_unauthenticated(api_client):
    url = reverse('car-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_car_list_authenticated(api_client, seller_user):
    api_client.force_authenticate(user=seller_user)
    url = reverse('car-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

# @pytest.mark.django_db
# def test_car_create_authenticated(api_client, seller_user):
#     api_client.force_authenticate(user=seller_user)
#     url = reverse('car-list')
#
#     data = {
#         "title": "New Test Car",
#         "description": "Description for new test car",
#         "price": 12000,
#         "year": 2021,
#         "mileage": 1000,
#         "location": "San Francisco"
#     }
#     response = api_client.post(url, data, format='json')
#     assert response.status_code == status.HTTP_201_CREATED
#     assert response.data['title'] == data['title']
#
#     car_id = response.data['id']
#     image_data = {
#         "car": car_id,
#         "image_url": "http://example.com/image1.jpg"
#     }
#     image_url = reverse('carimage-list')
#     image_response = api_client.post(image_url, image_data, format='json')
#     assert image_response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_car_detail(api_client, seller_user, car_instance):
    api_client.force_authenticate(user=seller_user)
    url = reverse('car-detail', args=[car_instance.id])
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == car_instance.title

@pytest.mark.django_db
def test_car_update_not_super_user(api_client, seller_user, car_instance):
    api_client.force_authenticate(user=seller_user)
    url = reverse('car-detail', args=[car_instance.id])
    data = {
        "title": "Updated Car Title"
    }
    response = api_client.patch(url, data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_car_delet_not_super_user(api_client, seller_user, car_instance):
    api_client.force_authenticate(user=seller_user)
    url = reverse('car-detail', args=[car_instance.id])
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN



@pytest.mark.django_db
def test_car_image_list_authenticated(api_client, seller_user, car_instance):
    api_client.force_authenticate(user=seller_user)
    url = reverse('carimage-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_car_image_detail(api_client, seller_user, car_image_instance):
    api_client.force_authenticate(user=seller_user)
    url = reverse('carimage-detail', args=[car_image_instance.id])
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['image_url'] == car_image_instance.image_url
