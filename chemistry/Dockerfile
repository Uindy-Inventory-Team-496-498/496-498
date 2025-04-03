# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3-slim

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install required system packages
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    gcc \
    default-mysql-client \
    netcat-openbsd \
    curl && \
    curl -fsSL https://deb.nodesource.com/setup_19.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY . /app

# Set the working directory for Tailwind CSS
WORKDIR /app/chemistry_system/static_src

# Copy the package.json and package-lock.json files
COPY chemistry_system/static_src/package.json chemistry_system/static_src/package-lock.json ./

# Install Node.js dependencies + DaisyUI
RUN npm install && \
    npm install daisyui && \
    npm install htmx.org@2.0.2

# Build the Tailwind CSS
RUN npm run build

WORKDIR /app
RUN SECRET_KEY=nothing python manage.py tailwind install --no-input && \
    SECRET_KEY=nothing python manage.py tailwind build --no-input && \
    SECRET_KEY=nothing python manage.py collectstatic --no-input

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Entrypoint to run migrations and load fixture data
CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && gunicorn --bind 0.0.0.0:8000 web_project.wsgi"]