import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from payment.models import Payment
from payment.tests.fixtures.conftest import *


@pytest.mark.django_db
def test_create_payment(user, ad):
    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse('payment-list-create')
    data = {
        "user": user.id,
        "ad": ad.id,
        "amount": 500,
        "is_successful": True,
        "transaction_id": "abc123"
    }
    response = client.post(url, data, format='json')

    assert response.status_code == 201, f"Expected 201 but got {response.status_code} with {response.data}"
    assert Payment.objects.count() == 1


@pytest.mark.django_db
def test_get_payment_list(user):
    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse('payment-list-create')
    response = client.get(url)

    assert response.status_code == 200, f"Expected 200 but got {response.status_code}"


@pytest.mark.django_db
def test_update_payment(user, payment):
    client = APIClient()
    client.force_authenticate(user=user)
    assert payment.ad.seller == user, "The user must be the seller of the ad"

    url = reverse('payment-detail', args=[payment.id])
    data = {
        "amount": 500,
    }

    response = client.patch(url, data, format='json')

    assert response.status_code == 200, f"Expected 200 but got {response.status_code} with {response.data}"
    payment.refresh_from_db()
    assert payment.amount == 500


@pytest.mark.django_db
def test_delete_payment(user, payment):
    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse('payment-detail', args=[payment.id])
    response = client.delete(url)

    assert response.status_code == 204, f"Expected 204 but got {response.status_code} with {response.data}"
    assert Payment.objects.count() == 0
