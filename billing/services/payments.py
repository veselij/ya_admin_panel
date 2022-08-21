from enum import Enum
from typing import Protocol
from uuid import uuid4
from yookassa import Configuration, Payment, Webhook
from yookassa.domain.common import ConfirmationType, SecurityHelper
from yookassa.domain.notification import WebhookNotificationEventType, WebhookNotificationFactory

from config import settings
from models import PaymentDetails, PaymentResult, PaymentResultUpdate, Subscription


class Status(Enum):
    pending = "pending"
    succeed = "succeed"
    canceled = "canceled"

class PaymentProcessor(Protocol):
    def generate_payment_url(
            self,
            subscription: Subscription,
            payment_details: PaymentDetails,
    ) -> PaymentResult:
        ...


class AbstractRequest:
    def get_client_ip(self) -> str:
        pass

    def get_json_data(self) -> dict:
        pass


class YookassaPaymentProcessor(PaymentProcessor):
    def __init__(self):
        Configuration.auth_token = settings.YOOKASSA_TOKEN

    @staticmethod
    def init_webhooks():
        Webhook.add({
            "event": WebhookNotificationEventType.PAYMENT_SUCCEEDED,
            "url": settings.CONFIRMATION_API_URL,
        })
        Webhook.add({
            "event": WebhookNotificationEventType.PAYMENT_CANCELED,
            "url": settings.CONFIRMATION_API_URL,
        })

    def generate_payment_url(
            self,
            subscription: Subscription,
            payment_details: PaymentDetails,
    ) -> PaymentResult:
        idempotent_key = str(subscription.id) + str(payment_details.user_id)
        payment_object = Payment.create({
            "amount": {
                "value": subscription.price,
                "currency": "RUB"
            },
            "confirmation": {
                "type": ConfirmationType.REDIRECT,
                "return_url": ""
            },
            "capture": True,
            "description": ""
        }, idempotent_key)

        if payment_object.status != Status.pending:
            settings.logger.warning("Unexpected payment status")
            raise

        return PaymentResult(
            id=payment_object.id,
            status=payment_object.status,
            url=payment_object.confirmation.confiramtion_url,
        )

    def security_check(self, request: AbstractRequest):
        ip = request.get_client_ip()
        if not SecurityHelper().is_ip_trusted(ip):
            return False

    def confirmation_process(self, data):
        notification_object = WebhookNotificationFactory().create(data)
        response_object = notification_object.object
        if notification_object.event == WebhookNotificationEventType.PAYMENT_SUCCEEDED:
            return PaymentResultUpdate(
                id=response_object.id,
                status=Status.succeed,
                auto_pay_id='',
                last_card_digits=response_object.payment_method.card.last4,
            )
        elif notification_object.event == WebhookNotificationEventType.PAYMENT_CANCELED:
            return PaymentResultUpdate(
                id=response_object.id,
                status=Status.canceled,
                auto_pay_id='',
                last_card_digits=response_object.payment_method.card.last4,
            )
        else:
            settings.logger.warning("Unexpected webhook payment status")
            raise


class FakePaymentProcessor(PaymentProcessor):
    def generate_payment_url(
            self,
            subscription: Subscription,
            payment_details: PaymentDetails,
    ) -> PaymentResult:
        return PaymentResult(
            id=uuid4(), status=Status.pending.value, url="http://payment.com"
        )
