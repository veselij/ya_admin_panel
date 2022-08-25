import json
from http import HTTPStatus
from typing import Any
from uuid import UUID

from django.apps import apps
from django.http import HttpRequest, JsonResponse
from django.http.response import HttpResponseBase
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from billing.services.exceptions import (
    PaymentProcessorAlreadyPayed,
    PaymentProcessorNotAvailable,
    PaymentProcessorPaymentCanceled,
    PaymentProcessorUnknownResponse,
    SubscriptionDoesNotExist,
)
from billing.services.main import initialize_payment, process_post_payment_update
from billing.services.models import PaymentDetails
from billing.services.repository import DjangoRepository
from billing.utils.security import check_token
from config import settings


class InitializePayment(View):

    http_method_names = ["post"]

    @csrf_exempt
    @check_token
    def dispatch(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponseBase:
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        post_body = json.loads(request.body)
        try:
            payment_details = PaymentDetails(
                user_id=UUID(post_body.get("user_id")),
                subscription_id=UUID(post_body.get("subscription_id")),
                auto_pay=bool(int(post_body.get("auto_pay"))),
                idempotent_key=UUID(post_body.get("idempotent_key")),
                return_url=settings.AFTER_PAYMENT_URL,
            )
        except (KeyError, ValueError) as e:
            settings.logger.exception("Bad request %s", e)
            return JsonResponse(
                {"error": e.__class__.__name__}, status=HTTPStatus.BAD_REQUEST
            )

        payment_processor = apps.get_app_config("billing").payment_processor  # type: ignore

        try:
            result = initialize_payment(
                payment_processor, payment_details, DjangoRepository()
            )
        except SubscriptionDoesNotExist as e:
            settings.logger.exception("Bad request %s", e)
            return JsonResponse(
                {"error": e.__class__.__name__}, status=HTTPStatus.BAD_REQUEST
            )
        except PaymentProcessorNotAvailable as e:
            settings.logger.exception("Payment provider not available %s", e)
            return JsonResponse(
                {"error": e.__class__.__name__}, status=HTTPStatus.REQUEST_TIMEOUT
            )
        except PaymentProcessorAlreadyPayed as e:
            settings.logger.exception("Already payed %s", e)
            return JsonResponse(
                {"error": e.__class__.__name__}, status=HTTPStatus.ALREADY_REPORTED
            )
        except PaymentProcessorPaymentCanceled as e:
            settings.logger.exception("Payment canceled %s", e)
            return JsonResponse(
                {"error": e.__class__.__name__}, status=HTTPStatus.ALREADY_REPORTED
            )

        return JsonResponse({"payment_url": result.url})


class UpdatePaymentInfo(View):

    http_method_names = ["post"]

    @csrf_exempt
    def dispatch(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponseBase:
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        print(request.body)
        post_body = json.loads(request.body)
        payment_processor = apps.get_app_config("billing").payment_processor  # type: ignore
        try:
            payment_response = payment_processor.get_payment_result(post_body)
        except PaymentProcessorUnknownResponse as e:
            print(post_body)
            return JsonResponse(
                {"error": e.__class__.__name__}, status=HTTPStatus.BAD_REQUEST
            )

        process_post_payment_update(payment_response, DjangoRepository())
        return JsonResponse({}, status=HTTPStatus.OK)
