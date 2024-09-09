Here’s the entire README.md content in a single tab, formatted for easy copying:

# Car Store Project

This project is an e-commerce platform for car sellers and buyers, built using Django and Docker. The system has a web application, a background worker for tasks using Celery, and a crawler microservice for scraping data.

## Features

- **User Accounts**: Buyers and sellers can register, login, and manage their profiles.
- **Car Listings**: Sellers can post cars for sale, and buyers can browse available cars.
- **Advertisement Management**: Sellers can promote their ads for better visibility.
- **Asynchronous Tasks**: Celery is used for background tasks, such as sending emails.
- **Crawler**: A microservice that scrapes data using the Django management command `crawler`.

## Prerequisites

- **Docker**: Ensure Docker and Docker Compose are installed on your system.
- **Environment Variables**: You need to create a `.env` file in the root of your project with the following content:

```env
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_DATABASE=your_database_name
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

## Project Structure

├── app/
│   ├── accounts/         # User account management
│   ├── ads/              # Advertisements module
│   ├── products/         # Products app (Car listings, car details, etc.)
│   │   └── scripts/      # Crawler scripts
│   └── manage.py         # Django management script
├── Dockerfile            # Docker build instructions for the web and crawler services
├── docker-compose.yml    # Docker Compose setup
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables file (to be created)

## Setup and Installation

Clone the repository:
bash
Copy code
git clone https://github.com/Mahdi-Salimi/car-store.git
cd car-store
Create the .env file:
Create a .env file in the root directory of your project and define the following variables:

```env
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_DATABASE=your_database_name
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
Build and run the services:
Run the following command to build and start your Docker containers:
```

```
docker-compose up --build
```
This will start:
MySQL: The database service.
Web: The Django application running the web interface.
Redis: A message broker used by Celery.
Celery: Background worker for handling asynchronous tasks.
Crawler: A service to run the crawler script.
Apply Migrations:
Once the services are running, open another terminal window and apply the migrations:

```
docker-compose exec web python3 manage.py makemigrations
docker-compose exec web python3 manage.py migrate
```
### Create a Superuser (optional):
If you want to access the Django admin, create a superuser:
```
docker-compose exec web python3 manage.py createsuperuser
```
### Run the Crawler:
The crawler script can be executed as a standalone service or via the management command:
```
docker-compose exec crawler python3 manage.py crawler
```
### Running Tests

To run tests using pytest:
```
docker-compose exec web pytest
```
### Celery

To check the status of the Celery worker, ensure it's running via Docker Compose:

```
docker-compose logs celery
```
You can also run specific tasks using Celery from your Django code.

## Technologies Used

Django: Backend framework
MySQL: Relational database
Redis: Message broker for Celery
Celery: Task queue for handling background tasks
Docker: Containerization of the services
Docker Compose: Orchestration tool for managing multi-container applications
## License

This project is licensed under the MIT License. See the LICENSE file for details.

## FAQ

How can I run the project locally without Docker?
Install Python 3.10+, MySQL, and Redis locally. Install the Python dependencies using:

```
pip install -r requirements.txt
```
Then, run the Django server locally:
```
python manage.py runserver
```
### How do I scale the Celery workers?
You can scale Celery workers by adding more worker instances in the docker-compose.yml file:
```
celery_worker_2:
  build:
    context: .
  container_name: celery_worker_2
  command: celery -A car_store worker --loglevel=info
  depends_on:
    redis:
      condition: service_healthy
  env_file:
    - .env
  networks:
    - app-network
```