from django.urls import include, path

urlpatterns = [path("v1/", include("billing.api.v1.urls"))]
