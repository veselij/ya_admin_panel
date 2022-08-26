from django.core.management.base import BaseCommand

from billing.services.main import delete_user_subscription_in_auth
from billing.services.repository.django_repositury import DjangoRepository


class Command(BaseCommand):
    help = "remove user subscription in auth"

    def handle(self, *args, **options):

        repository = DjangoRepository()

        delete_user_subscription_in_auth(repository)
