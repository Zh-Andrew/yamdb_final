from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Genre, Review, Title, User

from api_yamdb.settings import ADMIN_EMAIL

from .filters import TitleFilter
from .mixins import ListCreateDestroyViewSet
from .permissions import (IsAdminModeratorAuthorOnly, IsAdminOnly,
                          IsAdminOrReadOnly)
from .serializers import (AdminSerializer, CategorySerializer,
                          CommentSerializer, GenresSerializer,
                          ObtainTokenSerializer, ReviewSerializer,
                          SignupSerializer, TitlesPostSerializer,
                          TitlesSerializer, UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    """
    Администратор может просматривать и редактировать все поля любого другого
    пользователя. Эндпоинты:
    /users/ - доступ ко всем пользователям;
    /users/{username} - доступ к конкретному пользователя по username;
    /users/&search=username - поиск пользователя по username.
    Обычный пользователь может просматривать и редактировать свои данные.
    Эндпоинты:
    /users/me/ - доступ к текущему пользователю (поле 'role' изменить нельзя)
    """
    queryset = User.objects.all().order_by('id')
    serializer_class = AdminSerializer
    lookup_field = 'username'
    permission_classes = (IsAdminOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(detail=False,
            methods=['get', 'patch', ],
            url_path='me',
            permission_classes=(permissions.IsAuthenticated,)
            )
    def get_current_user(self, request):
        serializer = UserSerializer(request.user)
        if request.method == 'PATCH':
            if request.user.is_admin:
                serializer = AdminSerializer(
                    request.user, data=request.data, partial=True
                )
            else:
                serializer = UserSerializer(
                    request.user, data=request.data, partial=True
                )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_200_OK)


class APISignup(APIView):
    """
    Создание пользователя при POST-запросе по уникальным значениям
    username и email.
    Отправка confirmation_code на email пользователя, введенного при создании.
    Повторная отправка кода подтверждения на email пользователя
    при возможной утере первоначального.
    Эндпоинты:
    /auth/signup/
    """
    permission_classes = [AllowAny, ]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, created = User.objects.get_or_create(
            **serializer.validated_data
        )
        email = serializer.validated_data['email']
        send_mail(
            f'{user.username}, направляем ваш код подтверждения на YaMDB',
            f'Код подтверждения: {user.confirmation_code}',
            ADMIN_EMAIL,
            [email, ]
        )
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class APIObtainToken(APIView):
    """
    Получения JWT-токена пользователем при POST-запросе параметров
    username и confirmation_code.
    Эндпоинты:
    /auth/token/
    """
    permission_classes = [AllowAny, ]

    def post(self, request):
        serializer = ObtainTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        user = get_object_or_404(User, username=username)
        confirmation_code = serializer.validated_data['confirmation_code']
        if confirmation_code != user.confirmation_code:
            return Response(
                'Вы ввели неверный код подтверждения',
                status=status.HTTP_400_BAD_REQUEST
            )
        token = AccessToken.for_user(user)
        return Response(
            {'token': str(token)},
            status=status.HTTP_201_CREATED
        )


class CommentViewSet(viewsets.ModelViewSet):
    """
        Комментарии
        Эндпоинты:
        /titles/<title_id>/reviews/<review_id>/comments/
                - все комментарии к данному ревью
        /titles/<title_id>/reviews/<review_id>/comments/<comment_id>/
                - конкретный комментарий
        """
    serializer_class = CommentSerializer
    permission_classes = [IsAdminModeratorAuthorOnly, ]

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs['review_id'],
                                   title=self.kwargs['title_id'])
        return review.comments.all().order_by('id')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,
                        review=get_object_or_404(Review,
                                                 id=self.kwargs['review_id']))


class ReviewViewSet(viewsets.ModelViewSet):
    """
           Ревью
           Эндпоинты:
           /titles/<title_id>/reviews/
                   - все ревью к данному произведению
           /titles/<title_id>/reviews/<review_id>/
                   - конкретный ревью к данному произведению
           """
    serializer_class = ReviewSerializer
    permission_classes = [IsAdminModeratorAuthorOnly, ]

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        return title.reviews.all().order_by('id')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,
                        title=get_object_or_404(Title,
                                                id=self.kwargs['title_id']))


class CategoriesViewSet(ListCreateDestroyViewSet):
    """
    Получение списка категорий (для всех)
    Создание категории (только админ).
    Эндпоинты:
    /categories/
    """
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly, ]
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'slug'
    search_fields = ('name',)


class GenresViewSet(ListCreateDestroyViewSet):
    """
    Получение списка жанров (для всех)
    Создание жанров (только админ).
    Эндпоинты:
    /genres/
    """
    queryset = Genre.objects.all().order_by('id')
    serializer_class = GenresSerializer
    permission_classes = [IsAdminOrReadOnly, ]
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'slug'
    search_fields = ('name',)


class TitlesViewSet(viewsets.ModelViewSet):
    """
    Получение списка произведений (для всех).
    Cоздание произведений (только админ).
    Получение информации о произведении (для всех).
    Эндпоинты:
    /titles/
    /titles/{titles_id}/
    """
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).all().order_by('id')
    permission_classes = [IsAdminOrReadOnly, ]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitlesSerializer
        return TitlesPostSerializer
