from django.core.exceptions import ValidationError
from django.forms import IntegerField
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import Category, Genre, Title, Comment, Review, User


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категорий, модели Category."""

    class Meta:
        model = Category
        exclude = ('id', )


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанров, модели Genre."""

    class Meta:
        model = Genre
        exclude = ('id', )


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор произведений, модели Title."""

    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category',
        )


class PostTitleSerializer(serializers.ModelSerializer):
    """Сериализатор метода POST, модели Title. """

    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all(),
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        many=False,
        queryset=Category.objects.all(),
    )

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category',
        )

    def validate_year(self, data):
        if data > timezone.now().year:
            raise ValidationError(
                'Нельзя добавлять произведения, которые еще не вышли',
            )
        return data


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор модели отзывов, модели Review. """
    author = SlugRelatedField(slug_field='username', read_only=True)
    score = IntegerField(min_value=1, max_value=10)

    def validate(self, attrs):
        context = self.context['view']
        title = get_object_or_404(Title, id=context.kwargs.get('title_id'))
        user = self.context.get('request').user
        if Review.objects.filter(title=title, author=user).exists():
            if self.context['request'].method in ['POST']:
                raise serializers.ValidationError(
                    'Только один отзыв от пользователя!')
        return super().validate(attrs)

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date', 'score')
        model = Review
        read_only_fields = ['author']


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментариев, модели Comment. """

    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = '__all__'
        model = Comment
        read_only_fields = ['author']


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователей, модели User. """

    class Meta:
        model = User
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name',
                  'bio',
                  'role',
                  )


class AuthSerializer(serializers.ModelSerializer):
    """Сериализатор для аутентификации пользователя. """

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate_username(self, data):
        if data == 'me':
            raise ValidationError(
                message='Нельзя создать пользователя с username = me!')
        return data


class ObtainTokenSerializer(serializers.ModelSerializer):
    """Сериализатор для получения токена. """
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')
