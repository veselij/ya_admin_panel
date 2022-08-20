from models import PaymentDetails, PaymentResult, PaymentResultUpdate
from payments import PaymentProcessor, Status
from repository import AbstractRepository
from subscriptions import UserSubscriptionManager
from transactions import TransactionManager
from utils import assign_user_role_in_auth, send_notification


def initialize_payment(
    payment_processor: PaymentProcessor,
    payment_details: PaymentDetails,
    repository: AbstractRepository,
) -> PaymentResult:
    subscription = repository.get_subscription(payment_details.subscription_id)
    payment_result = payment_processor.generate_payment_url(subscription)

    transaction_manager = TransactionManager(repository)
    transaction = transaction_manager.create_transaction(
        payment_details, payment_result
    )

    user_subscription_manager = UserSubscriptionManager(repository)
    user_subscription_manager.create_user_subscription(
        transaction, auto_pay=payment_details.auto_pay
    )
    return payment_result


def process_post_payment_update(
    payment_update: PaymentResultUpdate,
    repository: AbstractRepository,
) -> None:
    transaction_manager = TransactionManager(repository)
    transaction = transaction_manager.update_transaction(
        payment_update.id, payment_update.status
    )

    if payment_update.status == Status.succeed.value:
        user_subscription_manager = UserSubscriptionManager(repository)
        user_subscription_manager.update_user_subscription(
            transaction,
            active=True,
            auto_pay_id=payment_update.auto_pay_id,
            last_card_digits=payment_update.last_card_digits,
        )
        assign_user_role_in_auth(
            str(transaction.user.id), str(transaction.subscription.id)
        )
        send_notification(
            str(transaction.user.id),
            str(transaction.subscription.id),
            transaction.subscription.description,
        )
