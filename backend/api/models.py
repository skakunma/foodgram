"""Модели для пользователей в API."""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)

    def __str__(self):
        """Возвращает name."""
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(max_length=256)
    measurement_unit = models.CharField(max_length=256)

    class Meta:
        """Мета."""

        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'],
                                    name='unique_name_measurement')
        ]

    def __str__(self):
        """Возвращает id."""
        return str(self.id)


class Recipe(models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    text = models.TextField()
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient')
    tags = models.ManyToManyField(Tag)
    cooking_time = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1,
                              message='Время приготовления'
                                      'должно быть больше 0.'),
            MaxValueValidator(300,
                              message='Максимальное время'
                                      'приготовления 300 минут.')
        ]
    )
    image = models.ImageField(upload_to='recipes/images/')
    short_link = models.CharField(max_length=50,
                                  unique=True,
                                  blank=True, null=True)
    is_favorited = models.BooleanField(default=False)
    is_in_shopping_cart = models.BooleanField(default=False)
    data_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Мета."""

        ordering = ['-data_time']


class RecipeIngredient(models.Model):
    """Молдель рецептов и ингредиентов(связная)."""

    recipe = models.ForeignKey(Recipe, related_name='recipe_ingredients',
                               on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()


class UserRecipe(models.Model):
    """Абстрактная модель для хранения пользовательских рецептов."""

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='%(class)s')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='%(class)s_related')

    class Meta:
        """Мета класс."""

        abstract = True  # Обозначает, что это абстрактный класс
        unique_together = ('user', 'recipe')


class FavoriteRecipe(UserRecipe):
    """Таблица избранного."""

    class Meta(UserRecipe.Meta):
        """Мета."""

        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class ShoppingCart(UserRecipe):
    """Таблица корзины."""

    class Meta(UserRecipe.Meta):
        """Мета."""

        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'


class Subscription(models.Model):
    """Таблица подписок."""

    user = models.ForeignKey(User, related_name='subscriptions',
                             on_delete=models.CASCADE)
    subscribed_to = models.ForeignKey(User, related_name='subscribers',
                                      on_delete=models.CASCADE)

    class Meta:
        """Мета."""

        unique_together = ('user', 'subscribed_to')
