from typing import Generator, Protocol
from uuid import UUID

from billing.services.models import Subscription, Transaction, User, UserSubscription


class AbstractRepository(Protocol):
    def get_subscription(self, subscription_id: UUID) -> Subscription:
        raise NotImplementedError

    def get_user(self, user_id: UUID) -> User:
        raise NotImplementedError

    def get_transaction(self, transaction_id: UUID) -> Transaction:
        raise NotImplementedError

    def get_user_subscription(
        self, user: User, subscription: Subscription
    ) -> UserSubscription | None:
        raise NotImplementedError

    def save_user_subscription(self, user_subscriptions: UserSubscription) -> None:
        raise NotImplementedError

    def save_transaction(self, transaction: Transaction) -> None:
        raise NotImplementedError

    def get_auto_pay_user_subscriptions(
        self,
    ) -> Generator[UserSubscription, None, None]:
        raise NotImplementedError
