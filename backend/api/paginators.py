"""Классы панигинации."""
from rest_framework import pagination
from rest_framework.response import Response


class RecipePagination(pagination.PageNumberPagination):
    """Пагинация для рецептов."""

    page_size = 6
    page_size_query_param = 'limit'
    page_query_param = 'page'
    max_page_size = 100

    def get_paginated_response(self, data):
        """Возвращает ответ с информацией о пагинации."""
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })


class UserSubscriptionPagination(pagination.PageNumberPagination):
    """Пагинация для подписок пользователей."""

    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100

    def get_paginated_response(self, data):
        """Возвращает ответ с информацией о пагинации."""
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })
