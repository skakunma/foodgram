"""Серлизаторы для моделей."""
from rest_framework import serializers
from .models import (
    User, Recipe, Ingredient, Tag, RecipeIngredient,
    FavoriteRecipe, ShoppingCart, Subscription
)


class RegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации нового пользователя."""

    password = serializers.CharField(write_only=True)

    class Meta:
        """Мета информация о сериализаторе."""

        model = User
        fields = [
            'username', 'email', 'password', 'last_name',
            'first_name', 'id'
        ]


class LoginSerializer(serializers.Serializer):
    """Сериализатор для аутентификации пользователя."""

    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    class Meta:
        """Мета информация о сериализаторе."""

        model = User
        fields = ['email', 'password']
        extra_kwargs = {'password': {'write_only': True}}


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для представления информации о пользователе."""

    class Meta:
        """Мета информация о сериализаторе."""

        model = User
        fields = [
            'id', 'email', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar'
        ]


class UserSubscribedSerializer(serializers.ModelSerializer):
    """Сериализатор для представления подписки пользователя."""

    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source='recipes.count',
                                             read_only=True)
    recipes = serializers.SerializerMethodField()

    class Meta:
        """Мета информация о сериализаторе."""

        model = User
        fields = [
            'id', 'email', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes',
            'recipes_count', 'avatar'
        ]

    def get_is_subscribed(self, obj):

        """Проверяет, подписан ли текущий пользователь
        на данного пользователя.
        """

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user, subscribed_to=obj
            ).exists()
        return False

    def get_recipes(self, obj):
        """Получает рецепты, созданные пользователем, с
        ограничением по количеству.
        """

        recipes = Recipe.objects.filter(
            author=obj)[:self.context.get('recipes_limit', None)]
        return RecipeSerializer(recipes, many=True).data


class SetPasswordSerializer(serializers.Serializer):
    """Сериализатор для изменения пароля пользователя."""

    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, data):
        """Проверяет, что текущий пароль введен правильно."""
        user = self.context['request'].user
        current_password = data.get('current_password')

        if not user.check_password(current_password):
            raise serializers.ValidationError({
                'current_password': 'Current password is incorrect.'
            })

        return data


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для представления ингредиента."""

    class Meta:
        """Мета информация о сериализаторе."""

        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для представления тега."""

    class Meta:
        """Мета информация о сериализаторе."""

        model = Tag
        fields = ['id', 'name', 'slug']


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для представления ингредиентов в рецепте."""

    ingredient = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        """Мета информация о сериализаторе."""

        model = RecipeIngredient
        fields = ['ingredient', 'amount']


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов."""

    ingredients = RecipeIngredientSerializer(many=True, write_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), write_only=True)

    class Meta:
        """Мета информация о сериализаторе."""

        model = Recipe
        fields = [
            'id', 'author', 'name', 'text', 'ingredients',
            'tags', 'cooking_time', 'image'
        ]

    def create(self, validated_data):
        """Создает новый рецепт и связывает его с ингредиентами и тегами."""
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            ingredient = ingredient_data['ingredient']
            amount = ingredient_data['amount']
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=ingredient, amount=amount)

        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        """Обновляет существующий рецепт и связывает его с новыми ингредиентами и тегами."""
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)
        instance.save()

        instance.recipe_ingredients.all().delete()
        for ingredient_data in ingredients_data:
            amount = ingredient_data['amount']
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredient_data['ingredient'],
                amount=amount
            )

        instance.tags.set(tags_data)
        return instance


class RecipeDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального представления рецепта."""

    ingredients = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        """Мета информация о сериализаторе."""

        model = Recipe
        fields = [
            'id', 'author', 'name', 'text', 'ingredients',
            'tags', 'cooking_time', 'image', 'is_favorited',
            'is_in_shopping_cart'
        ]

    def get_ingredients(self, obj):
        """Получает ингредиенты, связанные с рецептом."""
        ingredients = obj.recipe_ingredients.all()
        return [{
            "id": ingredient.ingredient.id,
            "name": ingredient.ingredient.name,
            "measurement_unit": ingredient.ingredient.measurement_unit,
            "amount": ingredient.amount
        } for ingredient in ingredients]

    def get_tags(self, obj):
        """Получает теги, связанные с рецептом."""
        return [{
            "id": tag.id, "name": tag.name, "slug": tag.slug
        } for tag in obj.tags.all()]

    def get_author(self, obj):
        """Получает информацию об авторе рецепта."""
        return {
            "id": obj.author.id,
            "username": obj.author.username,
            "first_name": obj.author.first_name,
            "last_name": obj.author.last_name,
            "avatar": obj.author.avatar.url if obj.author.avatar else None,
            "is_subscribed": obj.author.is_subscribed
        }

    def get_is_favorited(self, obj):
        """Проверяет, добавлен ли рецепт в избранное пользователем."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return FavoriteRecipe.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        """Проверяет, находится ли рецепт в корзине покупок пользователя."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        return False


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для получения информации об аватаре пользователя."""

    avatar = serializers.ImageField(read_only=True)

    class Meta:
        """Мета информация о сериализаторе."""

        model = User
        fields = ['avatar']
