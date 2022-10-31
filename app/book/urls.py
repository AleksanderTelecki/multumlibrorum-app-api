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
router.register('authors', views.AuthorViewSet)
router.register('languages', views.LanguageViewSet)
router.register('bookshelves', views.BookShelfViewSet)
router.register('publishers', views.PublisherViewSet)

app_name = 'book'

urlpatterns = [
    path('', include(router.urls)),
]
