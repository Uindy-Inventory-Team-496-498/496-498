# Chemistry Inventory System

Note: MySQL needs to be installed manually before running the below configuration, try ```pip install mysql```

use ```docker-compose build``` to create the relevant docker image (This will need to be run anytime changes are made to the web app)

use ```docker-compose up -d``` to start the docker container (including the MySQL database)

use ```docker-compose down``` to stop the running container(s)

go to <http://localhost:8000>
if inaccesible, double check docker logs for the MySQL container and the Django container.

useful commands:

For checking logs:
```docker logs <container_name>```

```docker exec -it <mysql_container_name> mysql -u my_user -p``` This will allow you to access the sql container directly, and run sql commands, allowing you to check if migrations were applied properly with:
    ```USE <your_database_name>;```
    ```SHOW TABLES;```
    ```DESCRIBE <table_name>;```

```docker ps``` Show current docker processes

```docker volume ls```

While the container is running, use ```docker exec -it <django_container_name> bash``` to access the running container, where you can manually create migrations if necessary:
    ```cd /app```
    ```python manage.py makemigrations hello```
    ```python manage.py migrate```
    ```python manage.py showmigrations```
    ```python manage.py inspectdb``` : This outputs model definitions based on the current database schema, which you can copy into models.py.
    If you accidentally modify the database directly and migrations are out of sync, you may need to reset migrations:
    ```python manage.py makemigrations --empty <app_name>```
    ```python manage.py migrate --fake```

To startup just the sql container or just the django container:

```docker-compose up <service_name>``

If serious migration issues:
Step 1: Delete migration files
```del hello\migrations\000*.py```

Step 2: Reset migration history
Connect to your database and run the following SQL command
```USE <your_database_name>;```
```DELETE FROM django_migrations WHERE app = 'hello';```

Step 3: Create new migrations
```python manage.py makemigrations hello --noinput```

Step 4: Apply migrations
```python manage.py migrate --noinput```