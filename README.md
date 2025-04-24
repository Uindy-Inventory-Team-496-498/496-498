# Chemistry Inventory System
This application was created my the University of Indianapolis ENGR/CSCI 496-498 class of 2024/2025.

## Start the Applciation and mySQL database
<https://docs.docker.com/reference/cli/docker/compose/>

To create a new docker image:
```docker compose build```

to start the docker container (including the MySQL database). use the flag -d to have no output, but be careful as the output is often helpful for debugging. The --force-recreate can be useful to start clean.
```docker-compose up```

to teardown the running container(s):
```docker-compose down```

or to stop them:
```docker-compose stop```

if inaccesible, double check docker logs for the MySQL container and the Django container.

## First thing
If this is the first time the containers are being created and started, you must first run the create_super.py command. This will create a default admin user as well as the intitial structure for the groups and users.
```python manage.py create_super.py```

## Misc Docker commands

For checking logs:
```docker logs <container_name>```

Show current docker processes:
```docker ps```

See current volumes:
```docker volume ls```

Restart the container:
```docker-compose restart web```

## To access the Django container

On your host machine
```docker exec -it django_web bash``` for default user

```docker exec -it --user root django_web bash``` for root user

## Migrations 
Migrations are how the database is managed for Django. If changes are made to the structure of hte database (contained in the models.py file) The following commands will have to be used to make sure the structure of the SQL database is up to date. The commands below are inside the django_web container.
<https://docs.djangoproject.com/en/5.2/topics/migrations/>

To make migrations:
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
##Tailwind
Tailwind is a tool used by the application for deploying CSS. Tailwind should be built and deployed automatically when the docker compose file is used
<https://django-tailwind.readthedocs.io/en/4.0.1/usage.html>

To install dependencies
```python manage.py tailwind install```

To build the tailwind css file used for production:
```python manage.py tailwind build```

For development environment, the following command can be used to have tailwind actively looking for changes and update real-time. This is only suitable for development:
```python manage.py tailwind start```

## mySQL Commands
The web applicaton uses MySQL for persistent data and user information.
<https://dev.mysql.com/doc/refman/8.4/en/mysql-commands.html>
<https://www.sqltutorial.org/sql-cheat-sheet/>

Access the mysql database (from the django container):
```python manage.py dbshell```

Usefell commads in mysql:

Set working database:
```USE my_database;```

See current tables:
```SHOW TABLES;```

See structure of specific table:
```DESCRIBE chemistry_system_individualChemicals;```

Delete previous migration:
```DELETE FROM django_migrations WHERE app = 'chemistry_system';```

Drop Tables:

```USE your_db_name;```

```DROP TABLE IF EXISTS chemistry_system_allChemicals;```

```DROP TABLE IF EXISTS chemistry_system_individualChemicals;```

```DROP TABLE IF EXISTS chemistry_system_qrcodedata;```
