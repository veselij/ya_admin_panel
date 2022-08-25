from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("billing.api.urls")),
    path("api/", include("movies.api.urls")),
    path("__debug__/", include("debug_toolbar.urls")),
]
