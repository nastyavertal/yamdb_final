from core.models import ClassificationModel, FeedbackModel
from core.validators import validate_username, validate_year
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    ROLES = (
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор'),
        (USER, 'Пользователь'),
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[validate_username, ],
        verbose_name='Имя пользователя',
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Биография',
    )
    role = models.CharField(
        max_length=max(len(role) for role, _ in ROLES),
        choices=ROLES,
        default=USER,
        verbose_name='Роль',
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Адрес электронной почты',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='username_unique_email',
            )
        ]
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'@{self.username}: {self.email}. {self.role}'

    @property
    def is_admin(self):
        return self.is_staff or self.role == self.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_user(self):
        return self.role == self.USER


class Category(ClassificationModel):
    """Модель хранит информацию о категориях произведений."""

    class Meta(ClassificationModel.Meta):
        verbose_name = 'Категория произведения'
        verbose_name_plural = 'Категории произведений'


class Genre(ClassificationModel):
    """Модель хранит информацию о жанрах произведений."""

    class Meta(ClassificationModel.Meta):
        verbose_name = 'Жанр произведения'
        verbose_name_plural = 'Жанры произведений'


class Title(models.Model):
    """Модель хранит информацию о произведениях."""
    name = models.TextField(
        verbose_name='Название произведения'
    )
    year = models.IntegerField(
        validators=(validate_year,),
        verbose_name='Год выпуска произведения'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание произведения'
    )
    category = models.ForeignKey(
        Category,
        related_name='titles',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория произведения'
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        verbose_name='Жанр произведения'
    )

    class Meta:
        ordering = ('-year', 'name',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'year'],
                name='unique_title'
            )
        ]

    def __str__(self):
        return self.name[:30]


class GenreTitle(models.Model):
    """В этой промежуточной модели описана связь title_id и genre_id."""
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        null=True,
        related_name='genre'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        null=True,
        related_name='titles'
    )

    class Meta:
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=['genre', 'title'],
                name='unique_genre_title'
            )
        ]

    def __str__(self):
        return f'"{self.title}" относится к жанру: {self.genre}'


class Review(FeedbackModel):
    """Модель хранит информацию об отзывах."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
    )
    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                1,
                message='Оценка не может быть ниже 1.'
            ),
            MaxValueValidator(
                10,
                message='Оценка не может быть выше 10.'
            )
        ]
    )

    class Meta(FeedbackModel.Meta):
        default_related_name = 'reviews'
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_title_author'
            ),
        ]

    def __str__(self):
        return (f'#{self.id} @{self.author.username} '
                f'написал {self.text[:30]}... о {self.title.name}')


class Comment(FeedbackModel):
    """Модель хранит информацию о комментариях к отзывам."""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв'
    )

    class Meta(FeedbackModel.Meta):
        default_related_name = 'comments'
        verbose_name = 'Комментарий к отзыву'
        verbose_name_plural = 'Комментарии к отзывам'

    def __str__(self):
        return (f'#{self.id} @{self.author.username} '
                f'написал {self.text[:30]}... об отзыве '
                f'@{self.review.author.username}')
