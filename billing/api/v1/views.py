import json

from django.http import JsonResponse, HttpResponse
from django.views import View
from billing.services.main import initialize_payment
from billing.services.models import PaymentDetails, PaymentResultUpdate
from billing.services.payments import PaymentProcessor
from billing.services.repository import DjangoRepository
from yookassa.domain.notification import WebhookNotification


class InitializePayment(View):

    http_method_names = ['get']

    @staticmethod
    def payment_handler(request):
        p = PaymentDetails(
            user_id=request.Get.get('user_id'),
            subscription_id=request.Get.get('subscription_id'),
            auto_pay=request.Get.get('auto_pay'),
        )
        result = initialize_payment(PaymentProcessor, p, DjangoRepository)
        return JsonResponse(result.__dict__)


class UpdatePaymentInfo(View):

    http_method_names = ['post']

    @staticmethod
    def yukassa_web_hook_handler(request):

        event_json = json.loads(request.body)
        notification_object = WebhookNotification(event_json)
        payment = notification_object.object
        p = PaymentResultUpdate(
            id=payment.id,
            status=payment.status,
            last_card_digits=payment.payment_method.card.last4,
            auto_pay_id='',
        )
        return HttpResponse(status=200)
