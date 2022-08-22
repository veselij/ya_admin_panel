from typing import Protocol
from uuid import UUID

import billing.models as django_models
from exceptions import (
    UserDoesNotExist,
    UserSubscriptionDoesNotExist,
    SubscriptionDoesNotExist,
    TransactionDoesNotExist,
)
from models import Subscription, Transaction, User, UserSubscription
from utils import exception_handler


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


class DjangoRepository(AbstractRepository):
    @exception_handler(
        exception_cls=django_models.Subscription.DoesNotExist,
        raises_exception_cls=SubscriptionDoesNotExist,
    )
    def get_subscription(self, subscription_id: UUID) -> Subscription:
        return django_models.Subscription.objects.get(id=subscription_id).to_domain()

    @exception_handler(
        exception_cls=django_models.Transaction.DoesNotExist,
        raises_exception_cls=TransactionDoesNotExist,
    )
    def get_transaction(self, transaction_id: UUID) -> Transaction:
        return django_models.Transaction.objects.get(id=transaction_id).to_domain()

    @exception_handler(
        exception_cls=django_models.User.DoesNotExist,
        raises_exception_cls=UserDoesNotExist,
    )
    def get_user(self, user_id: UUID) -> User:
        return django_models.User.objects.get(id=user_id).to_domain()

    @exception_handler(
        exception_cls=django_models.UserSubscription.DoesNotExist,
        raises_exception_cls=UserSubscriptionDoesNotExist,
    )
    def get_user_subscription(
        self, user: User, subscription: Subscription
    ) -> UserSubscription | None:
        try:
            return django_models.UserSubscription.objects.get(user=user ,subscription=Subscription).to_domain()
        except django_models.UserSubscription.DoesNotExist:
            return None

    def save_transaction(self, transaction: Transaction) -> None:
        django_models.Transaction.update_from_domain(transaction)

    def save_user_subscription(self, user_subscription: UserSubscription) -> None:
        django_models.UserSubscription.update_from_domain(user_subscription)
