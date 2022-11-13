"""
Serializers for order APIs
"""
from rest_framework import serializers
from core.models import (
    OrderItem,
    LikedItem
)

from book.serializers import BookSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for book orderitems."""

    class Meta:
        model = OrderItem
        fields = ['id', 'book', 'quantity']
        read_only_fields = ['id']


class OrderItemDetailSerializer(serializers.ModelSerializer):
    """Serializer for book orderitems."""

    book = BookSerializer(many=False, required=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'book', 'quantity']
        read_only_fields = ['id', 'book']


class LikedItemSerializer(serializers.ModelSerializer):
    """Serializer for book likeditems."""

    class Meta:
        model = LikedItem
        fields = ['id', 'book']
        read_only_fields = ['id']


class LikedItemDetailSerializer(serializers.ModelSerializer):
    """Serializer for book likeditems."""

    book = BookSerializer(many=False, required=True)

    class Meta:
        model = LikedItem
        fields = ['id', 'book']
        read_only_fields = ['id', 'book']
