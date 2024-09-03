import asyncio
from django.core.management.base import BaseCommand
from products.scripts.bama_crawler import main

class Command(BaseCommand):
    help = "Run the car crawler"

    def add_arguments(self, parser):
        parser.add_argument(
            '--range',
            type=int,
            default=10,
            help="Specify the range of pages to crawl. Defaults to 10."
        )
        parser.add_argument(
            '--sem',
            type=int,
            default=5,
            help="Specify the semaphore limit for concurrent requests. Defaults to 5."
        )

    def handle(self, *args, **options):
        page_range = options['range']
        sem_limit = options['sem']
        asyncio.run(main(page_range, sem_limit))
        self.stdout.write(self.style.SUCCESS(f'Successfully ran the crawler for {page_range} pages with a semaphore limit of {sem_limit}'))
