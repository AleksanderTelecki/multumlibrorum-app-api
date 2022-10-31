"""
Serializers for book APIs
"""
from rest_framework import serializers
from core.models import Book, Genre, Author, Language


class GenreSerializer(serializers.ModelSerializer):
    """Genre Serializer."""

    class Meta:
        model = Genre
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']


class AuthorSerializer(serializers.ModelSerializer):
    """Author Serializer."""

    class Meta:
        model = Author
        fields = ['id', 'name']
        read_only_fields = ['id']


class LanguageSerializer(serializers.ModelSerializer):
    """Language Serializer."""

    class Meta:
        model = Language
        fields = ['id', 'name']
        read_only_fields = ['id']


class BookSerializer(serializers.ModelSerializer):
    """Serializer for books."""
    genres = GenreSerializer(many=True, required=False)
    authors = AuthorSerializer(many=True, required=False)
    languages = LanguageSerializer(many=True, required=False)

    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            'price',
            'created_at',
            'genres',
            'authors',
            'languages',
        ]
        read_only_fields = ['id']

    def _get_or_create_genres(self, genres, book):
        """Handle getting or creating genres as needed."""
        for genre in genres:
            genre_obj, created = Genre.objects.get_or_create(**genre)
            book.genres.add(genre_obj)

    def _get_or_create_authors(self, authors, book):
        """Handle getting or creating authors as needed."""
        for author in authors:
            author_obj, created = Author.objects.get_or_create(**author)
            book.authors.add(author_obj)

    def _get_or_create_languages(self, languages, book):
        """Handle getting or creating languages as needed."""
        for language in languages:
            language_obj, created = Language.objects.get_or_create(**language)
            book.languages.add(language_obj)


    def create(self, validated_data):
        """Create a book."""
        genres = validated_data.pop('genres', [])
        authors = validated_data.pop('authors', [])
        languages = validated_data.pop('languages', [])

        book = Book.objects.create(**validated_data)
        self._get_or_create_genres(genres, book)
        self._get_or_create_authors(authors, book)
        self._get_or_create_languages(languages, book)

        return book

    def update(self, instance, validated_data):
        """Update book."""
        genres = validated_data.pop('genres', None)
        authors = validated_data.pop('authors', None)
        languages = validated_data.pop('languages', None)

        if genres is not None:
            instance.genres.clear()
            self._get_or_create_genres(genres, instance)

        if authors is not None:
            instance.authors.clear()
            self._get_or_create_authors(authors, instance)

        if languages is not None:
            instance.languages.clear()
            self._get_or_create_languages(languages, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class BookDetailSerializer(BookSerializer):
    """Serializer for book detail view."""

    class Meta(BookSerializer.Meta):
        fields = BookSerializer.Meta.fields + [
            'isbn13',
            'publication_date',
            'available_quantity',
            'description'
        ]
