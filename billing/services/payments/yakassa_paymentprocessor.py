from hashlib import md5
from uuid import UUID

from requests.exceptions import ConnectionError, ConnectTimeout
from yookassa import Configuration, Payment, Webhook
from yookassa.domain.common import ConfirmationType, SecurityHelper
from yookassa.domain.exceptions.bad_request_error import BadRequestError
from yookassa.domain.notification import (
    WebhookNotificationEventType,
    WebhookNotificationFactory,
)

from billing.services.exceptions import (
    PaymentProcessorAlreadyPayed,
    PaymentProcessorPaymentCanceled,
    PaymentProcessorUnknownResponse,
    PaymentProcessorWebhookFailure,
)
from billing.services.models import (
    PaymentDetails,
    PaymentResponse,
    PaymentResult,
    Subscription,
    UserSubscription,
)
from billing.services.payments.payments import AbstractRequest, PaymentProcessor, Status
from billing.utils.backoff import backoff
from billing.utils.exceptions import RetryExceptionError
from config import settings


class YookassaPaymentProcessor(PaymentProcessor):
    def __init__(self) -> None:
        Configuration.configure_auth_token(token=settings.YOOKASSA_TOKEN)
        self.init_webhooks()

    @staticmethod
    def init_webhooks() -> None:
        for webhook_event in [
            WebhookNotificationEventType.PAYMENT_SUCCEEDED,
            WebhookNotificationEventType.PAYMENT_CANCELED,
        ]:
            idempotence_key = md5(
                (webhook_event + settings.WEBHOOK_API_URL).encode()
            ).hexdigest()
            try:
                Webhook.add(
                    {
                        "event": webhook_event,
                        "url": settings.WEBHOOK_API_URL,
                    },
                    idempotence_key,
                )
            except BadRequestError as e:
                settings.logger.warning(e)
                raise PaymentProcessorWebhookFailure

    @backoff(
        settings.logger,
        start_sleep_time=0.1,
        factor=2,
        border_sleep_time=10,
        max_retray=2,
    )
    def generate_payment_url(
        self,
        subscription: Subscription,
        payment_details: PaymentDetails,
        return_url: str,
        idempotent_key: str,
    ) -> PaymentResult:
        try:
            payment_object = Payment.create(
                {
                    "amount": {"value": subscription.price, "currency": "RUB"},
                    "confirmation": {
                        "type": ConfirmationType.REDIRECT,
                        "return_url": return_url,
                    },
                    "payment_method_data": {"type": "bank_card"},
                    "capture": True,
                    "description": "Оплата подписки {description}".format(
                        description=subscription.description
                    ),
                    "save_payment_method": payment_details.auto_pay,
                },
                idempotent_key,
            )
        except (ConnectTimeout, ConnectionError):
            raise RetryExceptionError("Payment provider not available")

        if payment_object.paid:
            raise PaymentProcessorAlreadyPayed

        if payment_object.status == WebhookNotificationEventType.PAYMENT_CANCELED:
            raise PaymentProcessorPaymentCanceled

        return PaymentResult(
            id=UUID(payment_object.id),
            status=payment_object.status,
            url=payment_object.confirmation.confirmation_url,
        )

    @backoff(
        settings.logger,
        start_sleep_time=0.1,
        factor=2,
        border_sleep_time=10,
        max_retray=2,
    )
    def auto_pay_subscription(
        self, user_subscription: UserSubscription
    ) -> PaymentResult:
        try:
            payment_object = Payment.create(
                {
                    "amount": {
                        "value": user_subscription.subscription.price,
                        "currency": "RUB",
                    },
                    "capture": True,
                    "payment_method_id": user_subscription.auto_pay_id,
                    "description": "Авто оплата подписки {0}".format(
                        user_subscription.subscription.description
                    ),
                },
                f"{user_subscription.user.id}:{user_subscription.subscription.id}",
            )
        except (ConnectTimeout, ConnectionError):
            raise RetryExceptionError("Payment provider not available")

        return PaymentResult(
            id=UUID(payment_object.id),
            status=payment_object.status,
            url="",
        )

    def security_check(self, request: AbstractRequest) -> bool:
        ip = request.get_client_ip()
        return SecurityHelper().is_ip_trusted(ip)

    def get_payment_result(self, data: dict) -> PaymentResponse:
        notification_object = WebhookNotificationFactory().create(data)
        response_object = notification_object.object
        if notification_object.event == WebhookNotificationEventType.PAYMENT_SUCCEEDED:
            status = Status.succeed.value
        elif notification_object.event == WebhookNotificationEventType.PAYMENT_CANCELED:
            status = Status.canceled.value
        else:
            settings.logger.warning("Unexpected webhook payment status")
            raise PaymentProcessorUnknownResponse
        return PaymentResponse(
            id=response_object.id,
            status=status,
            auto_pay_id=response_object.payment_method.id,
            last_card_digits=response_object.payment_method.card.last4,
        )
