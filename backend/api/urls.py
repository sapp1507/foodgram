from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import (FavoriteViewSet, IngredientViewSet, RecipeViewSet,
                    ShoppingCartViewSet, TagViewSet, SubscribeViewSet,
                    AllSubscribedViewSet)

router = DefaultRouter()
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)
# router.register(r'users/subscriptions', AllSubscribedViewSet)


urlpatterns = [
    path('users/subscriptions/', AllSubscribedViewSet.as_view(
        {'get': 'list'})),
    path('recipes/download_shopping_cart/', ShoppingCartViewSet.as_view(
        {'get': 'get_pdf'}
    ), name='download_shopping_cart'),

    path('', include('djoser.urls')),
    path('', include(router.urls)),

    path('users/<int:id_user>/subscribe/', SubscribeViewSet.as_view(
        {'post': 'create', 'delete': 'destroy'}
    )),

    path('recipes/<int:id_recipe>/shopping_cart/', ShoppingCartViewSet.as_view(
        {'post': 'create', 'delete': 'destroy'}
    ), name='shopping_cart'),

    path('recipes/<int:id_recipe>/favorite/', FavoriteViewSet.as_view(
        {'post': 'create', 'delete': 'destroy'}
    ), name='favorite'),

    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
