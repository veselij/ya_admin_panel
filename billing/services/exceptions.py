class SubscriptionDoesNotExist(Exception):
    pass


class UserDoesNotExist(Exception):
    pass


class TransactionDoesNotExist(Exception):
    pass


class UserSubscriptionDoesNotExist(Exception):
    pass


class PaymentProcessorWebhookFailure(Exception):
    pass


class PaymentProcessorUnknownResponse(Exception):
    pass


class PaymentProcessorNotAvailable(Exception):
    pass


class PaymentProcessorAlreadyPayed(Exception):
    pass


class PaymentProcessorPaymentCanceled(Exception):
    pass
