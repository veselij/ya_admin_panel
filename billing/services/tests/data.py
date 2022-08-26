import copy
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from billing.services.models import (
    PaymentDetails,
    PaymentResponse,
    PaymentResult,
    Subscription,
    Transaction,
    User,
    UserSubscription,
)
from billing.services.payments.payments import Status

return_url = "http://return_url.com"
transaction_id = uuid4()
user_subscription_id = uuid4()

payment_details = PaymentDetails(
    user_id=UUID("841a4e67-515b-41dd-9ea6-2a4bd35ed6ca"),
    subscription_id=UUID("bb8a9bbd-9d6b-435d-bcff-13685d7796d6"),
    auto_pay=True,
)

payment_update = PaymentResponse(
    id=str(transaction_id),
    status=Status.succeed.value,
    auto_pay_id="",
    last_card_digits=1234,
)

payment_result = PaymentResult(
    id=transaction_id, status=Status.pending.value, url="http://payment.com"
)

subscription = Subscription(
    id=UUID("bb8a9bbd-9d6b-435d-bcff-13685d7796d6"),
    name="Test subscriptin",
    price=100,
    period_days=30,
    description="Test month subscriptions",
)
subscriptions = {subscription.id: subscription}

user = User(id=UUID("841a4e67-515b-41dd-9ea6-2a4bd35ed6ca"))

user_transaction_pending = Transaction(
    id=transaction_id, subscription=subscription, user=user, status=Status.pending.value
)
user_transaction_succ = Transaction(
    id=transaction_id, subscription=subscription, user=user, status=Status.succeed.value
)

user_init_subscription = UserSubscription(
    id=user_subscription_id, subscription=subscription, user=user, auto_pay=True
)

user_confirmed_subscription = copy.deepcopy(user_init_subscription)
user_confirmed_subscription.auto_pay_id = payment_update.auto_pay_id
user_confirmed_subscription.last_card_digits = payment_update.last_card_digits
user_confirmed_subscription.subscription_valid_to = datetime.now() + timedelta(
    days=subscription.period_days
)
