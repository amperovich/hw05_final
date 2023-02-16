from django.conf import settings
from django.core.paginator import Page, Paginator
from django.db.models import QuerySet
from django.http import HttpRequest


def paginate(
    request: HttpRequest,
    queryset: QuerySet,
    objects_num: int = settings.PAGE_SIZE,
) -> Page:
    return Paginator(
        queryset.order_by('-pub_date'),
        objects_num,
    ).get_page(request.GET.get('page'))
