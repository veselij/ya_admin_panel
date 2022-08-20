from uuid import UUID

from models import PaymentDetails, PaymentResult, Transaction, User
from repository import AbstractRepository


class TransactionManager:
    def __init__(self, repository: AbstractRepository) -> None:
        self.repository = repository

    def create_transaction(
        self, payment_details: PaymentDetails, payment_result: PaymentResult
    ) -> Transaction:
        subscription = self.repository.get_subscription(payment_details.subscription_id)
        transaction = Transaction(
            id=payment_result.id,
            user=User(id=payment_details.user_id),
            subscription=subscription,
            status=payment_result.status,
        )
        self.repository.save_transaction(transaction)
        return transaction

    def update_transaction(self, payment_id: str, status: str) -> Transaction:
        transaction = self.repository.get_transaction(UUID(payment_id))
        transaction.status = status
        self.repository.save_transaction(transaction)
        return transaction
