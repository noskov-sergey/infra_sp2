from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.views import APIView

from api.filtres import TitleFilter
from api.mixins import ListPatchDestroyViewSet
from api.permissions import AdminOrReadOnly, IsAdminOnly, WriteOnlyAuthorOr
from api.pagination import CategoryGenrePagination
from api.serializers import (AuthSerializer, CategorySerializer,
                             CommentSerializer, GenreSerializer,
                             ObtainTokenSerializer, PostTitleSerializer,
                             ReviewSerializer, TitleSerializer,
                             UserSerializer)
from reviews.models import Category, Comment, Genre, Review, Title, User


class CategoryViewSet(ListPatchDestroyViewSet):
    """ModelViewSet для обработки эндпоинта /category/."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CategoryGenrePagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = [
        AdminOrReadOnly,
    ]


class GenreViewSet(ListPatchDestroyViewSet):
    """ViewSet для обработки эндпоинта /category/."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = CategoryGenrePagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = [
        AdminOrReadOnly,
    ]


class TitleViewSet(viewsets.ModelViewSet):
    """ModelViewSet для обработки эндпоинта /titles/."""

    queryset = Title.objects.all().annotate(
        rating=Avg('reviews__score'),
    ).order_by('name')
    serializer_class = TitleSerializer
    pagination_class = CategoryGenrePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = [
        AdminOrReadOnly,
    ]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitleSerializer
        return PostTitleSerializer


class ReviewsViewSet(viewsets.ModelViewSet):
    """ModelViewSet для обработки эндпоинта /reviews/."""

    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [
        WriteOnlyAuthorOr,
    ]

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        new_queryset = get_object_or_404(
            Title, id=title_id).reviews.all()
        return new_queryset

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        serializer.save(title_id=title_id, author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """ModelViewSet для обработки эндпоинта /comment/."""

    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [
        WriteOnlyAuthorOr,
    ]

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        get_object_or_404(Review, id=review_id)
        new_queryset = Comment.objects.filter(review_id=review_id)
        return new_queryset

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        get_object_or_404(Review, id=review_id)
        serializer.save(author=self.request.user,
                        review_id=review_id)


class UsersViewSet(viewsets.ModelViewSet):
    """ModelViewSet для обработки эндпоинта /users/."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    permission_classes = (
        IsAuthenticated,
        IsAdminOnly,
    )
    search_fields = ('username',)
    lookup_field = 'username'

    @action(
        methods=['get', 'patch'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='me',
    )
    def get_account_information(self, request):
        serializer = UserSerializer(self.request.user)
        if request.method == 'PATCH':
            user = self.request.user
            serializer = UserSerializer(
                user,
                data=request.data,
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            serializer.validated_data.pop('role', None)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_200_OK)


class APISignUp(APIView):
    """APIView для регистрации нового пользователя."""

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = AuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        user = serializer.save()
        mail_subject = 'Ваш код подтверждения'
        message = f'Код подтверждения - {user.confirmation_code}'

        send_mail(
            mail_subject,
            message,
            settings.EMAIL_FROM,
            (email, )
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


class APIToken(APIView):
    """APIView для получения токена"""

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = ObtainTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(
                username=serializer.validated_data['username']
            )
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if (
            serializer.validated_data['confirmation_code']
            == user.confirmation_code
        ):
            token = AccessToken.for_user(user)
            return Response(
                {'token': str(token)},
                status=status.HTTP_201_CREATED,
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)
