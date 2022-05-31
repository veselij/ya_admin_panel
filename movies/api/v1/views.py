from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from movies.models import Filmwork, Roles


class MoviesApiMixin:
    """Mixin class to overide get_queryset method of parent classes."""

    model = Filmwork
    http_method_names = ['get']

    def get_queryset(self):
        return self.model.objects.prefetch_related(
            "genres", "persons", "subscriptions",
        ).values("id", "title", "description", "creation_date", "rating", "type").annotate(
            genres=ArrayAgg("genres__name", distinct=True),
            subscriptions=ArrayAgg("subscriptions__name", distinct=True),
            actors=ArrayAgg("persons__full_name", distinct=True, filter=Q(personfilmwork__role=Roles.actor)),
            directors=ArrayAgg("persons__full_name", distinct=True, filter=Q(personfilmwork__role=Roles.director)),
            writers=ArrayAgg("persons__full_name", distinct=True, filter=Q(personfilmwork__role=Roles.writer)),
        ).order_by("id")

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    """Class based List view API for Filmwork."""

    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, self.paginate_by)
        return {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': page.previous_page_number() if page.has_previous() else None,
            'next': page.next_page_number() if page.has_next() else None,
            'results': list(queryset),
        }


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    """Class based Detialed view for API for Filmwork."""

    def get_context_data(self, **kwargs):
        return self.object
