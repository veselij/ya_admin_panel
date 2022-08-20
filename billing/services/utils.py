import json
from contextlib import contextmanager
from dataclasses import asdict

import pika

from billing.services.models import NotificationMessage
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


def assign_user_role_in_auth(user_id: str, roles_id: str):
    pass
