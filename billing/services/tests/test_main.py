from uuid import UUID

import pytest

from main import initialize_payment, process_post_payment_update
from models import PaymentDetails, PaymentResult, PaymentResultUpdate
from payments import FakePaymentProcessor, Status
from repository import AbstractRepository, InMemoryRepository

payment_details = PaymentDetails(
    user_id=UUID("841a4e67-515b-41dd-9ea6-2a4bd35ed6ca"),
    subscription_id=UUID("bb8a9bbd-9d6b-435d-bcff-13685d7796d6"),
    auto_pay=True,
)


def init_payment(repository: AbstractRepository) -> PaymentResult:
    payment_processor = FakePaymentProcessor()
    return initialize_payment(payment_processor, payment_details, repository)


def test_initial_payment():

    repository = InMemoryRepository()

    payment_result = init_payment(repository)
    assert payment_result.status == Status.pending.value

    transaction = repository.get_transaction(payment_result.id)
    assert transaction.id == payment_result.id
    assert transaction.status == payment_result.status
    assert transaction.user.id == payment_details.user_id
    assert transaction.subscription.id == payment_details.subscription_id

    user_subscription = repository.get_user_subscription(
        transaction.user, transaction.subscription
    )
    assert user_subscription is not None
    assert user_subscription.user.id == payment_details.user_id
    assert user_subscription.subscription.id == payment_details.subscription_id


def test_process_post_payment_update():

    repository = InMemoryRepository()

    payment_result = init_payment(repository)
    payment_update = PaymentResultUpdate(
        id=str(payment_result.id),
        status=Status.succeed.value,
        auto_pay_id="",
        last_card_digits=1234,
    )

    process_post_payment_update(payment_update, repository)
    updated_transaction = repository.get_transaction(payment_result.id)
    assert updated_transaction.status == Status.succeed.value

    user_subscription = repository.get_user_subscription(
        updated_transaction.user, updated_transaction.subscription
    )
    assert user_subscription is not None
    assert user_subscription.active == True
    assert user_subscription.last_card_digits == payment_update.last_card_digits
