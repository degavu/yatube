from django.utils import timezone


def year(request):
    """Добавляет в контекст текущий год"""
    now_year = timezone.now().year
    return {
        'year': now_year
    }
