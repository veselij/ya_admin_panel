from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import billing.services.models as service_models
from movies.models import Subscription, TimeStampedMixin, UUIDMixin


class Status(models.TextChoices):
    FAILED = "failed", _("failed")
    PENDING = "pending", _("pending")
    SUCCESS = "succeed", _("succeed")


class User(UUIDMixin, TimeStampedMixin):
    subscription = models.ManyToManyField(Subscription, through="UserSubscription")

    class Meta:
        db_table = 'billing"."user'
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def to_domain(self):
        return service_models.User(
            id=self.id,
        )

    def __str__(self) -> str:
        return str(self.id)


class Transaction(UUIDMixin, TimeStampedMixin):
    user = models.ForeignKey("User", on_delete=models.CASCADE, verbose_name=_("user"))
    subscription = models.ForeignKey(
        "movies.Subscription", on_delete=models.CASCADE, verbose_name=_("subscription")
    )
    status = models.TextField(_("status"), choices=Status.choices)

    class Meta:
        db_table = 'billing"."transaction'
        verbose_name = _("transaction")
        verbose_name_plural = _("transactions")

    def to_domain(self):
        return service_models.Transaction(
            id=self.id,
            user=self.user,
            subscription=self.subscription,
            status=self.status,
        )

    @staticmethod
    def update_from_domain(transaction: service_models.Transaction):
        subscription = Subscription.objects.get(id=transaction.subscription.id)
        user = User.objects.get(id=transaction.user.id)
        tr_object, _ = Transaction.objects.get_or_create(
            id=transaction.id, subscription=subscription, user=user
        )
        tr_object.status = transaction.status
        tr_object.save()

    def __str__(self) -> str:
        return str(self.id)


class UserSubscription(UUIDMixin, TimeStampedMixin):
    user = models.ForeignKey("User", on_delete=models.CASCADE, verbose_name=_("user"))
    subscription = models.ForeignKey(
        "movies.Subscription", on_delete=models.CASCADE, verbose_name=_("subscription")
    )
    auto_pay = models.BooleanField(_("auto_pay"), default=False)
    subscription_valid_to = models.DateTimeField(_("valid_to"), null=True)
    last_card_digits = models.IntegerField(_("last_card_digits"), null=True)
    auto_pay_id = models.TextField(_("auto_pay_id"), null=True)

    class Meta:
        db_table = 'billing"."user_subscription'
        indexes = [
            models.Index(fields=("user", "subscription"), name="user_subsription_idx")
        ]
        verbose_name = _("user subscription")
        verbose_name_plural = _("user subscriptions")

    def to_domain(self):
        return service_models.UserSubscription(
            id=self.id,
            user=self.user,
            subscription=self.subscription,
            auto_pay=self.auto_pay,
            subscription_valid_to=timezone.make_naive(self.subscription_valid_to),
            last_card_digits=self.last_card_digits,
            auto_pay_id=self.auto_pay_id,
        )

    @staticmethod
    def update_from_domain(user_subscription: service_models.UserSubscription):
        subscription = Subscription.objects.get(id=user_subscription.subscription.id)
        user = User.objects.get(id=user_subscription.user.id)

        us_object, _ = UserSubscription.objects.get_or_create(
            id=user_subscription.id, subscription=subscription, user=user
        )
        us_object.auto_pay = user_subscription.auto_pay
        us_object.auto_pay_id = user_subscription.auto_pay_id
        us_object.last_card_digits = user_subscription.last_card_digits
        us_object.subscription_valid_to = user_subscription.subscription_valid_to
        us_object.save()

    def __str__(self) -> str:
        return f"{self.user.id} subscription {self.subscription.id}"
