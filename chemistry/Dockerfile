# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3-slim

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install required system packages for MySQL client
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    gcc \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y netcat-openbsd

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Entrypoint to run migrations and load fixture data
CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py migrate && python manage.py loaddata chemistry_system/fixtures/chemistry_system_fixtures.json && gunicorn --bind 0.0.0.0:8000 web_project.wsgi"]