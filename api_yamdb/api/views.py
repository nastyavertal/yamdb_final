from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Review, Title

from api_yamdb.settings import EMAIL_HOST

from .filters import TitleFilter
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsOwnerModeratorAdminOrReadOnly)
from .serializers import (CategorySerializer, ClassificationSerializer,
                          CommentSerializer, FeedbackSerializer,
                          GenreSerializer, GetConfirmationCodeSerializer,
                          GetTitleSerializer, GetTokenSerializer,
                          PersonalPageSerializer, PostTitleSerializer,
                          ReviewSerializer, UserSerializer)

User = get_user_model()


class SignUpViewSet(APIView):
    """Вью для регистрации пользователя.
    Создает пользователя с заданными 'username' и 'email',
    направляет на указанный 'email' письмо с 'confirmation_code'
    """
    http_method_names = ['post', ]
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = GetConfirmationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user, created = User.objects.get_or_create(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email']
            )

        except IntegrityError:
            return Response(
                {'error': (
                    'Пользователь с таким username '
                    'или email уже зарегистрирован'
                )},
                status=status.HTTP_400_BAD_REQUEST
            )

        send_mail(
            subject='Код подтверждения',
            message=(f'Ваш код подтверждения '
                     f'{default_token_generator.make_token(user)}'),
            from_email=EMAIL_HOST,
            recipient_list=[user.email],
            fail_silently=False
        )

        return Response(
            serializer.validated_data,
            status=status.HTTP_200_OK
        )


class TokenObtainView(APIView):
    """Вью-сет для получения JWToken"""
    http_method_names = ['post', ]
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User,
            username=serializer.validated_data['username']
        )
        if default_token_generator.check_token(
                user,
                serializer.validated_data['confirmation_code']
        ):
            access_token = RefreshToken.for_user(user).access_token
            return Response(
                {"token": str(access_token)},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {"error": "Не верный код подтверждения"},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserViewSet(viewsets.ModelViewSet):
    """Вью-сет для получения списка всех
    пользователей/пользователя по 'username' и их поиска
    с пагинацей."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    pagination_class = LimitOffsetPagination
    search_fields = ('username',)
    ordering = ('username',)

    @action(detail=False,
            methods=['get', 'patch'],
            permission_classes=(permissions.IsAuthenticated,),
            url_path='me')
    def personal_page_view(self, request):
        """Метод для доступа к персональной странице."""
        if request.method == 'GET':
            serializer = PersonalPageSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = PersonalPageSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class ClassificationViewSet(
    CreateModelMixin,
    ListModelMixin,
    DestroyModelMixin,
    GenericViewSet
):
    """Базовый вьюсет для получения списка, создания и удаления объекта
    абстрактной модели `core:ClassificationModel`."""
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    pagination_class = LimitOffsetPagination
    serializer_class = ClassificationSerializer


class CategoryViewSet(ClassificationViewSet):
    """Вью-сет для модели `reviews:Category`. Создает пагинированное множество
    категорий для просмотра. Чтение доступно всем,
    создание и редактирование только администрации."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(ClassificationViewSet):
    """Вью-сет для модели `reviews:Genre`. Создает пагинированное множество
    жанров для просмотра. Чтение доступно всем,
    создание и редактирование только администрации."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class FeedbackViewSet(viewsets.ModelViewSet):
    """Базовый CRUD для абстрактной модели `core:ClassificationModel`."""
    permission_classes = (IsOwnerModeratorAdminOrReadOnly,)
    pagination_class = LimitOffsetPagination
    serializer_class = FeedbackSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Вью-сет для модели `reviews:Title`. Создает пагинированное множество
    произведений для просмотра. Чтение доступно всем,
    создание и редактирование только администрации."""
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    serializer_class = PostTitleSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return GetTitleSerializer
        return PostTitleSerializer


class ReviewViewSet(FeedbackViewSet):
    """Вью-сет для отзывов на произведения `reviews:Reviews`.
    Создает пагинированное множество отзывов для просмотра
    или один отзыв для просмотра и/или изменений.
    Изменения доступны автору отзыва и администрации."""
    serializer_class = ReviewSerializer

    def _get_title_or_404(self):
        """Внутренний метод, возвращает объект `reviews:Title` из запроса
        по первичному ключу или исключение `Http404`."""
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self._get_title_or_404().reviews.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self._get_title_or_404()
        )


class CommentViewSet(FeedbackViewSet):
    """Вью-сет для комментариев отзывов на произведения `reviews:Comments`.
    Создает пагинированное множество комментариев для просмотра
    или один комментарий для просмотра и/или изменений.
    Изменения доступны автору комментария и администрации."""
    serializer_class = CommentSerializer

    def _get_review_or_404(self):
        """Внутренний метод, возвращает объект `reviews:Reviews`
        из запроса по первичным ключам или исключение `Http404`."""
        return get_object_or_404(
            Review,
            id=self.kwargs.get('review_id')
        )

    def get_queryset(self):
        return self._get_review_or_404().comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self._get_review_or_404()
        )
