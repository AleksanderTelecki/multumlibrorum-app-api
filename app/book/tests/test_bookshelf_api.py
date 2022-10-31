"""
Tests for the genres API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import BookShelf

from book.serializers import BookShelfSerializer

BOOKSHELF_URL = reverse('book:bookshelf-list')


def detail_url(bookshelf_id):
    return reverse('book:bookshelf-detail', args=[bookshelf_id])


class PublicBookshelvesApiTests(TestCase):
    """Test api bookshelves request."""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_genres(self):
        """Test list of bookshelves."""

        BookShelf.objects.create(name='Test 1', description='Test also 1')
        BookShelf.objects.create(name='Test 2', description='Test also 2')

        res = self.client.get(BOOKSHELF_URL)

        bookshelves = BookShelf.objects.all().order_by('-name')
        serializer = BookShelfSerializer(bookshelves, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class PrivateBookshelvesApiTests(TestCase):
    """Test bookshelves requests for admin user"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            'test@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_bookshelves_patch(self):
        """Test bookshelf update."""
        bookshelf = BookShelf.objects.create(
            name='Test 1',
            description='Test also 1'
        )

        payload = {'name': 'Test upd 1', 'description': 'Test also upd 1'}

        url = detail_url(bookshelf.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        bookshelf.refresh_from_db()
        self.assertEqual(bookshelf.name, payload['name'])

    def test_bookshelves_put(self):
        """Test bookshelf update."""
        bookshelf = BookShelf.objects.create(
            name='Test 1',
            description='Test also 1'
        )

        payload = {'name': 'Test upd 1', 'description': 'Test also upd 1'}

        url = detail_url(bookshelf.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        bookshelf.refresh_from_db()
        self.assertEqual(bookshelf.name, payload['name'])

    def test_bookshelves_delete(self):
        """Test deleting a bookshelf"""
        bookshelf = BookShelf.objects.create(
            name='Test 1',
            description='Test also 1'
        )

        url = detail_url(bookshelf.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        bookshelves = BookShelf.objects.all()
        self.assertFalse(bookshelves.exists())
