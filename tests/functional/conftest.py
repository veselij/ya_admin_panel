import psycopg2
import pytest
from psycopg2.extras import DictCursor
from settings import pg_db, pg_host, pg_password, pg_port, pg_user


@pytest.fixture(scope="function")
def insert_subscription():
    connect = psycopg2.connect(
        dbname=pg_db,
        host=pg_host,
        port=pg_port,
        user=pg_user,
        password=pg_password,
        cursor_factory=DictCursor,
    )
    cur = connect.cursor()
    cur.execute(
        "INSERT INTO content.subscription (id, name, price, period_days, description, created, modified) VALUES ('0bae8975-d350-4da2-91d7-e0c994b22bc4', 'test_subscription', 100, 30, 'test_subscription_description', '2022-08-27 07:32:43.062965+00', '2022-08-27 07:32:43.063021+00') ON CONFLICT DO NOTHING;"
    )
    cur.execute(
        "INSERT INTO billing.user (id, created, modified) VALUES ('0bae8975-d350-4da2-91d7-e0c994b22bc5', '2022-08-27 07:32:43.062965+00', '2022-08-27 07:32:43.063021+00') ON CONFLICT DO NOTHING;"
    )
    cur.close()
    connect.commit()
    connect.close()
    return (
        "0bae8975-d350-4da2-91d7-e0c994b22bc5",
        "0bae8975-d350-4da2-91d7-e0c994b22bc4",
    )


@pytest.fixture(scope="function")
def get_subscription():
    return (
        "0bae8975-d350-4da2-91d7-e0c994b22bc5",
        "0bae8975-d350-4da2-91d7-e0c994b22bc4",
    )


@pytest.fixture(scope="function")
def get_transaction():
    connect = psycopg2.connect(
        dbname=pg_db,
        host=pg_host,
        port=pg_port,
        user=pg_user,
        password=pg_password,
        cursor_factory=DictCursor,
    )
    cur = connect.cursor()
    cur.execute("SELECT id FROM billing.transaction limit 1;")
    id = cur.fetchone()[0]
    cur.close()
    connect.close()
    return id
