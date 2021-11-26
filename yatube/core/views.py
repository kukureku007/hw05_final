# core/views.py
from django.shortcuts import render


def page_not_found(request, exception):
    """Страница не найдена"""
    context = {
        'path': request.path,
        'exception': exception,
    }

    return render(request, 'core/404.html', context, status=404)


def csrf_failure(request, reason=''):
    """Ошибка csrf"""
    return render(request, 'core/403csrf.html')


def server_error(request):
    """500 server error"""
    return render(request, 'core/500.html', status=500)


def permission_denied(request, exception):
    """Ошибка доступа"""
    return render(request, 'core/403.html', status=403)
