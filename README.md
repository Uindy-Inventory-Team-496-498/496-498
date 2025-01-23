# Chemistry Inventory System

Note: MySQL needs to be installed manually before running the below configuration, try ```pip install mysql```

## Start the Applciation and mySQL database

to create the relevant docker image (This will need to be run anytime changes are made to the web app):

```docker-compose build```

to start the docker container (including the MySQL database). use the flag -d to have no output, but be careful as the output is often helpful for debugging:

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

Inside the container web container

Make migrations:  

```cd /app```
```python manage.py makemigrations```

Apply migrations:

```python manage.py migrate```

On your host machine (if necessary)
Restart the container:

```docker-compose restart web```

For removeing current migrations, sometimes necesarry if there are issues. Will need to remake and apply migrations afterwards. May also need to drop migrations from mysql manually:

```rm /app/hello/migrations/00*.py```

## Misc Django commands

For loading from a fixture:

```python manage.py loaddata hello/fixtures/hello_fixtures.json```

For loading from a csv:

```python manage.py load_csv '/app/Chemical Intentory Generalized.csv'```

See current Migrations:

```python manage.py showmigrations```

This outputs model definitions based on the current database schema, which you can copy into models.py:

```python manage.py inspectdb```

If you accidentally modify the database directly and migrations are out of sync, you may need to reset migrations:

```python manage.py makemigrations --empty <app_name>```

```python manage.py migrate --fake```

## mySQL Commands

Access the mysql database (from the django container):

```python manage.py dbshell```

Usefell commads in mysql:

Set working database:

```USE my_database;```

See current tables:

```SHOW TABLES;```

See structure of specific table:

```DESCRIBE hello_currentlyinstoragetable;```

Delete previous migration:

```DELETE FROM django_migrations WHERE app = 'hello';```

Drop Tables:

```USE your_db_name;```

```DROP TABLE IF EXISTS hello_allchemicalstable;```

```DROP TABLE IF EXISTS hello_currentlyinstoragetable;```

```DROP TABLE IF EXISTS hello_qrcodedata;```
