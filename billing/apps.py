from django.apps import AppConfig
from django.conf import settings

from billing.services.payments import (
    FakePaymentProcessor,
    PaymentProcessor,
    YookassaPaymentProcessor,
)


class BillingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "billing"
    payment_processor: PaymentProcessor

    def ready(self) -> None:
        if settings.IS_FAKE_PAYMENT_API:
            self.payment_processor = FakePaymentProcessor()
        else:
            self.payment_processor = YookassaPaymentProcessor()
