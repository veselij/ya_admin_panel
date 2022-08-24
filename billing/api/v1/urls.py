from django.urls import path
from .views import InitializePayment

url_patterns = [
    path('/billing', InitializePayment.as_view())
]