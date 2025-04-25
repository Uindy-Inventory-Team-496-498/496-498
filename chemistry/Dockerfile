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

# Set the working directory for the application
WORKDIR /app
COPY . /app

# Set the working directory for Tailwind CSS
WORKDIR /app/chemistry_system/static_src

# Copy the package.json and package-lock.json files
COPY chemistry_system/static_src/package.json chemistry_system/static_src/package-lock.json ./

# Install Node.js dependencies locally
RUN npm install

# Return to the application root directory
WORKDIR /app

# Run Django-Tailwind commands to install and build Tailwind CSS
RUN SECRET_KEY=nothing python manage.py tailwind install --no-input && \
    SECRET_KEY=nothing python manage.py tailwind build --no-input && \
    SECRET_KEY=nothing python manage.py collectstatic --no-input

# Create a non-root user (baseuser) in the users group
RUN useradd -m -r -g users -u 1000 baseuser

# Ensure the entrypoint script is executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Ensure all files are owned by the `baseuser` and `users` group
RUN chown -R baseuser:users /app /home/baseuser && chmod -R g+rwx /app /home/baseuser

USER baseuser

# Entrypoint to run migrations and start the server
ENTRYPOINT ["/app/entrypoint.sh"]