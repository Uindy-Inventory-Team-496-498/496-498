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
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd --create-home appuser

# Set the working directory for the application
WORKDIR /app

# Copy requirements and install Python dependencies
COPY --chown=appuser:appuser requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY --chown=appuser:appuser . /app

# Set the working directory for Tailwind CSS
WORKDIR /app/chemistry_system/static_src

# Copy the package.json and package-lock.json files
COPY --chown=appuser:appuser chemistry_system/static_src/package.json chemistry_system/static_src/package-lock.json ./

# Install Node.js dependencies locally
RUN npm install

# Return to the application root directory
WORKDIR /app

# Run Django-Tailwind commands
RUN SECRET_KEY=nothing python manage.py tailwind install --no-input
RUN SECRET_KEY=nothing python manage.py tailwind build --no-input
RUN SECRET_KEY=nothing python manage.py collectstatic --no-input

# Switch to the non-root user
USER appuser

# Entrypoint to run migrations and start the server
CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && gunicorn --bind 0.0.0.0:8000 web_project.wsgi"]