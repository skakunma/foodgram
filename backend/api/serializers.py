from rest_framework import serializers
from .models import (
    User, Recipe, Ingredient, Tag, RecipeIngredient,
    FavoriteRecipe, ShoppingCart, Subscription
)


class RegistrationSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'last_name',
                  'first_name', 'id']


class LoginSerializer(serializers.Serializer):

    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password']
        extra_kwargs = {'password': {'write_only': True}}


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'avatar']


class UserSubscribedSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source='recipes.count',
                                             read_only=True)
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', 'avatar']

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user,
                                               subscribed_to=obj).exists()
        return False

    def get_recipes(self, obj):
        # Получаем рецепты, созданные пользователем
        recipes = Recipe.objects.filter(
            author=obj)[:self.context.get('recipes_limit', None)]
        return RecipeSerializer(recipes, many=True).data


class SetPasswordSerializer(serializers.Serializer):

    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, data):
        user = self.context['request'].user
        current_password = data.get('current_password')

        if user.password != current_password:
            raise serializers.ValidationError({
                'current_password': 'Current password is incorrect.'})

        return data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class RecipeIngredientSerializer(serializers.ModelSerializer):

    ingredient = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ['ingredient', 'amount']


class RecipeSerializer(serializers.ModelSerializer):

    ingredients = RecipeIngredientSerializer(many=True,
                                             write_only=True)
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all(),
                                              write_only=True)

    class Meta:
        model = Recipe
        fields = ['id', 'author', 'name', 'text', 'ingredients',
                  'tags', 'cooking_time', 'image']

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            ingredient = ingredient_data['ingredient']
            amount = ingredient_data['amount']
            RecipeIngredient.objects.create(recipe=recipe,
                                            ingredient=ingredient,
                                            amount=amount)

        recipe.tags.set(tags_data)
        return recipe
    def update(self, instance, validated_data):
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
            RecipeIngredient.objects.create(recipe=instance,
                                            ingredient=ingredient_data
                                            ['ingredient'], amount=amount)

        instance.tags.set(tags_data)
        return instance


class RecipeDetailSerializer(serializers.ModelSerializer):

    ingredients = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ['id', 'author', 'name', 'text', 'ingredients', 'tags',
                  'cooking_time', 'image',
                  'is_favorited', 'is_in_shopping_cart']

    def get_ingredients(self, obj):
        ingredients = obj.recipe_ingredients.all()
        return [{
            "id": ingredient.ingredient.id,
            "name": ingredient.ingredient.name,
            "measurement_unit": ingredient.ingredient.measurement_unit,
            "amount": ingredient.amount
        } for ingredient in ingredients]

    def get_tags(self, obj):
        return [{"id": tag.id, "name": tag.name,
                 "slug": tag.slug} for tag in obj.tags.all()]

    def get_author(self, obj):
        return {
            "id": obj.author.id,
            "username": obj.author.username,
            "first_name": obj.author.first_name,
            "last_name": obj.author.last_name,
            "avatar": obj.author.avatar.url if obj.author.avatar else None,
            "is_subscribed": obj.author.is_subscribed
        }

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return FavoriteRecipe.objects.filter(user=request.user,
                                                 recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ShoppingCart.objects.filter(user=request.user,
                                               recipe=obj).exists()
        return False


class AvatarSerializer(serializers.ModelSerializer):

    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = User
        fields = ['avatar']
