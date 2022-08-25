from django.contrib import admin

from billing.models import Transaction, User, UserSubscription


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = ("id",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):

    list_display = ("user", "subscription", "status")


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):

    list_display = ("user", "auto_pay", "subscription_valid_to")
