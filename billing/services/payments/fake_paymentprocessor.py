from uuid import uuid4

from billing.services.models import (
    PaymentDetails,
    PaymentResponse,
    PaymentResult,
    Subscription,
    UserSubscription,
)
from billing.services.payments.payments import PaymentProcessor, Status


class FakePaymentProcessor(PaymentProcessor):
    result_uuid = uuid4()

    def generate_payment_url(
        self,
        subscription: Subscription,
        payment_details: PaymentDetails,
        return_url: str,
        idempotent_key: str,
    ) -> PaymentResult:
        return PaymentResult(
            id=self.result_uuid, status=Status.pending.value, url="http://payment.com"
        )

    def get_payment_result(self, data: dict) -> PaymentResponse:
        return PaymentResponse(
            id=data["id"],
            status=data["status"],
            auto_pay_id=data["auto_pay_id"],
            last_card_digits=data["last_card_digits"],
        )

    def auto_pay_subscription(
        self, user_subscription: UserSubscription
    ) -> PaymentResult:
        return PaymentResult(
            id=uuid4(), status=Status.pending.value, url="http://payment.com"
        )
