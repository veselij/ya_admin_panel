import json
from contextlib import contextmanager
from dataclasses import asdict
from functools import wraps
from typing import Type
from urllib.parse import urljoin

import pika
import requests
from requests import ConnectionError, ConnectTimeout, HTTPError

from billing.services.models import NotificationMessage
from billing.utils import errormessages
from billing.utils.backoff import backoff
from billing.utils.exceptions import RetryExceptionError
from config import settings


@contextmanager
def _rabbit_connection():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=settings.NOTIFICATION_HOST),
    )
    channel = connection.channel()
    channel.queue_declare(settings.NOTIFICATION_QUEUE, durable=True)
    try:
        yield channel
    finally:
        channel.close()
        connection.close()


def send_notification(user_id: str, content_id: str, content_value: str):
    message = NotificationMessage(
        notification_name=settings.NOTIFICATION_NAME,
        user_id=user_id,
        template_id=settings.NOTIFICATION_TEMPLATE,
        content_id=content_id,
        content_value=content_value,
    )
    if settings.NOTIFICATION_ENABLED:
        with _rabbit_connection() as conn:
            conn.basic_publish(
                exchange="",
                routing_key=settings.NOTIFICATION_QUEUE,
                body=json.dumps(asdict(message)),
            )
    settings.logger.info(
        "new payment event published for user %s content_id %s",
        message.user_id,
        message.content_id,
    )


@backoff(
    settings.logger,
    start_sleep_time=0.1,
    factor=2,
    border_sleep_time=10,
    max_retray=2,
)
def assign_user_role_in_auth(user_id: str, roles_id: str):
    if settings.AUTH_ENABLED:
        try:
            r = requests.post(
                urljoin(settings.AUTH_URL_ROLE, user_id),
                data=json.dumps({"roles_id": [roles_id]}),
            )
            r.raise_for_status()
        except (ConnectTimeout, ConnectionError):
            raise RetryExceptionError(errormessages.AUTH)
        except HTTPError:
            settings.logger.warning(errormessages.AUTH_HTTP)


@backoff(
    settings.logger,
    start_sleep_time=0.1,
    factor=2,
    border_sleep_time=10,
    max_retray=2,
)
def delete_user_role_in_auth(user_id: str, roles_id: str):
    if settings.AUTH_ENABLED:
        try:
            r = requests.delete(
                urljoin(settings.AUTH_URL_ROLE, user_id),
                data=json.dumps({"roles_id": [roles_id]}),
            )
            r.raise_for_status()
        except (ConnectTimeout, ConnectionError):
            raise RetryExceptionError(errormessages.AUTH)
        except HTTPError:
            settings.logger.warning(errormessages.AUTH)


def exception_handler(
    exception_cls: Type[Exception], raises_exception_cls: Type[Exception]
):
    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception_cls as e:
                raise raises_exception_cls() from e
            except Exception as e:
                raise exception_cls() from e

        return inner

    return decorator
