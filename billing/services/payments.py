from enum import Enum
from typing import Protocol
from uuid import uuid4

from models import PaymentResult, Subscription


class Status(Enum):
    pending = "pending"
    succeed = "succeed"


class PaymentProcessor(Protocol):
    def generate_payment_url(
        self,
        subscription: Subscription,
        save_payment_method: bool = False,
    ) -> PaymentResult:
        ...


class FakePaymentProcessor(PaymentProcessor):
    def generate_payment_url(
        self,
        subscription: Subscription,
        save_payment_method: bool = False,
    ) -> PaymentResult:
        return PaymentResult(
            id=uuid4(), status=Status.pending.value, url="http://payment.com"
        )
