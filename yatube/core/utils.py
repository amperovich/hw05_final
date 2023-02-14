from django.core.paginator import Page, Paginator
from django.db.models import QuerySet
from django.http import HttpRequest


def paginate(
    request: HttpRequest,
    queryset: QuerySet,
    objects_num: int,
) -> Page:
    paginator = Paginator(queryset, objects_num)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
