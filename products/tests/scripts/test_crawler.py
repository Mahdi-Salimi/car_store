import pytest
import asyncio
import aiohttp

from datetime import datetime
from aioresponses import aioresponses
from asgiref.sync import sync_to_async

from products.models import Car
from products.scripts.bama_crawler import parse_mileage, parse_price, parse_time, fetch_data, fetch_all_data, insert_data


@pytest.mark.asyncio
async def test_fetch_data():
    url = 'https://bama.ir/cad/api/search?pageIndex=1'
    sem = asyncio.Semaphore(1)

    # Mock aiohttp response
    with aioresponses() as m:
        m.get(url, payload={
            'data': {
                'ads': [{
                    'detail': {
                        'url': '/car-details',
                        'title': 'Car 1',
                        'time': 'لحظاتی پیش',
                        'year': 2020,
                        'mileage': '10,000 km',
                        'location': 'Tehran',
                        'description': 'Nice car',
                        'image': 'image-url',
                        'modified_date': '2023-09-10'
                    },
                    'price': {
                        'price': '1,200,000'
                    }
                }]
            }
        })

        async with aiohttp.ClientSession() as session:
            url, cars = await fetch_data(sem, session, url)

    assert url == 'https://bama.ir/cad/api/search?pageIndex=1'
    assert len(cars) == 1
    assert cars[0]['title'] == 'Car 1'
    assert cars[0]['price'] == '1,200,000'


@pytest.mark.asyncio
async def test_fetch_all_data():
    urls = ['https://bama.ir/cad/api/search?pageIndex=1']
    sem = asyncio.Semaphore(1)

    with aioresponses() as m:
        m.get(urls[0], payload={
            'data': {
                'ads': [{
                    'detail': {
                        'url': '/car-details',
                        'title': 'Car 1',
                        'time': 'لحظاتی پیش',
                        'year': 2020,
                        'mileage': '10,000 km',
                        'location': 'Tehran',
                        'description': 'Nice car',
                        'image': 'image-url',
                        'modified_date': '2023-09-10'
                    },
                    'price': {
                        'price': '1,200,000'
                    }
                }]
            }
        })

        results = await fetch_all_data(sem, urls)

    assert len(results) == 1
    url, cars = results[0]
    assert len(cars) == 1
    assert cars[0]['title'] == 'Car 1'

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_insert_data(mocker):
    car_data = [{
        'url': 'https://bama.ir/car-details',
        'title': 'Car 1',
        'time': '2023-09-10 15:30',
        'year': 2020,
        'mileage': '10,000 km',
        'location': 'Tehran',
        'description': 'Nice car',
        'image': 'image-url',
        'price': '1,200,000'
    }]

    results = [('https://bama.ir/cad/api/search?pageIndex=1', car_data)]

    mocker.patch('products.models.Car.objects.create')
    mocker.patch('products.models.Car.objects.filter').return_value.exists.return_value = False

    await insert_data(results)

    Car.objects.create.assert_called_once_with(
        url=car_data[0]['url'],
        title=car_data[0]['title'],
        time=mocker.ANY,
        year=car_data[0]['year'],
        mileage=10000,
        location=car_data[0]['location'],
        description=car_data[0]['description'],
        image=car_data[0]['image'],
        price=1200000
    )