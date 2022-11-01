"""
Views for the book APIs.
"""

from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.decorators import action

from core.models import (
    Book,
    Genre,
    Author,
    Language,
    BookShelf,
    Publisher,
    Review
)
from book import serializers


class BookViewSet(viewsets.ModelViewSet):
    """View for manage book APIs."""
    serializer_class = serializers.BookDetailSerializer
    queryset = Book.objects.all()
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        """Instantiates and returns the list of permissions for view."""
        if self.action == 'list' or self.action == 'retrieve' \
                or self.action == 'reviews':
            permission_classes = [AllowAny]
        elif self.action == 'create_review':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """retrieve recipes for authenticated user."""
        return self.queryset.order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.BookSerializer

        return self.serializer_class

    @action(detail=True, methods=['post'],
            serializer_class=serializers.ReviewSerializer,
            url_path='create-review')
    def create_review(self, request, pk=None):
        book = self.get_object()
        user = self.request.user
        serializer = serializers.ReviewSerializer(data=request.data)

        if serializer.is_valid():
            Review.objects.create(
                user=user,
                book=book,
                comment=serializer.validated_data['comment'],
                value=serializer.validated_data['value']
            )
            return Response(status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                            status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'],
            serializer_class=serializers.ReviewDetailSerializer)
    def reviews(self, request, pk=None):
        book = self.get_object()
        reviews = Review.objects.all().filter(book=book) \
            .order_by('-book__title')

        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)


class BaseBookAttrViewSet(mixins.DestroyModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    """Base ViewSet for book attributes."""
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        """Instantiates and returns the list of permissions for view."""
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Return query filtered by id."""
        return self.queryset.order_by('-name')


class GenreViewSet(BaseBookAttrViewSet):
    """Manage genres in database."""
    serializer_class = serializers.GenreSerializer
    queryset = Genre.objects.all()


class AuthorViewSet(BaseBookAttrViewSet):
    """Manage authors in database."""
    serializer_class = serializers.AuthorSerializer
    queryset = Author.objects.all()


class LanguageViewSet(BaseBookAttrViewSet):
    """Manage languages in database."""
    serializer_class = serializers.LanguageSerializer
    queryset = Language.objects.all()


class BookShelfViewSet(BaseBookAttrViewSet):
    """Manage bookshelves in database."""
    serializer_class = serializers.BookShelfSerializer
    queryset = BookShelf.objects.all()


class PublisherViewSet(BaseBookAttrViewSet):
    """Manage publishers in database."""
    serializer_class = serializers.PublisherSerializer
    queryset = Publisher.objects.all()


class ReviewViewSet(BaseBookAttrViewSet):
    """View for manage reviews APIs."""
    serializer_class = serializers.ReviewDetailSerializer
    queryset = Review.objects.all()

    def get_permissions(self):
        """Instantiates and returns the list of permissions for view."""
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """retrieve recipes fro authenticated user."""
        return self.queryset.order_by('-book__title')

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)
