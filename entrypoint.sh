#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z $PG_HOST $PG_PORT; do
  sleep 0.1
done
echo "PostgreSQL started"

echo "Create schema and tables in PG"
psql -h $PG_HOST -U $POSTGRES_USER -d $POSTGRES_DB -f movies_database.ddl

echo "Apply migrations, cerate super user and collectstatic"
python manage.py migrate --fake movies
python manage.py migrate --fake-initial
python manage.py createsuperuser --noinput
python manage.py collectstatic --noinput


echo "Migrate data from sqlite"
python load_data/load_data.py

echo "Start gunicorn server"
gunicorn -c config/gunicorn.py
exec "$@"
