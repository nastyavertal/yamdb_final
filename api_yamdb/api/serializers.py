from core.models import ClassificationModel, FeedbackModel
from core.validators import validate_username, validate_year
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueValidator
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class GetConfirmationCodeSerializer(serializers.Serializer):
    """Проверяет username и email перед выдачей confirmation_code."""
    username = serializers.CharField(
        max_length=150,
        validators=[validate_username, ]
    )
    email = serializers.EmailField(
        max_length=254
    )


class GetTokenSerializer(serializers.Serializer):
    """Сериализатор для получения JWToken"""
    username = serializers.CharField(
        max_length=150,
        validators=[validate_username, ]
    )
    confirmation_code = serializers.CharField()


class ClassificationSerializer(serializers.ModelSerializer):
    """Сериализатор для модели `core:ClassificationModel`."""

    class Meta:
        model = ClassificationModel
        fields = ('name', 'slug')


class CategorySerializer(ClassificationSerializer):
    """Сериализатор для модели `reviews:Category`."""

    class Meta(ClassificationSerializer.Meta):
        model = Category


class GenreSerializer(ClassificationSerializer):
    """Сериализатор для модели `reviews:Genre`."""

    class Meta(ClassificationSerializer.Meta):
        model = Genre


class GetTitleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Title. Дополнительно расcчитывает
    среднее (rating) из оценок (score) связанной модели Reviews."""
    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description',
                  'genre', 'category')
        read_only_fields = ('__all__',)


class PostTitleSerializer(serializers.ModelSerializer):
    """Десериализатор для модели `reviews:Title`."""
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    year = serializers.IntegerField(validators=(validate_year,))

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'category', 'genre')


class FeedbackSerializer(serializers.ModelSerializer):
    """Сериализаторр для модели `core:FeedbackModel`."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = FeedbackModel


class ReviewSerializer(FeedbackSerializer):
    """Сериализатор для модели `reviews:Review`."""
    score = serializers.IntegerField(min_value=1, max_value=10)

    class Meta:
        exclude = ('title',)
        model = Review

    def validate(self, obj):
        """Проверка на уникальность отзыва от автора на произведение."""
        if (self.context['request'].method != 'PATCH'
            and Review.objects.filter(
                author=self.context['request'].user,
                title=get_object_or_404(
                    Title, id=self.context['view'].kwargs.get('title_id')
                )).exists()):
            raise serializers.ValidationError(
                'Вы уже оставляли отзыв на это произведение.'
            )
        return obj


class CommentSerializer(FeedbackSerializer):
    """Сериализатор для модели `reviews:Comment`."""

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели `reviews:User`."""
    username = serializers.CharField(
        max_length=150,
        validators=[
            validate_username,
            UniqueValidator(queryset=User.objects.all())
        ]
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')


class PersonalPageSerializer(serializers.ModelSerializer):
    """Сериализатор персональной страницы пользователя."""

    class Meta(UserSerializer.Meta):
        read_only_fields = ['role']
