"""
Views for the order APIs.
"""

from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    OrderItem,
    LikedItem
)
from order import serializers


class BaseOrderAttrViewSet(mixins.DestroyModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.ListModelMixin,
                           mixins.CreateModelMixin,
                           viewsets.GenericViewSet):
    """Base ViewSet for order attributes."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return query filtered by id."""
        return self.queryset.filter(user=self.request.user) \
            .order_by('-book__title')


class CartViewSet(BaseOrderAttrViewSet):
    """Manage orderitems in database."""
    serializer_class = serializers.OrderItemSerializer
    queryset = OrderItem.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.OrderItemDetailSerializer

        return self.serializer_class


class LikedCartViewSet(mixins.DestroyModelMixin,
                       mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       viewsets.GenericViewSet):
    """Manage likeditems in database."""
    serializer_class = serializers.LikedItemSerializer
    queryset = LikedItem.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return query filtered by id."""
        return self.queryset.filter(user=self.request.user) \
            .order_by('-book__title')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.LikedItemDetailSerializer

        return self.serializer_class
