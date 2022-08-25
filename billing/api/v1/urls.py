from django.urls import path

from .views import CancelPayment, InitializePayment, UpdatePaymentInfo

urlpatterns = [
    path("billing/payment", InitializePayment.as_view()),
    path("billing/cancel", CancelPayment.as_view()),
    path("billing/paymentWebhookApi", UpdatePaymentInfo.as_view()),
]
