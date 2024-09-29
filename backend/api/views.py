"""views для api."""
from rest_framework import generics, status, permissions, viewsets
from .models import (Tag, Recipe, Ingredient, RecipeIngredient,
                     ShoppingCart, FavoriteRecipe, Subscription)
from users.models import User
from .serializers import (RegistrationSerializer, LoginSerializer,
                          UserSerializer, SetPasswordSerializer, TagSerializer,
                          RecipeSerializer, RecipeDetailSerializer,
                          IngredientSerializer, UserSubscribedSerializer)

from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .paginators import RecipePagination, UserSubscriptionPagination
import json
from rest_framework import filters
from django.core.files.base import ContentFile
from django.http import HttpResponseRedirect
import base64
import uuid
from django.urls import reverse
from .filters import RecipeFilter


class LoginAPIView(generics.CreateAPIView):
    """Класс для обработки запроса входа пользователя.

    Валидация учетных данных и создание токена для аутентификации.
    """

    model = User
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        """Обработка POST-запроса (вход)."""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            # Аутентификация пользователя
            user = User.objects.filter(email=email).first()

            if user.password == password:
                # Создаем или получаем токен для пользователя
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    'auth_token': str(token.key),
                }, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Invalid credentials'},
                                status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(generics.RetrieveAPIView):
    """Класс для получения информации о текущем пользователе.

    Возвращает данные аутентифицированного пользователя.
    """

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Возвращает request.user."""
        return self.request.user


class LogoutAPIView(generics.GenericAPIView):
    """Класс для обработки выхода пользователя.

    Блокирует refresh токен для завершения сессии.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Обработка POST-запроса (выход)."""
        try:
            # Получаем токен из заголовка Authorization
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Token '):
                token_key = auth_header.split(' ')[1]
                token = Token.objects.filter(key=token_key).first()

                if token:
                    token.delete()  # Удаляем токен
                    return Response({'detail': 'Successfully logged out.'},
                                    status=status.HTTP_200_OK)
                else:
                    return Response({'detail': 'Invalid token.'},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'detail': 'Token is required in the Authorization header.'
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)


class SetPasswordAPIView(generics.UpdateAPIView):
    """Класс для изменения пароля пользователя.

    Обрабатывает POST запрос для обновления пароля.
    """

    serializer_class = SetPasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Обработка post запроса."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        new_password = serializer.validated_data['new_password']
        user.password = new_password
        user.save()
        return Response({'detail': 'Password has been updated.'},
                        status=status.HTTP_200_OK)


class UserViewSet(viewsets.ViewSet):
    """Класс для работы с пользователями.

    Обрабатывает GET и POST запросы для получения и создания пользователей.
    """

    def list(self, request):
        """Обработка GET запроса."""
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Обработка GET запроса по pk."""
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def create(self, request):
        """Обработка POST зароса."""
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class TagViewSet(viewsets.ViewSet):
    """Класс для работы с тегами.

    Обрабатывает GET запросы для получения списка тегов и информации
    о конкретном теге.
    """

    def list(self, request):
        """Обработка get запроса."""
        queryset = Tag.objects.all()
        serializer = TagSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """GET по pk."""
        tag = get_object_or_404(Tag, pk=pk)
        serializer = TagSerializer(tag)
        return Response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    """Класс для работы с рецептами.

    Обрабатывает CRUD операции для рецептов, включая фильтрацию,
    создание и управление избранным и корзиной.
    """

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = RecipePagination
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Возвращает соответствующий сериализатор.

        в зависимости от действия.
        """
        if self.action in ['retrieve', 'list']:
            return RecipeDetailSerializer
        return RecipeSerializer

    def get_link(self, request, id=None):
        """Создает короткую ссылку на рецепт.

        Если короткая ссылка еще не создана, генерирует новую.
        """
        recipe = get_object_or_404(Recipe, id=id)

        if not recipe.short_link:
            short_link = str(uuid.uuid4())[:8]
            recipe.short_link = short_link
            recipe.save()

        short_url = f"http://localhost:8080/s/{recipe.short_link}"
        return Response({"short-link": short_url})

    def redirect_to_recipe(self, request, short_link):
        """Перенаправляет на детальную страницу рецепта по короткой ссылке."""
        recipe = get_object_or_404(Recipe, short_link=short_link)
        return HttpResponseRedirect(reverse('recipe-detail',
                                            kwargs={'id': recipe.id}))

    def get_queryset(self):
        """Возвращает отфильтрованный список рецептов на.

        основе параметров запроса.
        """
        queryset = super().get_queryset()
        # Остальные параметры фильтрации, если нужно
        return queryset

    def create(self, request, *args, **kwargs):
        """Создает новый рецепт.

        Сохраняет изображение и ингредиенты, привязывает автора.
        """
        if request.user.is_authenticated:
            request.data['author'] = request.user.id
            base64_image = request.data['image']
            if base64_image.startswith('data:image/'):
                header, imgstr = base64_image.split(';base64,')
                ext = header.split('/')[1]
                file_name = f'recipe.{ext}'
                image = ContentFile(base64.b64decode(imgstr), name=file_name)
                request.data['image'] = image
            request.data['ingredients'] = [{
                "ingredient": ingredient['id'],
                "amount": ingredient['amount']} for ingredient in
                request.data['ingredients']]

            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                recipe = serializer.save()

                ingredients = RecipeIngredient.objects.filter(recipe=recipe)
                ingredient_list = [{
                    "id": ingredient.ingredient.id,
                    "name": ingredient.ingredient.name,
                    "measurement_unit": ingredient.ingredient.measurement_unit,
                    "amount": ingredient.amount
                } for ingredient in ingredients]

                tags = recipe.tags.all()
                tag_list = [{
                    "id": tag.id,
                    "name": tag.name,
                    "slug": tag.slug
                } for tag in tags]

                response_data = serializer.data
                response_data['ingredients'] = ingredient_list
                response_data['tags'] = tag_list
                response_data['author'] = {
                    "id": recipe.author.id,
                    "username": recipe.author.username
                }

                return Response(response_data, status=201)
            return Response(serializer.errors, status=400)
        return Response({'detail': 'Not authenticated'},
                        status=status.HTTP_401_UNAUTHORIZED)

    def update(self, request, *args, **kwargs):
        """Обновляет существующий рецепт.

        Изменяет изображение, ингредиенты и теги.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        if not request.user.is_authenticated:
            return Response({'detail': 'Not authenticated'},
                            status=status.HTTP_401_UNAUTHORIZED)

        request.data['author'] = request.user.id
        base64_image = request.data.get('image')

        if base64_image and base64_image.startswith('data:image/'):
            header, imgstr = base64_image.split(';base64,')
            ext = header.split('/')[1]
            file_name = f'recipe.{ext}'
            image = ContentFile(base64.b64decode(imgstr), name=file_name)
            request.data['image'] = image

        request.data['ingredients'] = [
            {"ingredient": ingredient['id'],
             "amount": ingredient['amount']} for ingredient in
            request.data['ingredients']
        ]

        serializer = self.get_serializer(instance, data=request.data,
                                         partial=partial)

        if serializer.is_valid():
            recipe = serializer.save()

            RecipeIngredient.objects.filter(recipe=recipe).delete()

            for ingredient_data in request.data['ingredients']:
                ingredient_id = ingredient_data['ingredient']
                amount = ingredient_data['amount']
                ingredient = Ingredient.objects.get(id=ingredient_id)
                RecipeIngredient.objects.create(recipe=recipe,
                                                ingredient=ingredient,
                                                amount=amount)

            tags = request.data.get('tags', [])
            recipe.tags.set(tags)

            ingredients = RecipeIngredient.objects.filter(recipe=recipe)
            ingredient_list = [{
                "id": ingredient.ingredient.id,
                "name": ingredient.ingredient.name,
                "measurement_unit": ingredient.ingredient.measurement_unit,
                "amount": ingredient.amount
            } for ingredient in ingredients]

            tags = recipe.tags.all()
            tag_list = [{
                "id": tag.id,
                "name": tag.name,
                "slug": tag.slug
            } for tag in tags]

            response_data = serializer.data
            response_data['ingredients'] = ingredient_list
            response_data['tags'] = tag_list
            response_data['author'] = {
                "id": recipe.author.id,
                "username": recipe.author.username
            }

            return Response(response_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, id=None):
        """Добавляет или удаляет рецепт из списка покупок."""
        recipe = get_object_or_404(Recipe, id=id)

        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=request.user,
                                           recipe=recipe).exists():
                return Response({"detail": "Рецепт уже в списке покупок."},
                                status=status.HTTP_400_BAD_REQUEST)

            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            return Response({
                "id": recipe.id,
                "name": recipe.name,
                "image": recipe.image.url if recipe.image else None,
                "cooking_time": recipe.cooking_time
            }, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            cart_item = ShoppingCart.objects.filter(user=request.user,
                                                    recipe=recipe).first()
            if not cart_item:
                return Response({"detail": "Рецепт не найден в списке покупок."
                                 },
                                status=status.HTTP_400_BAD_REQUEST)

            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        """Скачивает список покупок в текстовом формате."""
        shopping_cart_items = ShoppingCart.objects.filter(
            user=request.user).select_related('recipe')
        if not shopping_cart_items:
            return Response({"detail": "Список покупок пуст."},
                            status=status.HTTP_404_NOT_FOUND)

        response_content = "Название:"
        for item in shopping_cart_items:
            response_content += f" {item.recipe.name}, "

        response = Response(response_content, content_type='text/plain')
        response['Content-Disposition'] = ('attachment;'
                                           'filename="shopping_cart.txt"')
        return response

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, id=None):
        """Добавляет или удаляет рецепт из избранного."""
        recipe = get_object_or_404(Recipe, id=id)

        if request.method == 'POST':
            if FavoriteRecipe.objects.filter(user=request.user,
                                             recipe=recipe).exists():
                return Response({"detail": "Рецепт уже в избранном."},
                                status=status.HTTP_400_BAD_REQUEST)

            FavoriteRecipe.objects.create(user=request.user, recipe=recipe)
            return Response({
                "id": recipe.id,
                "name": recipe.name,
                "image": recipe.image.url if recipe.image else None,
                "cooking_time": recipe.cooking_time
            }, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            favorite_item = FavoriteRecipe.objects.filter(user=request.user,
                                                          recipe=recipe
                                                          ).first()
            if not favorite_item:
                return Response({"detail": "Рецепт не найден в избранном."},
                                status=status.HTTP_400_BAD_REQUEST)

            favorite_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def avatar_view(request):
    """Обрабатывает обновление и удаление аватара пользователя."""
    user = request.user

    if request.method == 'PUT':
        data = json.loads(request.body)
        base64_image = data.get('avatar')
        user_profile = User.objects.get(username=request.user)
        user_profile.set_avatar(base64_image, request.user)
        user_profile.save()

        return JsonResponse({'status': 'success'})

    elif request.method == 'DELETE':
        if user.avatar:
            user.avatar.delete(save=False)
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({"detail": "Avatar not found."},
                        status=status.HTTP_404_NOT_FOUND)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Класс для работы с ингредиентами.

    Позволяет выполнять GET запросы для получения списка ингредиентов.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['^name']


class UserSubscriptionViewSet(viewsets.GenericViewSet):
    """Класс для управления подписками пользователей.

    Обрабатывает подписки на других пользователей.
    """

    permission_classes = [permissions.IsAuthenticated]
    pagination_class = UserSubscriptionPagination

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        """Возвращает список подписок текущего пользователя."""
        subscriptions = Subscription.objects.filter(
            user=request.user).select_related('subscribed_to')
        page = self.paginate_queryset(subscriptions)

        if page is not None:
            serializer = UserSubscribedSerializer([sub.subscribed_to for sub in
                                                  page],
                                                  many=True,
                                                  context={'request': request})

            return self.get_paginated_response(serializer.data)

        serializer = UserSubscribedSerializer([sub.subscribed_to for sub in
                                               subscriptions],
                                              many=True,
                                              context={'request': request})

        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, id=None):
        """Подписка или отписка от пользователя."""
        user_to_subscribe = get_object_or_404(User, id=id)

        if request.method == 'POST':
            if user_to_subscribe == request.user:
                return Response({
                    "detail": "Нельзя подписаться на самого себя."},
                    status=400)

            Subscription.objects.get_or_create(user=request.user,
                                               subscribed_to=user_to_subscribe)
            return Response(UserSubscribedSerializer(user_to_subscribe,
                                                     context={
                                                         'request': request}
                                                     ).data, status=201)

        elif request.method == 'DELETE':
            subscription = Subscription.objects.filter(
                user=request.user, subscribed_to=user_to_subscribe).first()
            if subscription:
                subscription.delete()
                return Response(status=204)
            return Response({"detail": "Не подписан."}, status=400)
