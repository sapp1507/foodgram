import io

from django.contrib.auth import get_user_model
from django.db.models import F
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfgen import canvas
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from recipes.models import Ingredient, Recipe, Tag
from users.models import Subscription

from .filters import IngredientSearchFilterBackend, RecipeFilterSet
from .paginators import PageLimitPaginator
from .permissions import IsAuthorOrReadOnly
from .serializers import (AddRecipeSerializer, IngredientSerializer,
                          RecipeSerializer, SmallRecipeSerializer,
                          TagSerializer, UserSerializer, UserRecipeSerializer)
from .mixins import ListViewSet

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    # permission_classes = [permissions.AllowAny]
    filter_backends = [IngredientSearchFilterBackend]
    search_fields = ['^name']
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrReadOnly, permissions.IsAdminUser]
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
            queryset = queryset.filter(shopping_carts=self.request.user)

        author_id = params.get('author')
        if author_id is not None and User.objects.filter(pk=author_id).exists():
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
        return Response(
            {'errors': f'Рецепт "{recipe.name}" уже добавлен'},
            status.HTTP_400_BAD_REQUEST
        )

    def custom_destroy(self, request, id_recipe, attribute):
        recipe = get_object_or_404(Recipe, pk=id_recipe)
        queryset = getattr(request.user, attribute)
        if queryset.filter(id=recipe.id).exists():
            queryset.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': f'Рецепта "{recipe.name}" нету в списке'}
        )


class ShoppingCartViewSet(viewsets.ViewSet, CreateDeleteMixin):
    permission_classes = [permissions.IsAuthenticated]

    def get_pdf(self, request):
        buffer = io.BytesIO()

        pdf = canvas.Canvas(buffer)

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

        for key, value in print_ingredients.items():
            pdf.drawString(100, 100, f'{key}: {value["amount"]} '
                                     f'{value["unit"]}')
        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        return FileResponse(
            buffer, as_attachment=True, filename='Список покупок.pdf')

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
    # queryset = request.user.follower.all()
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
            return self._get_response(
                'Нельзя подписаться на самого себя',
                status.HTTP_400_BAD_REQUEST
            )
        author = get_object_or_404(User, pk=id_user)
        if request.user.follower.filter(author=author).exists():
            return self._get_response(
                'Вы уже подписаны на этого автора',
                status.HTTP_400_BAD_REQUEST
            )

        Subscription.objects.create(user=request.user, author=author)
        serializer = UserRecipeSerializer(author, context={'request': request})
        return Response(serializer.data, status.HTTP_201_CREATED)

    def destroy(self, request, id_user):

        author = get_object_or_404(User, pk=id_user)

        if not request.user.follower.filter(author=author).exists():
            return self._get_response(
                'Вы не подписаны на этого автора',
                status.HTTP_400_BAD_REQUEST
            )

        subscribe = request.user.follower.filter(author=author)
        subscribe.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
