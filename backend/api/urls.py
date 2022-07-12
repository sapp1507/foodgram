import djoser.conf
from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import TagViewSet

router = DefaultRouter()
router.register(r'tags', TagViewSet)


urlpatterns = [
    path('', include('djoser.urls')),
    path('', include(router.urls)),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
