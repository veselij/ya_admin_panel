from django.urls import include, path

url_patterns = [
    path('v1', include('billing.api.v1.urls'))
]