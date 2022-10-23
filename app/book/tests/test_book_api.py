"""
Tests for book APIs.
"""

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Book
from book.serializers import BookSerializer, BookDetailSerializer


BOOK_URL = reverse('book:book-list')


def detail_url(book_id):
    """Create and return a book URL."""
    return reverse('book:book-detail', args=[book_id])


def create_book(**params):
    """Create and return a sample book."""

    defaults = {
        'title': 'Sample book title',
        'isbn13': '978-3-16-148410-0',
        'publicationDate': date(2022, 5, 7),
        'availableQuantity': 25,
        'price': Decimal('5.50'),
        'description': 'Sample Book description'
    }

    defaults.update(params)

    book = Book.objects.create(**defaults)
    return book


class PublicBookAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_not_required(self):
        """Test auth is not required to call API."""
        res = self.client.get(BOOK_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrive_books(self):
        """Test retrieving a list of books."""
        create_book()
        create_book()

        res = self.client.get(BOOK_URL)

        books = Book.objects.all().order_by('-id')
        serializer = BookSerializer(books, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_book_detail(self):
        """Test get book detail."""
        book = create_book()

        url = detail_url(book.id)
        res = self.client.get(url)

        serializer = BookDetailSerializer(book)

        self.assertEqual(res.data, serializer.data)

    def test_create_book_non_admin(self):
        """Test creating a book."""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )
        self.client.force_authenticate(user)

        payload = {
            'title': 'Sample book title',
            'isbn13': '978-3-16-148410-0',
            'publicationDate': date(2022, 5, 7),
            'availableQuantity': 25,
            'price': Decimal('5.50'),
            'description': 'Sample Book description'
        }

        res = self.client.post(BOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PrivateBookAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            'test@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_create_book(self):
        """Test creating a book."""
        payload = {
            'title': 'Sample book title',
            'isbn13': '978-3-16-148410-0',
            'publicationDate': date(2022, 5, 7),
            'availableQuantity': 25,
            'price': Decimal('5.50'),
            'description': 'Sample Book description'
        }

        res = self.client.post(BOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        book = Book.objects.get(id=res.data['id'])

        for k, v in payload.items():
            self.assertEqual(getattr(book, k), v)

    def test_partial_update(self):
        """Test partial update of a book."""
        original_isbn13 = '978-3-16-148410-2'

        book = create_book(isbn13=original_isbn13)

        payload = {'title': 'New title'}

        url = detail_url(book.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        book.refresh_from_db()
        self.assertEqual(book.title, payload['title'])
        self.assertEqual(book.isbn13, original_isbn13)

    def test_full_update(self):
        """Test full update of a book."""
        book = create_book()

        payload = {
            'title': 'updated book title',
            'isbn13': '978-3-15-148410-0',
            'publicationDate': date(2022, 6, 7),
            'availableQuantity': 40,
            'price': Decimal('5.70'),
            'description': 'SUpdated description'
        }

        url = detail_url(book.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        book.refresh_from_db()

        for k, v in payload.items():
            self.assertEqual(getattr(book, k), v)

    def test_delete_book(self):
        """Test deleting a book successful."""
        book = create_book()

        url = detail_url(book.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=book.id).exists())
