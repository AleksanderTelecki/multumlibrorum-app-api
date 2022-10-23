"""
Serializers for book APIs
"""
from rest_framework import serializers
from core.models import Book


class BookSerializer(serializers.ModelSerializer):
    """Serializer for books."""

    class Meta:
        model = Book
        fields = ['id', 'title', 'isbn13', 'publicationDate', 'availableQuantity', 'price', 'description', 'createdAt']
        read_only_fields = ['id', 'isbn13']