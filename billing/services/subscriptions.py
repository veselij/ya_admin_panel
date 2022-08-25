import datetime as dt
from uuid import uuid4

from billing.services.models import Subscription, Transaction, User, UserSubscription
from billing.services.repository import AbstractRepository


class UserSubscriptionManager:
    def __init__(self, repository: AbstractRepository) -> None:
        self.repository = repository

    def create_user_subscription(
        self,
        transaction: Transaction,
        auto_pay: bool,
    ) -> None:
        user_subscription = self.repository.get_user_subscription(
            transaction.user, transaction.subscription
        )

        if user_subscription:
            user_subscription.auto_pay = auto_pay
        else:
            user_subscription = UserSubscription(
                id=uuid4(),
                user=transaction.user,
                subscription=transaction.subscription,
                auto_pay=auto_pay,
            )
        self.repository.save_user_subscription(user_subscription)

    def update_user_subscription(
        self,
        transaction: Transaction,
        auto_pay_id: str,
        last_card_digits: int,
    ) -> None:
        user_subscription = self.repository.get_user_subscription(
            transaction.user, transaction.subscription
        )
        if not user_subscription:
            raise KeyError(
                "User subscription for user %s with subscription %s does not exist",
                transaction.user.id,
                transaction.subscription.id,
            )
        user_subscription.auto_pay_id = auto_pay_id
        user_subscription.last_card_digits = last_card_digits
        user_subscription.subscription_valid_to = calculate_vaild_date(
            user_subscription, transaction.subscription
        )

        self.repository.save_user_subscription(user_subscription)

    def cancel_user_subscription(self, user: User, subscription: Subscription) -> None:
        user_subscription = self.repository.get_user_subscription(user, subscription)
        if not user_subscription:
            raise KeyError(
                "User subscription for user %s with subscription %s does not exist",
                user.id,
                subscription.id,
            )
        user_subscription.auto_pay = False
        self.repository.save_user_subscription(user_subscription)


def calculate_vaild_date(
    user_subscription: UserSubscription, subscription: Subscription
) -> dt.datetime:
    if user_subscription.subscription_valid_to > dt.datetime.now():
        return user_subscription.subscription_valid_to + dt.timedelta(
            days=subscription.period_days
        )
    return dt.datetime.now() + dt.timedelta(days=subscription.period_days)
