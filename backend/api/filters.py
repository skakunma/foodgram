"""filters."""
from django_filters import rest_framework as filters
from .models import Recipe


class RecipeFilter(filters.FilterSet):
    """Фильтр для рецептов."""

    is_favorited = filters.BooleanFilter(field_name='is_favorited',
                                         method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='filter_is_in_shopping_cart')
    author = filters.NumberFilter(field_name='author')
    tags = filters.CharFilter(field_name='tags__slug', lookup_expr='in')
    date_from = filters.DateTimeFilter(field_name='data_time',
                                       lookup_expr='gte')
    date_to = filters.DateTimeFilter(field_name='data_time', lookup_expr='lte')

    class Meta:
        """Мета."""

        model = Recipe
        fields = []

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрация по избранным рецептам."""
        return queryset.filter(is_favorited=value)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрация по рецептам в корзине."""
        return queryset.filter(is_in_shopping_cart=value)
