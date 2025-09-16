docker build -t saloon:0.9 .
docker run -it --rm -p 8000:8000 -v $(pwd):/app my-django-app