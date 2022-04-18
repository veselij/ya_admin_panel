"""Script to migrate data from sqlite3 to Postgres database."""
from contextlib import closing
import os
import sqlite3

import psycopg2
from loaders import PostgresSaver, SQLiteLoader
from psycopg2.extras import DictCursor
from tables import table_registry

if __name__ == '__main__':
    script_directory = os.path.dirname(os.path.realpath(__file__))
    config = {
        "dbname": os.environ.get("POSTGRES_DB"),
        "user": os.environ.get("POSTGRES_USER"),
        "password": os.environ.get("PGPASSWORD"),
        "host": os.environ.get("PG_HOST"),
        "port": os.environ.get("PG_PORT"),
    }
    with closing(sqlite3.connect(os.path.join(script_directory, 'db.sqlite'))) as sqlite_conn:
        with closing(psycopg2.connect(**config, cursor_factory=DictCursor)) as pg_conn:

            postgres_saver = PostgresSaver(pg_conn)
            sqlite_loader = SQLiteLoader(sqlite_conn)

            sqlite_data = sqlite_loader.load_movies(table_registry)
            postgres_saver.save_all_data(sqlite_data)
