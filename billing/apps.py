from django.apps import AppConfig
from django.conf import settings

from billing.services.payments.payments import PaymentProcessor


class BillingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "billing"
    payment_processor: PaymentProcessor

    def ready(self) -> None:
        if settings.IS_FAKE_PAYMENT_API:
            from billing.services.payments.fake_paymentprocessor import (
                FakePaymentProcessor,
            )

            self.payment_processor = FakePaymentProcessor()
        else:
            from billing.services.payments.yakassa_paymentprocessor import (
                YookassaPaymentProcessor,
            )

            self.payment_processor = YookassaPaymentProcessor()
