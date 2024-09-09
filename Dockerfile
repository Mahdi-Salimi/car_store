# Use official Python image as a base
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libmariadb-dev-compat \
    libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy the project requirements
COPY ./requirements.txt /app/requirements.txt

# Install project dependencies with increased verbosity
RUN pip install --no-cache-dir -r requirements.txt --verbose

# Copy the Django project files to the working directory
COPY . /app/

# Copy the environment file
COPY .env /app/.env

# Expose the port for the application
EXPOSE 8000

# Start Django application
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
