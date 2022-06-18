from http import HTTPStatus

from django.shortcuts import render


def page_not_found(request, exception):
    """Вывод страницы 404."""
    template = 'core/404.html'
    context = {
        'path': request.path,
    }
    return render(request, template, context, status=HTTPStatus.NOT_FOUND)


def server_error(request):
    """Вывод страницы 500."""
    template = 'core/500.html'
    return render(request, template, status=HTTPStatus.INTERNAL_SERVER_ERROR)


def permission_denied(request, exception):
    """Вывод страницы 403."""
    template = 'core/403.html'
    return render(request, template, status=HTTPStatus.FORBIDDEN)


def csrf_failure(request, reason=''):
    """Вывод страницы 403."""
    return render(request, 'core/403csrf.html')
