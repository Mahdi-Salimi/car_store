import aiohttp
import asyncio
import time
import logging
import os
import django
import re

from datetime import datetime, timedelta
from django.utils import timezone
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta
from asgiref.sync import sync_to_async

from products.models import Car

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_mileage(mileage_str):
    try:
        numeric_part = re.sub(r'[^\d.]', '', mileage_str)
        return float(numeric_part)
    except (ValueError, TypeError):
        return None

def parse_time(time_str):
    now = datetime.utcnow()
    if 'لحظاتی پیش' in time_str:
        return now
    try:
        return date_parser.parse(time_str)
    except ValueError:
        return now


def parse_price(price_str):
    try:
        numeric_part = price_str.replace(',', '')
        return float(numeric_part)
    except (ValueError, TypeError):
        return None


def extract_car_json_data(response_json):
    cars = []
    ads = response_json.get('data', {}).get('ads', [])
    for ad in ads:
        car = ad.get('detail', {})
        detail_keys = ['url', 'title', 'time', 'year', 'mileage', 'location', 'description', 'image', 'modified_date']

        values = {key: car.get(key) for key in detail_keys}
        price = ad.get('price', {}).get('price')
        values['price'] = price
        values['url'] = 'https://bama.ir' + values['url']
        cars.append(values)
    return cars



async def fetch_data(sem, session, url):
    async with sem:
        try:
            logger.info(f"Fetching data from {url}")
            start_time = time.time()
            async with session.get(url, headers=None, ssl=False) as response:
                logger.info(f"Response status for {url}: {response.status}")

                if response.status == 200:
                    response_json = await response.json()
                    cars = extract_car_json_data(response_json)
                    end_time = time.time()
                    logger.info(f"Fetched {len(cars)} cars from {url} in {end_time - start_time:.2f} seconds")
                    return url, cars
                else:
                    logger.error(f"Unexpected response status {response.status} for {url}")
                    return url, []
        except aiohttp.ClientError as e:
            logger.error(f"Client error fetching data from {url}: {e}")
            return url, []
        except asyncio.TimeoutError as e:
            logger.error(f"Timeout error fetching data from {url}: {e}")
            return url, []
        except Exception as e:
            logger.error(f"Unexpected error fetching data from {url}: {e}")
            return url, []


async def fetch_all_data(sem, urls):
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(fetch_data(sem, session, url)) for url in urls]
        logger.info("Starting gather")
        start_time = time.time()
        try:
            results = await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Exception during gather: {e}")
            results = []
        end_time = time.time()
        logger.info(f"Completed gather in {end_time - start_time:.2f} seconds")
        return results


async def insert_data(results):
    insert_count = 0
    start_time = time.time()

    async def insert_car_data(car_data):
        nonlocal insert_count
        try:
            if isinstance(car_data['time'], str):
                car_data['time'] = parse_time(car_data['time'])
            else:
                car_data['time'] = datetime.utcnow()

            car_data['time'] = timezone.make_aware(car_data['time'], timezone.get_default_timezone())

            car_data['mileage'] = parse_mileage(car_data.get('mileage', ''))
            car_data['price'] = parse_price(car_data.get('price', ''))

            exists = await sync_to_async(lambda: Car.objects.filter(
                url=car_data['url'],
                title=car_data['title'],
                year=car_data['year'],
                price=car_data['price']).exists())()

            if not exists:
                await sync_to_async(Car.objects.create)(
                    url=car_data['url'],
                    title=car_data['title'],
                    time=car_data['time'],
                    year=car_data['year'],
                    mileage=car_data.get('mileage'),
                    location=car_data.get('location'),
                    description=car_data.get('description', ''),
                    image=car_data.get('image'),
                    price=car_data.get('price'),
                )
                insert_count += 1
                logger.info(f"Added new car: {car_data['title']}")
            else:
                logger.info(f"Car already exists: {car_data['title']}")
        except Exception as e:
            logger.error(f"Failed to insert data for {car_data['title']}: {e}")

    tasks = [insert_car_data(car_data) for _, cars in results for car_data in cars]
    await asyncio.gather(*tasks)

    end_time = time.time()
    logger.info(f"Inserted {insert_count} records into the database in {end_time - start_time:.2f} seconds.")




async def main(page_range, sem_limit):
    sem = asyncio.Semaphore(sem_limit)
    urls = [f'https://bama.ir/cad/api/search?pageIndex={i}' for i in range(page_range)]
    results = await fetch_all_data(sem, urls)
    await insert_data(results)
