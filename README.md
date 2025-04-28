# Chemistry Inventory System
This application was created my the University of Indianapolis ENGR/CSCI 496-498 class of 2024/2025.

## Start the Applciation and mySQL database
<https://docs.docker.com/reference/cli/docker/compose/>

There are two separete docker-compose files, one for production and one for development. use the -f flag to specify the file to use. The dev enviroment uses a bind mount so changes are reflected right away, while the prod enviroment uses a named volume, so changes must be reflected manually (delete the named volume and restart). 

Additionally, the prod enviroment specifies DEBUG to be False so errors are not reported directly to users, and it serves static files via whitenoise (acceptable in low volume situations)

To create a new docker image:

```docker compose -f docker-compose.dev.yml build``` or

```docker compose -f docker-compose.prod.yml build```

to start the docker container (including the MySQL database). use the flag -d to have no output, but be careful as the output is often helpful for debugging. The --force-recreate can be useful to start clean.

```docker compose -f docker-compose.dev.yml up``` or 

```docker compose -f docker-compose.prod.yml up```

to teardown the running container(s).

```docker compose -f docker-compose.prod.yml down``` or 

```docker compose -f docker-compose.prod.yml down```


or to stop them:

```docker compose stop```

After changes are made and you want to update a prod evironment
1. ```docker compose -f docker-compose.prod.yml down```
2. ```git pull```
3. ```docker volume delete 496-498_app_data```
4. ```docker compose -f docker-compose.prod.yml up --build```

if inaccesible, double check docker logs for the MySQL container and the Django container.

### Misc Docker commands

For checking logs:
```docker logs <container_name>```

Show current docker processes:
```docker ps```

See current volumes:
```docker volume ls```

Restart the container:
```docker compose restart```

## To access the Django container

On your host machine
```docker exec -it django_web bash``` for default user

```docker exec -it --user root django_web bash``` for root user

## Migrations 
Migrations are how the database is managed for Django. If changes are made to the structure of hte database (contained in the models.py file) The following commands will have to be used to make sure the structure of the SQL database is up to date. The commands below are inside the django_web container.
<https://docs.djangoproject.com/en/5.2/topics/migrations/>

Heres the basic workflow for when changes are made to the SQl structure in a dev environment and you want to apply them to the running django service.
1. Run ```python manage.py makemigrations``` on the dev machine.
2. Run ```python manage.py migrate``` on the dev machine, in order to apply the changes locally and test them.
3. Push your changes, including the newly created migration file, to GitHub
4. On the machine with the application running, pull the changes from GitHub initially, Django may throw some errors since there migratory changes not yet applied.
5. Restart the django_web container. Within the docker-compose.yml file, the ```python manage.py migrate``` command will be run on startup
6. Wait for the container to restart

To make migrations:
```python manage.py makemigrations```

Apply migrations:
```python manage.py migrate```

For removeing current migrations, sometimes necesarry if there are issues. Will need to remake and apply migrations afterwards. This needs to be done inside the django container. May also need to drop migrations from mysql manually:
```rm /app/chemistry_system/migrations/00*.py```

On your host machine, not inside the container (if necessary)
Restart the container:
```docker-compose restart web```

### Misc Django commands
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
