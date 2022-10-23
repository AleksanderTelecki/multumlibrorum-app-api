"""
Serializers for book APIs
"""
from rest_framework import serializers
from core.models import Book


class BookSerializer(serializers.ModelSerializer):
    """Serializer for books."""

    class Meta:
        model = Book
        fields = ['id', 'title', 'price', 'created_at']
        read_only_fields = ['id']


class BookDetailSerializer(BookSerializer):
    """Serializer for book detail view."""

    class Meta(BookSerializer.Meta):
        fields = BookSerializer.Meta.fields + [
            'isbn13',
            'publication_date',
            'available_quantity',
            'description'
        ]
