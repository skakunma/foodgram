"""Главный фвйл приложения."""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Класс."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
