from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import TagViewSet, IngredientViewSet

router = DefaultRouter()
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)


urlpatterns = [
    path('', include('djoser.urls')),
    path('', include(router.urls)),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
