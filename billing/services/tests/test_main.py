from datetime import datetime

import pytest

from billing.services.main import (
    cancel_subscription,
    initialize_payment,
    process_post_payment_update,
    prolong_subscription,
)
from billing.services.models import PaymentResult
from billing.services.payments.fake_paymentprocessor import FakePaymentProcessor
from billing.services.repository.inmemory_repository import InMemoryRepository
from billing.services.repository.repository import AbstractRepository
from billing.services.tests.data import (
    cancelation_details,
    payment_details,
    payment_result,
    payment_update,
    return_url,
    subscription,
    subscriptions,
    transaction_id,
    user,
    user_confirmed_subscription,
    user_init_subscription,
    user_transaction_pending,
    user_transaction_succ,
)


def init_payment(repository: AbstractRepository) -> PaymentResult:
    payment_processor = FakePaymentProcessor()
    payment_processor.result_uuid = transaction_id
    idempotent_key = f"{payment_details.user_id}:{payment_details.subscription_id}"
    return initialize_payment(
        payment_processor, payment_details, repository, return_url, idempotent_key
    )


@pytest.fixture
def repository():
    r = InMemoryRepository()
    r.subscriptions = subscriptions
    return r


def test_initial_payment(repository):

    pr = init_payment(repository)

    assert pr == payment_result
    assert (
        repository.transactions[user_transaction_pending.id] == user_transaction_pending
    )
    assert (
        repository.user_subscriptions[
            (payment_details.user_id, payment_details.subscription_id)
        ].subscription
        == subscription
    )
    assert (
        repository.user_subscriptions[
            (payment_details.user_id, payment_details.subscription_id)
        ].user
        == user
    )


def test_process_post_payment_update(repository):

    repository.user_subscriptions[
        (payment_details.user_id, payment_details.subscription_id)
    ] = user_init_subscription
    repository.transactions[user_transaction_pending.id] = user_transaction_pending

    process_post_payment_update(payment_update, repository)

    assert (
        repository.user_subscriptions[
            (payment_details.user_id, payment_details.subscription_id)
        ].last_card_digits
        == user_confirmed_subscription.last_card_digits
    )
    assert (
        repository.user_subscriptions[
            (payment_details.user_id, payment_details.subscription_id)
        ].subscription_valid_to.date()
        == user_confirmed_subscription.subscription_valid_to.date()
    )
    assert repository.transactions[user_transaction_pending.id] == user_transaction_succ


def test_init_prolong_subscription(repository):

    repository.user_subscriptions[
        (payment_details.user_id, payment_details.subscription_id)
    ] = user_confirmed_subscription
    repository.transactions[user_transaction_pending.id] = user_transaction_succ
    repository.user_subscriptions[
        (payment_details.user_id, payment_details.subscription_id)
    ].subscription_valid_to = datetime.now()

    prolong_subscription(FakePaymentProcessor(), repository)
    assert (
        repository.transactions[user_transaction_pending.id] == user_transaction_pending
    )


def test_cancel_subscription(repository):
    repository.user_subscriptions[
        (payment_details.user_id, payment_details.subscription_id)
    ] = user_confirmed_subscription
    repository.transactions[user_transaction_pending.id] = user_transaction_succ

    cancel_subscription(cancelation_details, repository)

    assert not (
        repository.user_subscriptions[
            (cancelation_details.user_id, cancelation_details.subscription_id)
        ].auto_pay
    )
