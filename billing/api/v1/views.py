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
from billing.services.main import (
    cancel_subscription,
    initialize_payment,
    process_post_payment_update,
)
from billing.services.models import CancelationDetails, PaymentDetails
from billing.services.repository.django_repositury import DjangoRepository
from billing.utils import errormessages
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
            )
            idempotent_key = post_body.get("idempotent_key")
            return_url = settings.AFTER_PAYMENT_URL
        except (KeyError, ValueError) as e:
            settings.logger.exception(errormessages.API_REQUEST, e)
            return JsonResponse(
                {"error": e.__class__.__name__}, status=HTTPStatus.BAD_REQUEST
            )

        payment_processor = apps.get_app_config("billing").payment_processor  # type: ignore

        try:
            result = initialize_payment(
                payment_processor,
                payment_details,
                DjangoRepository(),
                return_url,
                idempotent_key,
            )
        except (
            SubscriptionDoesNotExist,
            PaymentProcessorNotAvailable,
            PaymentProcessorAlreadyPayed,
            PaymentProcessorPaymentCanceled,
        ) as e:
            settings.logger.exception(errormessages.API_REQUEST, e)
            return JsonResponse(
                {"error": e.__class__.__name__}, status=HTTPStatus.BAD_REQUEST
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
        post_body = json.loads(request.body)
        payment_processor = apps.get_app_config("billing").payment_processor  # type: ignore
        try:
            payment_response = payment_processor.get_payment_result(post_body)
        except PaymentProcessorUnknownResponse as e:
            return JsonResponse(
                {"error": e.__class__.__name__}, status=HTTPStatus.BAD_REQUEST
            )

        process_post_payment_update(payment_response, DjangoRepository())
        return JsonResponse({}, status=HTTPStatus.OK)


class CancelPayment(View):

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
            cancelation_details = CancelationDetails(
                user_id=UUID(post_body.get("user_id")),
                subscription_id=UUID(post_body.get("subscription_id")),
            )
        except (KeyError, ValueError) as e:
            settings.logger.exception(errormessages.API_REQUEST, e)
            return JsonResponse(
                {"error": e.__class__.__name__}, status=HTTPStatus.BAD_REQUEST
            )

        cancel_subscription(cancelation_details, DjangoRepository())
        return JsonResponse({}, status=HTTPStatus.OK)
