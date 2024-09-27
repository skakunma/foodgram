"""Настройка админки."""
from django.contrib import admin
from .models import (
    Recipe, Tag, RecipeIngredient, Ingredient,
    Subscription, FavoriteRecipe, ShoppingCart
)
from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email',
                    'is_staff', 'date_joined')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'date_joined')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка для модели Tag."""
    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}  # Автозаполнение slug


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка для модели Ingredient."""
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('measurement_unit',)


class RecipeIngredientInline(admin.TabularInline):
    """Инлайн для отображения ингредиентов в рецепте."""
    model = RecipeIngredient
    extra = 1  # Количество пустых строк для добавления


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка для модели Recipe."""
    list_display = ('id', 'name', 'author', 'cooking_time', 'data_time')
    search_fields = ('name', 'author__username')
    list_filter = ('tags', 'cooking_time')
    inlines = [RecipeIngredientInline]  # Включаем инлайн для ингредиентов
    raw_id_fields = ('author',)  # Улучшает производительность для большого количества пользователей


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    """Админка для модели FavoriteRecipe."""
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админка для модели ShoppingCart."""
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user', 'recipe')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Админка для модели Subscription."""
    list_display = ('id', 'user', 'subscribed_to')
    search_fields = ('user__username', 'subscribed_to__username')
    list_filter = ('user', 'subscribed_to')
