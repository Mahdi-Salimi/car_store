FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libmariadb-dev-compat \
    libmariadb-dev \
    cron \
    libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt --verbose

COPY . /app/

COPY .env /app/.env

COPY ./crontab /etc/cron.d/crawler-cron

RUN chmod 0644 /etc/cron.d/crawler-cron

RUN crontab /etc/cron.d/crawler-cron

RUN touch /var/log/cron.log

EXPOSE 8000

CMD cron && tail -f /var/log/cron.log
