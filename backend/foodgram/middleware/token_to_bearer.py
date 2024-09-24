"""Конверт Token to Berer файл."""


class TokenToBearerMiddleware:
    """Главный класс."""

    def __init__(self, get_response):
        """Конверт Token to Berer."""
        self.get_response = get_response

    def __call__(self, request):
        """Конверт Token to Berer."""
        # Изменяем заголовок запроса
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header and auth_header.startswith('Token '):
            request.META['HTTP_AUTHORIZATION'] = 'Bearer ' + auth_header[6:]

        response = self.get_response(request)
        return response
