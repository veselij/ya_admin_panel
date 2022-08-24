import json

from django.http import JsonResponse, HttpResponse
from django.views import View
from django.shortcuts import redirect
from billing.services.main import initialize_payment, process_post_payment_update
from billing.services.models import PaymentDetails
from billing.services.payments import YookassaPaymentProcessor
from billing.services.repository import DjangoRepository


class InitializePayment(View):

    http_method_names = ['get']

    @staticmethod
    def payment_handler(request):
        p = PaymentDetails(
            user_id=request.Get.get('user_id'),
            subscription_id=request.Get.get('subscription_id'),
            auto_pay=request.Get.get('auto_pay'),
            return_url=redirect('/admin').url,
        )
        result = initialize_payment(YookassaPaymentProcessor, p, DjangoRepository)
        return JsonResponse(result.__dict__)


class UpdatePaymentInfo(View):

    http_method_names = ['post']

    @staticmethod
    def yukassa_web_hook_handler(request):
        event_json = json.loads(request.body)
        p = YookassaPaymentProcessor().confirmation_process(data=event_json)
        process_post_payment_update(p, DjangoRepository)
        return HttpResponse(status=200)
