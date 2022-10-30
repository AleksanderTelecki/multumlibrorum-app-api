"""
URL mappings for book app.
"""

from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter
from book import views

router = DefaultRouter()
router.register('books', views.BookViewSet)
router.register('genres', views.GenreViewSet)

app_name = 'book'

urlpatterns = [
    path('', include(router.urls)),
]
