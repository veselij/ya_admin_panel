from datetime import datetime
from typing import Generator
from uuid import UUID

from billing.services.models import Subscription, Transaction, User, UserSubscription
from billing.services.repository.repository import AbstractRepository


class InMemoryRepository(AbstractRepository):
    def __init__(self) -> None:
        self.transactions: dict[UUID, Transaction] = {}
        self.user_subscriptions: dict[tuple[UUID, UUID], UserSubscription] = {}
        self.subscriptions: dict[UUID, Subscription] = {}

    def get_user(self, user_id: UUID) -> User:

        users: dict[UUID, User] = {
            UUID("841a4e67-515b-41dd-9ea6-2a4bd35ed6ca"): User(
                id=UUID("841a4e67-515b-41dd-9ea6-2a4bd35ed6ca")
            )
        }
        if user_id not in users:
            users[user_id] = User(id=user_id)
        return users[user_id]

    def get_subscription(self, subscription_id: UUID) -> Subscription:
        if subscription_id not in self.subscriptions:
            raise ValueError("subscription_id %id does not exist", subscription_id)
        return self.subscriptions[subscription_id]

    def get_transaction(self, transaction_id: UUID) -> Transaction:
        return self.transactions[transaction_id]

    def save_transaction(self, transaction: Transaction) -> None:
        self.transactions[transaction.id] = transaction

    def get_user_subscription(
        self, user: User, subscription: Subscription
    ) -> UserSubscription | None:
        return self.user_subscriptions.get((user.id, subscription.id), None)

    def save_user_subscription(self, user_subscriptions: UserSubscription) -> None:
        self.user_subscriptions[
            (user_subscriptions.user.id, user_subscriptions.subscription.id)
        ] = user_subscriptions

    def get_auto_pay_user_subscriptions(
        self,
    ) -> Generator[UserSubscription, None, None]:
        for user_subscription in self.user_subscriptions.values():
            if (
                user_subscription.auto_pay
                and user_subscription.subscription_valid_to.date()
                == datetime.now().date()
            ):
                yield user_subscription
