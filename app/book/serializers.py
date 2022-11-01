"""
Serializers for book APIs
"""
from rest_framework import serializers
from core.models import (
    Book,
    Genre,
    Author,
    Language,
    BookShelf,
    Publisher,
    Review
)


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


class BookShelfSerializer(serializers.ModelSerializer):
    """BookShelf Serializer."""

    class Meta:
        model = BookShelf
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']


class PublisherSerializer(serializers.ModelSerializer):
    """Publisher Serializer."""

    class Meta:
        model = Publisher
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']


class BookSerializer(serializers.ModelSerializer):
    """Serializer for books."""
    genres = GenreSerializer(many=True, required=False)
    authors = AuthorSerializer(many=True, required=False)
    languages = LanguageSerializer(many=True, required=False)
    bookshelves = BookShelfSerializer(many=True, required=False)
    publishers = PublisherSerializer(many=True, required=False)

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
            'bookshelves',
            'publishers',
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

    def _get_or_create_bookshelves(self, bookshelves, book):
        """Handle getting or creating bookshelves as needed."""
        for bkshlf in bookshelves:
            bookshelf_obj, created = BookShelf.objects.get_or_create(**bkshlf)
            book.bookshelves.add(bookshelf_obj)

    def _get_or_create_publishers(self, publishers, book):
        """Handle getting or creating publishers as needed."""
        for pblshr in publishers:
            publisher_obj, created = Publisher.objects.get_or_create(**pblshr)
            book.publishers.add(publisher_obj)

    def create(self, validated_data):
        """Create a book."""
        genres = validated_data.pop('genres', [])
        authors = validated_data.pop('authors', [])
        languages = validated_data.pop('languages', [])
        bookshelves = validated_data.pop('bookshelves', [])
        publishers = validated_data.pop('publishers', [])

        book = Book.objects.create(**validated_data)
        self._get_or_create_genres(genres, book)
        self._get_or_create_authors(authors, book)
        self._get_or_create_languages(languages, book)
        self._get_or_create_bookshelves(bookshelves, book)
        self._get_or_create_publishers(publishers, book)

        return book

    def update(self, instance, validated_data):
        """Update book."""
        genres = validated_data.pop('genres', None)
        authors = validated_data.pop('authors', None)
        languages = validated_data.pop('languages', None)
        bookshelves = validated_data.pop('bookshelves', None)
        publishers = validated_data.pop('publishers', None)

        if genres is not None:
            instance.genres.clear()
            self._get_or_create_genres(genres, instance)

        if authors is not None:
            instance.authors.clear()
            self._get_or_create_authors(authors, instance)

        if languages is not None:
            instance.languages.clear()
            self._get_or_create_languages(languages, instance)

        if bookshelves is not None:
            instance.bookshelves.clear()
            self._get_or_create_bookshelves(bookshelves, instance)

        if publishers is not None:
            instance.publishers.clear()
            self._get_or_create_publishers(publishers, instance)

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


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for book reviews."""

    class Meta:
        model = Review
        fields = ['id', 'comment', 'value', 'created_at']
        read_only_fields = ['id']


class ReviewDetailSerializer(serializers.ModelSerializer):
    """Serializer for book reviews."""

    class Meta(ReviewSerializer.Meta):
        fields = ReviewSerializer.Meta.fields+['book']
