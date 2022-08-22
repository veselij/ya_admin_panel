from django.db import models
from django.utils.translation import gettext_lazy as _

from movies.models import UUIDMixin, TimeStampedMixin
import services.models as service_models


class Status(models.TextChoices):
    FAILED = 'failed', _('failed')
    PENDING = 'pending', _('pending')
    SUCCESS = 'succeed', _('succeed')


class Subscription(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_("name"), max_length=255)
    price = models.IntegerField(_("price"), max_length=16)
    period_days = models.IntegerField(_("period"), max_length=16)
    description = models.CharField(_("description"), max_length=32, blank=True)

    class Meta:
        db_table = "billing\".\"subscription"
        verbose_name = _("subscription")
        verbose_name_plural = _("subscriptions")

    def to_domain(self):
        return service_models.Subscription(
            id=self.id,
            name=self.name,
            price=self.price,
            period_days=self.period_days,
            description=self.description,
        )


class User(UUIDMixin, TimeStampedMixin):
    subscription = models.ManyToManyField(Subscription, through="UserSubscription")

    class Meta:
        db_table = "billing\".\"user"
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def to_domain(self):
        return service_models.User(
            id=self.id,
        )


class Transaction(UUIDMixin, TimeStampedMixin):
    user = models.ForeignKey("User", on_delete=models.CASCADE, verbose_name=_("user"))
    subscription = models.ForeignKey("Subscription", on_delete=models.CASCADE, verbose_name=_("subscription"))
    status = models.TextField(_('status'), choices=Status)

    class Meta:
        db_table = "billing\".\"subscription"
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
        tr_object = Transaction.objects.get_or_create(transaction.id)
        tr_object.user = User.objects.get_or_create(transaction.user.id)
        tr_object.subscription = Subscription.objects.get_or_create(transaction.subscription.id)
        tr_object.status = transaction.status
        tr_object.save()


class UserSubscription(UUIDMixin, TimeStampedMixin):
    user = models.ForeignKey("User", on_delete=models.CASCADE, verbose_name=_("user"))
    subscription = models.ForeignKey("Subscription", on_delete=models.CASCADE, verbose_name=_("subscription"))
    auto_pay = models.BooleanField(_('auto_pay'))
    subscription_valid_to = models.DateTimeField(_('valid_to'))
    active = models.BooleanField(_('active'), default=False)
    last_card_digits = models.IntegerField(_('last_card_digits'), max_length=4)
    auto_pay_id = models.TextField(_('auto_pay_id'), null=True, default=None)

    class Meta:
        db_table = "billing\".\"user_subscription"
        indexes = [models.Index(fields=("user", "subscription"), name="user_subsription_idx")]
        verbose_name = _("user subscription")
        verbose_name_plural = _("user subscriptions")

    def to_domain(self):
        return service_models.UserSubscription(
            id=self.id,
            user=self.user,
            subscription=self.subscription,
            auto_pay=self.auto_pay,
            subscription_valid_to=self.subscription_valid_to,
            active=self.active,
            last_card_digits=self.last_card_digits,
            auto_pay_id=self.auto_pay_id,
        )

    @staticmethod
    def update_from_domain(user_subscription: service_models.UserSubscription):
        us_object = UserSubscription.objects.get_or_create(user_subscription.id)
        us_object.user = User.objects.get_or_create(user_subscription.user.id)
        us_object.subscription = Subscription.objects.get_or_create(user_subscription.subscription.id)
        us_object.auto_pay = user_subscription.auto_pay
        us_object.auto_pay_id = user_subscription.auto_pay_id
        us_object.active = user_subscription.active
        us_object.last_card_digits = user_subscription.last_card_digits
        us_object.subscription_valid_to = user_subscription.subscription_valid_to
        us_object.save()
