import pytest
import aiohttp
import asyncio
from unittest.mock import AsyncMock, patch
from asgiref.sync import sync_to_async
from products.models import Car

@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_session():
    with patch('aiohttp.ClientSession.get', new_callable=AsyncMock) as mock_get:
        yield mock_get

@pytest.fixture
def car_data():
    car = Car.objects.create(
        url='https://example.com/car1',
        title='Test Car',
        time=timezone.now(),
        year=2020,
        mileage=10000,
        location='Test Location',
        description='A test car',
        image='https://example.com/image.jpg',
        price=20000
    )
    yield car
    car.delete()
