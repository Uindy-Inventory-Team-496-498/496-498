# Chemistry Inventory System

Note: MySQL needs to be installed manually before running the below configuration, try ```pip install mysql```

## Start the Applciation and mySQL database

to create the relevant docker image (This will need to be run anytime changes are made to the web app):
```docker-compose build```

to start the docker container (including the MySQL database). use the flag -d to have no output, but be careful as the output is often helpful for debugging. After starting the container, you will need to manually make and apply migrations. This should be done from within the Django container. See below for the instructions:
```docker-compose up```

to stop the running container(s):
```docker-compose down```

go to <http://localhost:8000>
if inaccesible, double check docker logs for the MySQL container and the Django container.

## Misc Docker commands

For checking logs:
```docker logs <container_name>```

Show current docker processes:
```docker ps```

See current volumes:
```docker volume ls```

## To access the Django container

On your host machine
```docker exec -it django_web bash```

The commands below are inside the web container

Make migrations:  

```cd /app```

```python manage.py makemigrations```

Apply migrations:
```python manage.py migrate```

For removeing current migrations, sometimes necesarry if there are issues. Will need to remake and apply migrations afterwards. This needs to be done inside the django container. May also need to drop migrations from mysql manually:
```rm /app/chemistry_system/migrations/00*.py```

On your host machine, not inside the container (if necessary)
Restart the container:
```docker-compose restart web```

## Misc Django commands

For loading from a fixture:
```python manage.py loaddata chemistry_system/fixtures/chemistry_system_fixtures.json```

For loading from a csv:
```python manage.py load_csv '/app/Chemical Intentory Generalized.csv'```

See current Migrations:
```python manage.py showmigrations```

This outputs model definitions based on the current database schema, which you can copy into models.py:
```python manage.py inspectdb```

If you accidentally modify the database directly and migrations are out of sync, you may need to reset migrations:

```python manage.py makemigrations --empty <app_name>```

```python manage.py migrate --fake```

While in the docker container, you can run this to populate the Individual Bottles table with some dummy data
```python manage.py populate_storage```

## mySQL Commands

Access the mysql database (from the django container):
```python manage.py dbshell```

Usefell commads in mysql:

Set working database:
```USE my_database;```

See current tables:
```SHOW TABLES;```

See structure of specific table:
```DESCRIBE chemistry_system_currentlyinstoragetable;```

Delete previous migration:
```DELETE FROM django_migrations WHERE app = 'chemistry_system';```

Drop Tables:

```USE your_db_name;```

```DROP TABLE IF EXISTS chemistry_system_allchemicalstable;```

```DROP TABLE IF EXISTS chemistry_system_currentlyinstoragetable;```

```DROP TABLE IF EXISTS chemistry_system_qrcodedata;```
