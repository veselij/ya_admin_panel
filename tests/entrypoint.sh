#!/bin/sh

echo "Waiting for web server"
while ! nc -z $NGINX_HOST 80; do
  sleep 0.1
done

while ! nc -z $ADMIN_HOST 8000; do
  sleep 0.1
done


python3 -m pytest functional/
exec "$@"
