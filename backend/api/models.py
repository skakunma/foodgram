"""Модели для api."""
from django.db import models
from users.models import User

class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)

    def __str__(self):
        """Возвращает name."""
        return self.name


class Ingredient(models.Model):
    """Молдель ингредиентов."""

    name = models.CharField(max_length=256)
    measurement_unit = models.CharField(max_length=256)

    def __str__(self):
        """Возвращает id."""
        return str(self.id)


class Recipe(models.Model):
    """Молдель рецептов."""

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    text = models.TextField()
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient')
    tags = models.ManyToManyField(Tag)
    cooking_time = models.PositiveIntegerField()
    image = models.ImageField(upload_to='recipes/images/')
    short_link = models.CharField(max_length=50, unique=True, blank=True,
                                  null=True)
    is_favorited = models.BooleanField(default=False)
    is_in_shopping_cart = models.BooleanField(default=False)
    data_time = models.DateTimeField(auto_now_add=True)


class RecipeIngredient(models.Model):
    """Молдель рецептов и ингредиентов(связная)."""

    recipe = models.ForeignKey(Recipe, related_name='recipe_ingredients',
                               on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()


class FavoriteRecipe(models.Model):
    """Таблица избранного."""

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='favorite_recipes')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='favorited_by')

    class Meta:
        """Мета."""

        unique_together = ('user', 'recipe')


class ShoppingCart(models.Model):
    """Таблица корзины."""

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='shopping_cart')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='in_shopping_cart')

    class Meta:
        """Мета."""

        unique_together = ('user', 'recipe')


class Subscription(models.Model):
    """Таблица подписок."""

    user = models.ForeignKey(User, related_name='subscriptions',
                             on_delete=models.CASCADE)
    subscribed_to = models.ForeignKey(User, related_name='subscribers',
                                      on_delete=models.CASCADE)

    class Meta:
        """Мета."""

        unique_together = ('user', 'subscribed_to')
