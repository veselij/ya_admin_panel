from abc import ABC, abstractmethod
from enum import Enum
from typing import Protocol

from billing.services.models import (
    PaymentDetails,
    PaymentResponse,
    PaymentResult,
    Subscription,
    UserSubscription,
)


class Status(Enum):
    pending = "pending"
    succeed = "succeed"
    canceled = "canceled"


class PaymentProcessor(Protocol):
    def generate_payment_url(
        self,
        subscription: Subscription,
        payment_details: PaymentDetails,
        return_url: str,
        idempotent_key: str,
    ) -> PaymentResult:
        raise NotImplementedError

    def get_payment_result(self, data: dict) -> PaymentResponse:
        raise NotImplementedError

    def auto_pay_subscription(
        self, user_subscription: UserSubscription
    ) -> PaymentResult:
        raise NotImplementedError


class AbstractRequest(ABC):
    @abstractmethod
    def get_client_ip(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_json_data(self) -> dict:
        raise NotImplementedError
