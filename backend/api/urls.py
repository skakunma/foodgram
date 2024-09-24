from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(f'tags', views.TagViewSet, basename='tag')
router.register(f'recipes', views.RecipeViewSet, basename='recipe')
router.register(r'ingredients', views.IngredientViewSet, basename='ingredient')

urlpatterns = [
    path('auth/token/login/', views.LoginAPIView.as_view(), name='login'),
    path('users/me/', views.UserDetailView.as_view(), name='user-detail'),
    path('auth/token/logout/', views.LogoutAPIView.as_view(), name='logout'),
    path('recipes/<int:id>/get-link/', views.RecipeViewSet.as_view(
        {'get': 'get_link'}), name='recipe-get-link'),
    path('s/<str:short_link>/', views.RecipeViewSet.as_view(
        {'get': 'redirect_to_recipe'}), name='short-link-redirect'),
    path('recipes/<int:id>/shopping_cart/',
         views.RecipeViewSet.as_view({'post': 'shopping_cart',
                                      'delete': 'shopping_cart'}),
         name='shopping-cart'),
    path('recipes/download_shopping_cart/', views.RecipeViewSet.as_view(
        {'get': 'download_shopping_cart'}), name='download-shopping-cart'),
    path('recipes/<int:id>/favorite/', views.RecipeViewSet.as_view(
        {'post': 'favorite', 'delete': 'favorite'}), name='favorite'),
    path('users/subscriptions/', views.UserSubscriptionViewSet.as_view(
        {'get': 'subscriptions'}), name='user-subscriptions'),
    path('users/<int:id>/subscribe/', views.UserSubscriptionViewSet.as_view(
        {'post': 'subscribe', 'delete': 'subscribe'}),
        name='user-subscribe'),

    path('users/set_password/', views.SetPasswordAPIView.as_view(),
         name='set-password'),
    path('', include(router.urls)),
    path('users/me/avatar/', views.avatar_view, name='avatar')
]
