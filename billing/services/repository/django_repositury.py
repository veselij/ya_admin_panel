from typing import Generator
from uuid import UUID

from django.utils import timezone

import billing.models as django_models
from billing.services.exceptions import (
    SubscriptionDoesNotExist,
    TransactionDoesNotExist,
    UserDoesNotExist,
    UserSubscriptionDoesNotExist,
)
from billing.services.models import Subscription, Transaction, User, UserSubscription
from billing.services.repository.repository import AbstractRepository
from billing.services.utils import exception_handler


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
        user, _ = django_models.User.objects.get_or_create(id=user_id)
        return user.to_domain()

    @exception_handler(
        exception_cls=django_models.UserSubscription.DoesNotExist,
        raises_exception_cls=UserSubscriptionDoesNotExist,
    )
    def get_user_subscription(
        self, user: User, subscription: Subscription
    ) -> UserSubscription | None:
        try:
            return django_models.UserSubscription.objects.get(
                user_id=user.id, subscription_id=subscription.id
            ).to_domain()
        except django_models.UserSubscription.DoesNotExist:
            return None

    def save_transaction(self, transaction: Transaction) -> None:
        django_models.Transaction.update_from_domain(transaction)

    def save_user_subscription(self, user_subscription: UserSubscription) -> None:
        django_models.UserSubscription.update_from_domain(user_subscription)

    def get_auto_pay_user_subscriptions(
        self,
    ) -> Generator[UserSubscription, None, None]:
        for user_subscription in django_models.UserSubscription.objects.all().filter(
            auto_pay=True, subscription_valid_to__date=timezone.now().date()
        ):
            yield user_subscription.to_domain()
