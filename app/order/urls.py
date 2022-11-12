"""
URL mappings for order app.
"""

from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter
from order import views

router = DefaultRouter()
router.register('cart', views.CartViewSet)

app_name = 'order'

urlpatterns = [
    path('', include(router.urls)),
]
