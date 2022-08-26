from django.core.management.base import BaseCommand

from billing.services.main import prolong_subscription
from billing.services.payments.yakassa_paymentprocessor import YookassaPaymentProcessor
from billing.services.repository.django_repositury import DjangoRepository


class Command(BaseCommand):
    help = "execute reccurent payment"

    def handle(self, *args, **options):

        payment_processor = YookassaPaymentProcessor()
        repository = DjangoRepository()

        prolong_subscription(payment_processor, repository)
