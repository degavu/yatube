from django.core.paginator import Paginator

from django.conf import settings as yatube_conf


def page_objects(request,
                 all_objects,
                 div_counts=yatube_conf.COUNT_POSTS_IN_PAGE):
    """Функция влзвращет объекты на оду страницу"""
    paginator = Paginator(all_objects, div_counts)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
