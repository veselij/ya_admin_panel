import random
from enum import Enum
from hashlib import md5
from typing import Protocol
from uuid import uuid4

from yookassa import Configuration, Payment, Webhook
from yookassa.domain.common import ConfirmationType, SecurityHelper
from yookassa.domain.exceptions.bad_request_error import BadRequestError
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
        Configuration.configure_auth_token(
            token=settings.YOOKASSA_TOKEN
        )

        self.init_webhooks()

    @staticmethod
    def init_webhooks():
        for webhook_event in [
            WebhookNotificationEventType.PAYMENT_SUCCEEDED,
            WebhookNotificationEventType.PAYMENT_CANCELED
        ]:
            idempotence_key = md5((webhook_event + settings.WEBHOOK_API_URL).encode()).hexdigest()
            try:
                Webhook.add({
                    "event": webhook_event,
                    "url": settings.WEBHOOK_API_URL,
                }, idempotence_key)
            except BadRequestError as e:
                settings.logger.warning(e)

    def generate_payment_url(
            self,
            subscription: Subscription,
            payment_details: PaymentDetails,
    ) -> PaymentResult:
        idempotent_key = md5(
            (str(subscription.id) + str(payment_details.user_id)).encode()
        ).hexdigest()
        payment_object = Payment.create({
            "amount": {
                "value": subscription.price,
                "currency": "RUB"
            },
            "confirmation": {
                "type": ConfirmationType.REDIRECT,
                "return_url": payment_details.return_url
            },
            "payment_method_data": {
                "type": "bank_card"
            },
            "capture": True,
            "description": "Оплата подписки {description}".format(description=subscription.description),
            "save_payment_method": payment_details.auto_pay,
        }, idempotent_key)

        if payment_object.status != Status.pending.value:
            settings.logger.warning("Unexpected payment status")
            raise

        return PaymentResult(
            id=payment_object.id,
            status=payment_object.status,
            url=payment_object.confirmation.confirmation_url,
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
                status=Status.succeed.value,
                auto_pay_id=response_object.payment_method.id,
                last_card_digits=response_object.payment_method.card.last4,
            )
        elif notification_object.event == WebhookNotificationEventType.PAYMENT_CANCELED:
            return PaymentResultUpdate(
                id=response_object.id,
                status=Status.canceled.value,
                auto_pay_id=response_object.payment_method.id,
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
