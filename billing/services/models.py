import datetime as dt
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class PaymentDetails:
    user_id: UUID
    subscription_id: UUID
    auto_pay: bool


@dataclass(frozen=True)
class PaymentResult:
    id: UUID
    status: str
    url: str


@dataclass(frozen=True)
class PaymentResultUpdate:
    id: str
    status: str
    auto_pay_id: str
    last_card_digits: int


@dataclass(frozen=True)
class Subscription:
    id: UUID
    price: int
    period_days: int
    description: str


@dataclass(frozen=True)
class User:
    id: UUID


@dataclass
class Transaction:
    id: UUID
    user: User
    subscription: Subscription
    status: str


@dataclass
class UserSubscription:
    id: UUID
    user: User
    subscription: Subscription
    auto_pay: bool
    subscription_valid_to: dt.datetime = dt.datetime(year=2000, month=1, day=1)
    active: bool = False
    last_card_digits: int = 0
    auto_pay_id: str | None = None


@dataclass(frozen=True)
class NotificationMessage:
    notification_name: str
    user_id: str
    template_id: str | None
    content_id: str | None
    content_value: str | None
