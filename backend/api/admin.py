from django.contrib import admin
from .models import (User, Recipe, Tag, RecipeIngredient, Ingredient,
                     Subscription, FavoriteRecipe, ShoppingCart)

admin.site.register(User)
admin.site.register(Recipe)
admin.site.register(Tag)
admin.site.register(RecipeIngredient)
admin.site.register(Ingredient)
admin.site.register(Subscription)
admin.site.register(FavoriteRecipe)
admin.site.register(ShoppingCart)
