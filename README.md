# Chemistry Inventory System

use ```docker-compose build``` to create the relevant docker image (This will need to be run anytime changes are made to the web app)

use ```docker-compose up -d``` to start the docker container (including the MySQL database)

use ```docker-compose down``` to stop the running container

go to <http://localhost:8000>

useful commands:

```docker ps```

```docker volume ls```

While the container is running, use ```docker exec -it 496-498-web-1 bash``` to access the running container, where you can panually create migrations if necessary
