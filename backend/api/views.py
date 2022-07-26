import io

from django.contrib.auth import get_user_model
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Ingredient, Recipe, Tag
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from users.models import Subscription

from .filters import IngredientSearchFilterBackend, RecipeFilterSet
from .mixins import ListViewSet
from .paginators import PageLimitPaginator
from .permissions import RecipesPermissions
from .serializers import (AddRecipeSerializer, IngredientSerializer,
                          RecipeSerializer, SmallRecipeSerializer,
                          TagSerializer, UserRecipeSerializer)

User = get_user_model()


def _get_response(message, status_response):
    return Response(
        {'errors': message},
        status_response
    )


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
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilterSet

    def get_queryset(self):
        queryset = Recipe.objects.all()
        params = self.request.query_params

        is_favorited = params.get('is_favorited')
        if is_favorited is not None and is_favorited == '1':
            queryset = queryset.filter(favorite=self.request.user)

        is_shopping_cart = params.get('is_in_shopping_cart')
        if is_shopping_cart is not None and is_shopping_cart == '1':
            queryset = queryset.filter(shopping_carts__id=self.request.user.id)

        author_id = params.get('author')
        if author_id is not None and User.objects.filter(
                pk=author_id).exists():
            queryset = queryset.filter(author_id=author_id)

        return queryset

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return AddRecipeSerializer


class CreateDeleteMixin:
    def custom_create(self, request, id_recipe, attribute):
        recipe = get_object_or_404(Recipe, pk=id_recipe)
        queryset = getattr(request.user, attribute)
        if not queryset.filter(id=recipe.id).exists():
            queryset.add(recipe)
            serializer = SmallRecipeSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status.HTTP_201_CREATED)
        return _get_response(
            f'Рецепт "{recipe.name}" уже добавлен',
            status.HTTP_400_BAD_REQUEST
        )

    def custom_destroy(self, request, id_recipe, attribute):
        recipe = get_object_or_404(Recipe, pk=id_recipe)
        queryset = getattr(request.user, attribute)
        if queryset.filter(id=recipe.id).exists():
            queryset.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return _get_response(
            f'Рецепта "{recipe.name}" нету в списке',
            status.HTTP_400_BAD_REQUEST
        )


class ShoppingCartViewSet(viewsets.ViewSet, CreateDeleteMixin):
    permission_classes = [permissions.IsAuthenticated]

    def get_pdf(self, request):
        user = request.user

        ingredients = user.shopping_cart.all().values(
            _name=F('ingredients__ingredient__name'),
            _amount=F('ingredients__amount'),
            _unit=F('ingredients__ingredient__measurement_unit')
        )

        print_ingredients = {}
        for ingredient in ingredients:
            if ingredient['_name'] in print_ingredients:
                print_ingredients[ingredient['_name']]['amount'] += (
                    ingredient['_amount'])
            else:
                print_ingredients[ingredient['_name']] = {
                    'amount': ingredient['_amount'],
                    'unit': ingredient['_unit']
                }
        wishlist = []
        for key, value in print_ingredients.items():
            wishlist.append(
                f'{key}: {value["amount"]} {value["unit"]}'
            )

        pdfmetrics.registerFont(TTFont(
            'Arkhip',
            'data/arkhip_font.ttf',
            'UTF-8'
        ))

        response = HttpResponse(wishlist, content_type='application/pdf')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_list.pdf"')

        page = canvas.Canvas(response)
        page.setFont('Arkhip', size=32)
        page.drawString(200, 800, 'Список покупок')
        page.setFont('Arkhip', size=18)
        height = 760
        for i, (name, data) in enumerate(print_ingredients.items(), 1):
            page.drawString(55, height, (f'{i}. {name} - {data["amount"]} '
                                         f'{data["measurement_unit"]}'))
            height -= 30
        page.showPage()
        page.save()
        return response

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
            following__user=self.request.user).all()


class SubscribeViewSet(viewsets.ViewSet):

    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, id_user):
        if id_user == request.user.id:
            return _get_response(
                'Нельзя подписаться на самого себя',
                status.HTTP_400_BAD_REQUEST
            )
        author = get_object_or_404(User, pk=id_user)
        if request.user.follower.filter(author=author).exists():
            return _get_response(
                'Вы уже подписаны на этого автора',
                status.HTTP_400_BAD_REQUEST
            )

        Subscription.objects.create(user=request.user, author=author)
        serializer = UserRecipeSerializer(author, context={'request': request})
        return Response(serializer.data, status.HTTP_201_CREATED)

    def destroy(self, request, id_user):

        author = get_object_or_404(User, pk=id_user)

        if not request.user.follower.filter(author=author).exists():
            return _get_response(
                'Вы не подписаны на этого автора',
                status.HTTP_400_BAD_REQUEST
            )

        subscribe = request.user.follower.filter(author=author)
        subscribe.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
