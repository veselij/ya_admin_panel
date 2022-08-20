from typing import Protocol
from uuid import UUID

from models import Subscription, Transaction, User, UserSubscription


class AbstractRepository(Protocol):
    def get_subscription(self, subscription_id: UUID) -> Subscription:
        ...

    def get_user(self, user_id: UUID) -> User:
        ...

    def get_transaction(self, transaction_id: UUID) -> Transaction:
        ...

    def get_user_subscription(
        self, user: User, subscription: Subscription
    ) -> UserSubscription | None:
        ...

    def save_user_subscription(self, user_subscriptions: UserSubscription) -> None:
        ...

    def save_transaction(self, transaction: Transaction) -> None:
        ...


class InMemoryRepository(AbstractRepository):
    def __init__(self) -> None:
        self.transactions: dict[UUID, Transaction] = {}
        self.user_subscriptions: dict[tuple[UUID, UUID], UserSubscription] = {}

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
        subscriptions: dict[UUID, Subscription] = {
            UUID("bb8a9bbd-9d6b-435d-bcff-13685d7796d6"): Subscription(
                id=UUID("bb8a9bbd-9d6b-435d-bcff-13685d7796d6"),
                price=100,
                period_days=30,
                description="Test month subscriptions",
            )
        }
        if subscription_id not in subscriptions:
            raise ValueError("subscription_id %id does not exist", subscription_id)
        return subscriptions[subscription_id]

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
