import os

pg_db = os.environ.get("POSTGRES_DB")
pg_user = os.environ.get("POSTGRES_USER")
pg_password = os.environ.get("PGPASSWORD")
pg_host = os.environ.get("PG_HOST", "127.0.0.1")
pg_port = os.environ.get("PG_PORT", 5432)
admin_host = os.environ.get("ADMIN_HOST", "127.0.0.1")
nginx_host = os.environ.get("NGINX_HOST", "127.0.0.1")
