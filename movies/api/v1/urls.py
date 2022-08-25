from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path

from movies.api.v1 import views

urlpatterns = [
    path("movies", staff_member_required(views.MoviesListApi.as_view())),
    path("movies/<uuid:pk>", staff_member_required(views.MoviesDetailApi.as_view())),
]
