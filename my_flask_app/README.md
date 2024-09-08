# Chemistry Inventory System.

## Builds the image, make sure Docker is running
docker build -t my-flask-app .

## Creates a container from the image 
docker run -p 5000:5000 my-flask-app
access via port 5000 (http://localhost:5000)