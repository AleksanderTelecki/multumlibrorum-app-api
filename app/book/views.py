"""
Views for the book APIs.
"""

from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser, AllowAny

from core.models import Book, Genre, Author, Language, BookShelf
from book import serializers


class BookViewSet(viewsets.ModelViewSet):
    """View for manage book APIs."""
    serializer_class = serializers.BookDetailSerializer
    queryset = Book.objects.all()
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        """Instantiates and returns the list of permissions for view."""
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """retrieve recipes fro authenticated user."""
        return self.queryset.order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.BookSerializer

        return self.serializer_class


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
