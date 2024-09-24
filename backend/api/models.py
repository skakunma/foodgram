"""Модели для api."""
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, UserManager
)
from django.core.validators import EmailValidator, RegexValidator
from django.db import models
from django.core.files.base import ContentFile
import base64


class User(AbstractBaseUser, PermissionsMixin):
    """Модель для пользователей."""

    email = models.EmailField(
        unique=True,
        validators=[EmailValidator(
            message="Введите корректный адрес электронной почты.")]
    )

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[RegexValidator(regex=r'^[\w.@+-]+$',
                                   message='Username должен быть формата'
                                           '^[w.@+-]+Z')]
    )
    password = models.CharField(max_length=120, )
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    is_subscribed = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='avatars', blank=True, null=True)
    REQUIRED_FIELDS = ['email', 'password', 'first_name', 'last_name']
    USERNAME_FIELD = 'username'
    is_staff = models.BooleanField(default=False)
    objects = UserManager()

    def __str__(self):
        """Возвращает username."""
        return self.username

    def set_avatar(self, base64_image, user):
        """base64 to file."""
        if base64_image.startswith('data:image/'):
            header, imgstr = base64_image.split(';base64,')
            ext = header.split('/')[1]
            file_name = f'avatar_{user}.{ext}'
            image = ContentFile(base64.b64decode(imgstr), name=file_name)
            self.avatar.save(file_name, image, save=True)


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
