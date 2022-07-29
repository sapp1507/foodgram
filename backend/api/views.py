import io

from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from recipes.models import Ingredient, Recipe, Tag
from users.models import Subscription, User

from .filters import IngredientSearchFilterBackend, RecipeFilterBackend
from .mixins import CreateDeleteMixin, ListViewSet
from .paginators import PageLimitPaginator
from .permissions import RecipesPermissions
from .serializers import (AddRecipeSerializer, IngredientSerializer,
                          RecipeSerializer, TagSerializer,
                          UserRecipeSerializer)
from .utils import get_response_as_error


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [IngredientSearchFilterBackend]
    search_fields = ['^name']
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [RecipesPermissions]
    pagination_class = PageLimitPaginator
    filter_backends = [RecipeFilterBackend]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return AddRecipeSerializer


class ShoppingCartViewSet(viewsets.ViewSet, CreateDeleteMixin):
    permission_classes = [permissions.IsAuthenticated]

    def get_pdf(self, request):
        user = request.user

        recipes = user.shopping_cart.all()

        queryset = Ingredient.objects.filter(
            ingredient_count__recipe__in=recipes
        ).values('name', 'measurement_unit').annotate(
            count=(Sum('ingredient_count__amount')))

        pdfmetrics.registerFont(TTFont(
            'Arkhip',
            'data/arkhip_font.ttf',
            'UTF-8'
        ))

        buffer = io.BytesIO()

        page = canvas.Canvas(buffer)
        page.setFont('Arkhip', size=32)
        page.drawString(150, 800, 'Список покупок')
        page.setFont('Arkhip', size=18)
        height = 760

        for i, (ingredient) in enumerate(queryset, 1):
            page.drawString(
                55,
                height,
                f'{i}. {ingredient["name"]}: {ingredient["count"]} '
                f'{ingredient["measurement_unit"]}'
            )
            height -= 30

        page.showPage()
        page.save()
        buffer.seek(0)
        return FileResponse(
            buffer, as_attachment=True, filename='Список покупок.pdf'
        )

    def create(self, request, id_recipe):
        attribute = 'shopping_cart'
        return self.custom_create(request, id_recipe, attribute)

    def destroy(self, request, id_recipe):
        attribute = 'shopping_cart'
        return self.custom_destroy(request, id_recipe, attribute)


class FavoriteViewSet(viewsets.ViewSet, CreateDeleteMixin):

    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, id_recipe):
        attribute = 'favorite'
        return self.custom_create(request, id_recipe, attribute)

    def destroy(self, request, id_recipe):
        attribute = 'favorite'
        return self.custom_destroy(request, id_recipe, attribute)


class AllSubscribedViewSet(ListViewSet):
    serializer_class = UserRecipeSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageLimitPaginator

    def get_queryset(self):
        return User.objects.filter(
            following__user=self.request.user)


class SubscribeViewSet(viewsets.ViewSet):

    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, id_user):
        if id_user == request.user.id:
            return get_response_as_error(
                'Нельзя подписаться на самого себя',
                status.HTTP_400_BAD_REQUEST
            )
        author = get_object_or_404(User, pk=id_user)
        if request.user.follower.filter(author=author).exists():
            return get_response_as_error(
                'Вы уже подписаны на этого автора',
                status.HTTP_400_BAD_REQUEST
            )

        Subscription.objects.create(user=request.user, author=author)
        serializer = UserRecipeSerializer(author, context={'request': request})
        return Response(serializer.data, status.HTTP_201_CREATED)

    def destroy(self, request, id_user):

        author = get_object_or_404(User, pk=id_user)

        if not request.user.follower.filter(author=author).exists():
            return get_response_as_error(
                'Вы не подписаны на этого автора',
                status.HTTP_400_BAD_REQUEST
            )

        subscribe = request.user.follower.filter(author=author)
        subscribe.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
