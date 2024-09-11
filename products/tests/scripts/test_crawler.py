import pytest
import aiohttp
import asyncio

from asgiref.sync import sync_to_async

from django.utils import datetime

from products.tests.fixtures.crawler_conftest import *
from products.models import Car
from products.scripts.bama_crawler import parse_mileage, parse_time, parse_price, fetch_data, insert_data, main


def test_parse_mileage():
    assert parse_mileage('12,000 km') == 12000.0
    assert parse_mileage('unknown') is None
    assert parse_mileage('') is None


def test_parse_price():
    assert parse_price('20,000') == 20000.0
    assert parse_price('price: unknown') is None


def test_parse_time():
    assert isinstance(parse_time('لحظاتی پیش'), datetime)
    assert isinstance(parse_time('2023-09-01T10:00:00'), datetime)


@pytest.mark.asyncio
async def test_fetch_data(mock_session):
    url = 'https://example.com/api/cars'

    mock_response = {
        "data": {
            "ads": [{
                "detail": {
                    "url": "https://example.com/car1",
                    "title": "Test Car",
                    "time": "2023-09-01T10:00:00",
                    "year": 2020,
                    "mileage": "10000 km",
                    "location": "Test Location",
                    "description": "A test car",
                    "image": "https://example.com/image.jpg",
                    "modified_date": "2023-09-02"
                },
                "price": {
                    "price": "20,000"
                }
            }]
        }
    }

    mock_session.return_value.__aenter__.return_value.status = 200
    mock_session.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)

    sem = asyncio.Semaphore(1)
    async with aiohttp.ClientSession() as session:
        url, cars = await fetch_data(sem, session, url)

    assert len(cars) == 1
    assert cars[0]['title'] == 'Test Car'
    assert cars[0]['price'] == '20,000'


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_insert_data(car_data):
    results = [('https://example.com/api/cars', [{
        "url": "https://example.com/car2",
        "title": "New Test Car",
        "time": "2023-09-01T10:00:00",
        "year": 2020,
        "mileage": "15000 km",
        "location": "New Test Location",
        "description": "A new test car",
        "image": "https://example.com/image2.jpg",
        "price": "30,000"
    }])]

    await insert_data(results)

    new_car = await sync_to_async(Car.objects.get)(url="https://example.com/car2")
    assert new_car.title == "New Test Car"
    assert new_car.mileage == 15000
    assert new_car.price == 30000


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_main(mock_session):
    mock_response = {
        "data": {
            "ads": [{
                "detail": {
                    "url": "https://example.com/car1",
                    "title": "Test Car",
                    "time": "2023-09-01T10:00:00",
                    "year": 2020,
                    "mileage": "10000 km",
                    "location": "Test Location",
                    "description": "A test car",
                    "image": "https://example.com/image.jpg",
                    "modified_date": "2023-09-02"
                },
                "price": {
                    "price": "20,000"
                }
            }]
        }
    }

    mock_session.return_value.__aenter__.return_value.status = 200
    mock_session.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)

    sem_limit = 1
    page_range = 1
    await main(page_range, sem_limit)

    car = await sync_to_async(Car.objects.get)(url="https://example.com/car1")
    assert car.title == "Test Car"
    assert car.price == 20000
