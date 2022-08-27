from http import HTTPStatus
from urllib.parse import urljoin

import pytest
import requests
from settings import nginx_host

PAYMENT_INIT_URL = f"http://{nginx_host}/api/v1/billing/"


def test_payment_init(insert_subscription):
    user_id, subsc_id = insert_subscription

    body = {
        "user_id": user_id,
        "subscription_id": subsc_id,
        "auto_pay": "1",
        "idempotent_key": user_id,
    }

    r = requests.post(urljoin(PAYMENT_INIT_URL, "payment"), json=body)

    assert r.status_code == HTTPStatus.OK


def test_cancel_subscription(get_subscription):
    user_id, subsc_id = get_subscription

    body = {
        "user_id": user_id,
        "subscription_id": subsc_id,
    }

    r = requests.post(urljoin(PAYMENT_INIT_URL, "cancel"), json=body)

    assert r.status_code == HTTPStatus.OK


def test_provider_update(get_transaction):

    body = {
        "id": get_transaction,
        "status": "succeed",
        "auto_pay_id": "",
        "last_card_digits": "1234",
    }

    r = requests.post(urljoin(PAYMENT_INIT_URL, "paymentWebhookApi"), json=body)

    assert r.status_code == HTTPStatus.OK
